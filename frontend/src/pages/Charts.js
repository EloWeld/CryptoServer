import React, { useState, useRef, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import Navbar from '../components/Navbar';
import {
    Listbox, ListboxOption, ListboxOptions, ListboxButton,
    Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption,
} from '@headlessui/react';

import axios from 'axiosConfig';
import { toast } from 'react-toastify';

function Charts({ isAuthenticated, setIsAuthenticated }) {
    const [coins, setCoins] = useState([]);
    const [selectedCoin, setSelectedCoin] = useState(null);

    const [query, setQuery] = useState('');
    const [timezoneOffset, setTimezoneOffset] = useState(0);
    const [loading, setLoading] = useState("...");

    const chartsRef = useRef([]);
    const chartContainerRef = useRef();
    const volumeChartContainerRef = useRef(null);
    const cvdChartContainerRef = useRef(null);
    const oiChartContainerRef = useRef(null);

    const filteredCoins =
        query === ''
            ? coins
            : coins.filter((coin) =>
                coin.name.toLowerCase().includes(query.toLowerCase())
            );


    useEffect(() => {
        async function fetchUserData() {
            try {
                const userResponse = await axios.get('/api/user');
                setTimezoneOffset(userResponse.data.timezone_offset);
            } catch (error) {
                toast.error(`'Error fetching user data: ${error}`)
            }
        }
        fetchUserData();

        axios.get('/api/coins')
            .then(response => {
                setCoins(response.data);
                if (response.data.length > 0) {
                    if (response.data.length > 0) {
                        if (localStorage.getItem('selectedCoin')) {
                            setSelectedCoin(JSON.parse(localStorage.getItem('selectedCoin')));
                        } else {
                            setSelectedCoin(response.data[0]);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching coins:', error);
                toast.error(`Error fetching coins`)
            });
    }, []);

    const handleCoinChange = (coin) => {
        setSelectedCoin(coin);
        console.log(coin)
        localStorage.setItem('selectedCoin', JSON.stringify(coin));
    };


    // Функция для форматирования времени в UTC
    function formatDateTime(time) {
        const date = new Date((time) * 1000);
        return date.toISOString().slice(11, 16).replace('T', ' ');
    }
    // Функция для форматирования времени в UTC
    function adjustTime(time) {
        return (time * 60 - (180 * 60000) + (new Date()).getTimezoneOffset() / -60 * 3600000 + timezoneOffset * 3600);
    }

    const createMyChart = (ref) => {
        return createChart(ref, {
            barSpacing: 10,
            layout: {
                background: { color: '#222' },
                textColor: '#DDD',
            },
            grid: {
                vertLines: { color: '#444' },
                horzLines: { color: '#444' },
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: true,
                tickMarkFormatter: formatDateTime // Форматирование времени в UTC
            },
            crossHair: {
                mode: 1, // Режим перекрестия
            },
            rightPriceScale: {
                borderColor: '#555',
            },
            watermark: {
                visible: true,
                fontSize: 24,
                horzAlign: 'left',
                vertAlign: 'bottom',
                color: 'rgba(255, 255, 255, 0.4)',
                text: 'DaVinchi',
            },
            width: ref.clientWidth,
            height: ref.clientHeight,
        });

    }

    // Функция для синхронизации временной шкалы между графиками
    function synchronizeTimescale(charts) {
        const [mainChart, ...otherCharts] = charts;
        const mainTimeScale = mainChart.timeScale();

        function applyChanges() {
            const logicalRange = mainTimeScale.getVisibleLogicalRange();
            otherCharts.forEach(chart => {
                chart.timeScale().setVisibleLogicalRange(logicalRange);
            });

            // Получаем текущее положение прокрутки основного графика
            const scrollPosition = mainTimeScale.scrollPosition();

            // Устанавливаем такое же положение прокрутки для всех остальных графиков
            otherCharts.forEach(chart => {
                chart.timeScale().scrollToPosition(scrollPosition, false);
            });
        }

        mainTimeScale.subscribeVisibleLogicalRangeChange(applyChanges);
        otherCharts.forEach(chart => {
            chart.timeScale().subscribeVisibleLogicalRangeChange(applyChanges);
        });

        // Центрирование графиков по правой стороне при инициализации
        charts.forEach(chart => {
            chart.timeScale().fitContent();
        });

        // Применяем начальные изменения для синхронизации всех графиков
        applyChanges();
    }
    useEffect(() => {
        if (selectedCoin) {
            setLoading("Загрузка графика...");  // Показываем спиннер
            axios.get(`/api/coins/${selectedCoin.id}/chart`)
                .then(response => {
                    setLoading("Рисуем график...");
                    if (response.data.message === "NO_PROCESS") {
                        toast.info("No process for this coin")
                    } else if (response.data.message === "NO_PRICE_HISTORY") {
                        toast.info("No saved price history for this coin")
                    } else if (response.data.message === "NO_COIN_PRICE_HISTORY") {
                        toast.info("No saved price history for this coin")
                    } else {

                        console.log(response.data);
                        chartsRef.current.forEach(chart => chart.remove());
                        chartsRef.current = [];
                        const priceChart = createMyChart(chartContainerRef.current);
                        const oiChart = createMyChart(oiChartContainerRef.current);
                        const cvdChart = createMyChart(cvdChartContainerRef.current);
                        const volumesChart = createMyChart(volumeChartContainerRef.current);

                        chartsRef.current = [priceChart, oiChart, cvdChart, volumesChart];

                        try {
                            synchronizeTimescale([priceChart, volumesChart, cvdChart, oiChart]);
                        } catch (e) {
                            console.error(e);
                        }



                        // ———————————————— PRICE ———————————————— //
                        const firstPrice = response.data['price'][0][1];
                        const priceData = response.data['price'].map(item => ({
                            time: adjustTime(item[0]),
                            value: ((item[1] - firstPrice) / firstPrice) * 100 // Процентное изменение
                        }));

                        const lineSeries = priceChart.addAreaSeries({
                            lineColor: '#2962FF',
                            topColor: 'rgba(41, 98, 255, 0.58)',
                            bottomColor: 'rgba(41, 98, 255, 0.05)',
                            title: 'Price'
                        }); // Blue
                        lineSeries.setData(priceData);

                        // ———————————————— OI ———————————————— //
                        const firstOi = response.data['oi'][0][1];
                        const oiData = response.data['oi'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: ((item[1] - firstOi) / firstOi) * 100 // Процентное изменение
                        }));

                        const oiSeries = oiChart.addAreaSeries({
                            lineColor: '#FF5733',
                            topColor: 'rgba(255, 87, 51, 0.58)',
                            bottomColor: 'rgba(255, 87, 51, 0.05)',
                            title: 'OI'
                        }); // Orange
                        oiSeries.setData(oiData);
                        // ———————————————— CVD ———————————————— //
                        const cvdData = response.data['cvd'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: item[1]
                        }));

                        // Нормализация значений CVD и масштабирование в диапазоне от -100 до 100
                        const maxCvd = Math.max(...cvdData.map(item => item.value));
                        const minCvd = Math.min(...cvdData.map(item => item.value));

                        const normalizedCvdData = cvdData.map(item => {
                            const normalizedValue = ((item.value - minCvd) / (maxCvd - minCvd)) * 200 - 100; // Нормализация в диапазоне -100 до 100
                            return {
                                time: item.time,
                                value: normalizedValue * -1
                            };
                        });

                        const cvdSeries = cvdChart.addAreaSeries({
                            lineColor: '#33FF57',
                            topColor: 'rgba(51, 255, 87, 0.58)',
                            bottomColor: 'rgba(51, 255, 87, 0.05)',
                            title: 'CVD'
                        }); // Green
                        cvdSeries.setData(normalizedCvdData);

                        // ———————————————— VOLUMES ———————————————— //
                        const volumesData = response.data['volumes'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: item[1]
                        }));

                        // Нормализация значений объемов и масштабирование в диапазоне от -100 до 100
                        const maxVolume = Math.max(...volumesData.map(item => item.value));
                        const minVolume = Math.min(...volumesData.map(item => item.value));

                        const normalizedVolumesData = volumesData.map(item => {
                            const normalizedValue = ((item.value - minVolume) / (maxVolume - minVolume)) * 200 - 100; // Нормализация в диапазоне -100 до 100
                            return {
                                time: item.time,
                                value: normalizedValue * -1
                            };
                        });

                        const volumeSeries = volumesChart.addAreaSeries({
                            lineColor: '#FF33A6',
                            topColor: 'rgba(255, 51, 166, 0.58)',
                            bottomColor: 'rgba(255, 51, 166, 0.05)',
                            title: 'Volume'
                        }); // Pink
                        volumeSeries.setData(normalizedVolumesData);

                        // Добавляем легенду для выбранной монеты
                        const legendPrice = document.createElement('div');
                        legendPrice.setAttribute('class', "top-3 left-3 absolute p-2 rounded-sm z-10")
                        legendPrice.style.backgroundColor = '#666666C1';
                        chartContainerRef.current.appendChild(legendPrice);

                        const legendOI = document.createElement('div');
                        legendOI.setAttribute('class', "top-3 left-3 absolute p-2 rounded-sm z-10")
                        legendOI.style.backgroundColor = '#666666C1';
                        oiChartContainerRef.current.appendChild(legendOI);

                        const legendCVD = document.createElement('div');
                        legendCVD.setAttribute('class', "top-3 left-3 absolute p-2 rounded-sm z-10")
                        legendCVD.style.backgroundColor = '#666666C1';
                        cvdChartContainerRef.current.appendChild(legendCVD);

                        const legendVol = document.createElement('div');
                        legendVol.setAttribute('class', "top-3 left-3 absolute p-2 rounded-sm z-10")
                        legendVol.style.backgroundColor = '#666666C1';
                        volumeChartContainerRef.current.appendChild(legendVol);

                        const priceRow = document.createElement('div');
                        priceRow.innerHTML = 'Price:';
                        priceRow.style.color = '#2962FF'; // Blue
                        legendPrice.appendChild(priceRow);

                        const oiRow = document.createElement('div');
                        oiRow.innerHTML = 'OI:';
                        oiRow.style.color = '#FF5733'; // Orange
                        legendOI.appendChild(oiRow);

                        const cvdRow = document.createElement('div');
                        cvdRow.innerHTML = 'CVD:';
                        cvdRow.style.color = '#33FF57'; // Green
                        legendCVD.appendChild(cvdRow);

                        const volumeRow = document.createElement('div');
                        volumeRow.innerHTML = 'Volume:';
                        volumeRow.style.color = '#FF33A6'; // Pink
                        legendVol.appendChild(volumeRow);

                        priceChart.subscribeCrosshairMove(param => {
                            if (param.time) {
                                const priceData = param.seriesData.get(lineSeries);
                                const priceValue = priceData ? (priceData.value !== undefined ? priceData.value : priceData.close) : 'N/A';

                                priceRow.innerHTML = `Price: <strong>${typeof priceValue === 'number' ? priceValue.toFixed(2) : priceValue}</strong>`;
                            }
                        });

                        priceChart.timeScale().fitContent();


                        oiChart.subscribeCrosshairMove(param => {
                            if (param.time) {
                                const oiData = param.seriesData.get(oiSeries);
                                const oiValue = oiData ? (oiData.value !== undefined ? oiData.value : oiData.close) : 'N/A';
                                oiRow.innerHTML = `OI: <strong>${typeof oiValue === 'number' ? oiValue.toFixed(2) : oiValue}</strong>`;
                            }
                        });

                        oiChart.timeScale().fitContent();


                        cvdChart.subscribeCrosshairMove(param => {
                            if (param.time) {
                                const cvdData = param.seriesData.get(cvdSeries);
                                const cvdValue = cvdData ? (cvdData.value !== undefined ? cvdData.value : cvdData.close) : 'N/A';
                                cvdRow.innerHTML = `CVD: <strong>${typeof cvdValue === 'number' ? cvdValue.toFixed(2) : cvdValue}</strong>`;
                            }
                        });

                        cvdChart.timeScale().fitContent();


                        volumesChart.subscribeCrosshairMove(param => {
                            if (param.time) {
                                const volumeData = param.seriesData.get(volumeSeries);
                                const volumeValue = volumeData ? (volumeData.value !== undefined ? volumeData.value : volumeData.close) : 'N/A';
                                volumeRow.innerHTML = `Volume: <strong>${typeof volumeValue === 'number' ? volumeValue.toFixed(2) : volumeValue}</strong>`;
                            }
                        });

                        volumesChart.timeScale().fitContent();
                        setLoading(null);
                    }
                })
                ;
        }
    }, [selectedCoin, timezoneOffset]);

    return (
        <div>
            <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
            <div className="container mx-auto p-4">
                <h1 className="text-2xl font-bold mb-4">Charts</h1>
                <div className="flex flex-row gap-5 items-start justify-start">
                    <div className="w-64">

                        {/* <Listbox value={selectedCoin} onChange={handleCoinChange}>
                            {({ open }) => (
                                <>
                                    <ListboxButton className="block w-40 p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm relative text-left">
                                        {selectedCoin ? selectedCoin.name : 'Select a coin'}
                                        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                                            <svg className={`w-5 h-5 text-gray-400 transform ${open ? 'rotate-180' : 'rotate-0'}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.87l3.71-3.64a.75.75 0 011.08 1.04l-4.25 4.17a.75.75 0 01-1.06 0L5.23 8.27a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                                            </svg>
                                        </span>
                                    </ListboxButton>
                                    <ListboxOptions className="z-20 absolute mt-1 max-h-60 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                        {coins.map((coin) => (
                                            <ListboxOption key={coin.id} value={coin} className="cursor-pointer select-none relative py-2 pl-3 pr-9">
                                                {coin.name}
                                            </ListboxOption>
                                        ))}
                                    </ListboxOptions>
                                </>
                            )}
                        </Listbox> */}
                        <Combobox value={selectedCoin} onChange={handleCoinChange}>
                            <div className="relative mt-1">
                                <div className="relative w-full text-left bg-white border border-gray-300 rounded-md shadow-sm cursor-default focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm overflow-hidden">
                                    <ComboboxInput
                                        className="w-full border-none focus:ring-0 py-2 pl-3 pr-10 text-sm leading-5 text-gray-900"
                                        displayValue={(coin) => coin?.name || ''}
                                        onChange={(event) => setQuery(event.target.value)}
                                    />
                                    <ComboboxButton className="absolute inset-y-0 right-0 flex items-center pr-2">
                                        <svg className="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                            <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.87l3.71-3.64a.75.75 0 011.08 1.04l-4.25 4.17a.75.75 0 01-1.06 0L5.23 8.27a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                                        </svg>
                                    </ComboboxButton>
                                </div>
                                <ComboboxOptions className="absolute z-20 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                                    {filteredCoins.map((coin) => (
                                        <ComboboxOption
                                            key={coin.id}
                                            value={coin}
                                            className={({ active }) =>
                                                `cursor-pointer select-none relative py-2 pl-3 pr-9 ${active ? 'text-white bg-indigo-600' : 'text-gray-900'
                                                }`
                                            }
                                        >
                                            {({ selected, active }) => (
                                                <>
                                                    <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                                                        {coin.name}
                                                    </span>

                                                </>
                                            )}
                                        </ComboboxOption>
                                    ))}
                                </ComboboxOptions>
                            </div>
                        </Combobox>
                    </div>
                </div>

                <div ref={chartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '500px', }}>
                    {loading &&
                        <div className="flex justify-center items-center h-full">
                            <div type="button" className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 transition ease-in-out duration-150">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                {loading}
                            </div>
                        </div>}
                </div>
                <div ref={oiChartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '200px', }}>
                    {loading &&
                        <div className="flex justify-center items-center h-full">
                            <div type="button" className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 transition ease-in-out duration-150">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                {loading}
                            </div>
                        </div>}
                </div>
                <div ref={cvdChartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '200px', }}>
                    {loading &&
                        <div className="flex justify-center items-center h-full">
                            <div type="button" className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 transition ease-in-out duration-150">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                {loading}
                            </div>
                        </div>}
                </div>
                <div ref={volumeChartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '200px', }}>
                    {loading &&
                        <div className="flex justify-center items-center h-full">
                            <div type="button" className="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 transition ease-in-out duration-150">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                {loading}
                            </div>
                        </div>}
                </div>
            </div>
        </div>
    );
}

export default Charts;