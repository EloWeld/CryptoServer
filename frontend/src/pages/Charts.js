import React, { useState, useRef, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import Navbar from '../components/Navbar';
import { Listbox, ListboxOption, ListboxOptions, ListboxButton } from '@headlessui/react';

import axios from 'axiosConfig';
import { toast } from 'react-toastify';

function Charts({ isAuthenticated, setIsAuthenticated }) {
    const [coins, setCoins] = useState([]);
    const [selectedCoin, setSelectedCoin] = useState(null);
    const [timezoneOffset, setTimezoneOffset] = useState(0);
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const [loading, setLoading] = useState("...");


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
                    setSelectedCoin(response.data[0]);
                }
            })
            .catch(error => {
                console.error('Error fetching coins:', error);
                toast.error(`Error fetching coins`)
            });
    }, []);


    // Функция для форматирования времени в UTC
    function formatDateTime(time) {
        const date = new Date((time) * 1000);
        return date.toISOString().slice(11, 16).replace('T', ' ');
    }
    // Функция для форматирования времени в UTC
    function adjustTime(time) {
        return (time * 60 + timezoneOffset * 3600);
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
                        if (chartRef.current) {
                            chartRef.current.remove();
                        }
                        const chart = createChart(chartContainerRef.current, {
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
                            width: chartContainerRef.current.clientWidth,
                            height: chartContainerRef.current.clientHeight,
                        });

                        chartRef.current = chart;


                        // ———————————————— PRICE ———————————————— //
                        const priceData = response.data['price'].map(item => ({
                            time: adjustTime(item[0]),
                            value: item[1]
                        }));

                        // Вычисление среднего значения и стандартного отклонения для цены
                        const priceValues = priceData.map(item => item.value);
                        const meanPrice = priceValues.reduce((acc, val) => acc + val, 0) / priceValues.length;
                        const stdDevPrice = Math.sqrt(priceValues.map(val => (val - meanPrice) ** 2).reduce((acc, val) => acc + val, 0) / priceValues.length);

                        // Нормализация значений цены и масштабирование в диапазоне от -100 до 100
                        const normalizedPriceData = priceData.map(item => {
                            const normalizedValue = (item.value - meanPrice) / stdDevPrice;
                            return {
                                time: item.time,
                                value: Math.max(Math.min(normalizedValue * 100, 100), -100) // Ограничение значений в диапазоне -100 до 100
                            };
                        });

                        const lineSeries = chart.addLineSeries({ color: '#2962FF' }); // Blue
                        lineSeries.setData(normalizedPriceData);
                        // ———————————————— OI ———————————————— //
                        const oiData = response.data['oi'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: item[1]
                        }));

                        // Вычисление среднего значения и стандартного отклонения для OI
                        const oiValues = oiData.map(item => item.value);
                        const meanOi = oiValues.reduce((acc, val) => acc + val, 0) / oiValues.length;
                        const stdDevOi = Math.sqrt(oiValues.map(val => (val - meanOi) ** 2).reduce((acc, val) => acc + val, 0) / oiValues.length);

                        // Нормализация значений OI и масштабирование в диапазоне от -100 до 100
                        const normalizedOiData = oiData.map(item => {
                            const normalizedValue = (item.value - meanOi) / stdDevOi;
                            return {
                                time: item.time,
                                value: Math.max(Math.min(normalizedValue * 100, 100), -100) // Ограничение значений в диапазоне -100 до 100
                            };
                        });

                        const oiSeries = chart.addLineSeries({ color: '#FF5733', }); // Orange
                        oiSeries.setData(normalizedOiData);
                        // ———————————————— CVD ———————————————— //
                        const cvdData = response.data['cvd'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: item[1]
                        }));

                        // Вычисление среднего значения и стандартного отклонения
                        const cvdValues = cvdData.map(item => item.value);
                        const meanCvd = cvdValues.reduce((acc, val) => acc + val, 0) / cvdValues.length;
                        const stdDevCvd = Math.sqrt(cvdValues.map(val => (val - meanCvd) ** 2).reduce((acc, val) => acc + val, 0) / cvdValues.length);

                        // Нормализация значений CVD и масштабирование в диапазоне от -100 до 100
                        const normalizedCvdData = cvdData.map(item => {
                            const normalizedValue = (item.value - meanCvd) / stdDevCvd;
                            return {
                                time: item.time,
                                value: Math.max(Math.min(normalizedValue * 100, 100), -100) // Ограничение значений в диапазоне -100 до 100
                            };
                        });

                        const cvdSeries = chart.addLineSeries({ color: '#33FF57' }); // Green
                        cvdSeries.setData(normalizedCvdData);

                        // ———————————————— VOLUMES ———————————————— //
                        const volumesData = response.data['volumes'].map(item => ({
                            time: adjustTime(item[0]), // Используйте Unix timestamp в секундах
                            value: item[1]
                        }));

                        // Вычисление среднего значения и стандартного отклонения для объемов
                        const volumeValues = volumesData.map(item => item.value);
                        const meanVolume = volumeValues.reduce((acc, val) => acc + val, 0) / volumeValues.length;
                        const stdDevVolume = Math.sqrt(volumeValues.map(val => (val - meanVolume) ** 2).reduce((acc, val) => acc + val, 0) / volumeValues.length);

                        // Нормализация значений объемов и масштабирование в диапазоне от -100 до 100
                        const normalizedVolumesData = volumesData.map(item => {
                            const normalizedValue = (item.value - meanVolume) / stdDevVolume;
                            return {
                                time: item.time,
                                value: Math.max(Math.min(normalizedValue * 100, 100), -100) // Ограничение значений в диапазоне -100 до 100
                            };
                        });

                        const volumeSeries = chart.addLineSeries({ color: '#FF33A6' }); // Pink
                        volumeSeries.setData(normalizedVolumesData);

                        // Добавляем легенду для выбранной монеты
                        const legend = document.createElement('div');
                        legend.style.position = 'absolute';
                        legend.style.top = '10px';
                        legend.style.left = '10px';
                        legend.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
                        legend.style.padding = '10px';
                        legend.style.borderRadius = '5px';
                        legend.style.zIndex = '1';
                        chartContainerRef.current.appendChild(legend);

                        const priceRow = document.createElement('div');
                        priceRow.innerHTML = 'Price:';
                        priceRow.style.color = '#2962FF'; // Blue
                        legend.appendChild(priceRow);

                        const oiRow = document.createElement('div');
                        oiRow.innerHTML = 'OI:';
                        oiRow.style.color = '#FF5733'; // Orange
                        legend.appendChild(oiRow);

                        const cvdRow = document.createElement('div');
                        cvdRow.innerHTML = 'CVD:';
                        cvdRow.style.color = '#33FF57'; // Green
                        legend.appendChild(cvdRow);

                        const volumeRow = document.createElement('div');
                        volumeRow.innerHTML = 'Volume:';
                        volumeRow.style.color = '#FF33A6'; // Pink
                        legend.appendChild(volumeRow);

                        chart.subscribeCrosshairMove(param => {
                            if (param.time) {
                                const priceData = param.seriesData.get(lineSeries);
                                const oiData = param.seriesData.get(oiSeries);
                                const cvdData = param.seriesData.get(cvdSeries);
                                const volumeData = param.seriesData.get(volumeSeries);

                                const priceValue = priceData ? (priceData.value !== undefined ? priceData.value : priceData.close) : 'N/A';
                                const oiValue = oiData ? (oiData.value !== undefined ? oiData.value : oiData.close) : 'N/A';
                                const cvdValue = cvdData ? (cvdData.value !== undefined ? cvdData.value : cvdData.close) : 'N/A';
                                const volumeValue = volumeData ? (volumeData.value !== undefined ? volumeData.value : volumeData.close) : 'N/A';

                                priceRow.innerHTML = `Price: <strong>${typeof priceValue === 'number' ? priceValue.toFixed(2) : priceValue}</strong>`;
                                oiRow.innerHTML = `OI: <strong>${typeof oiValue === 'number' ? oiValue.toFixed(2) : oiValue}</strong>`;
                                cvdRow.innerHTML = `CVD: <strong>${typeof cvdValue === 'number' ? cvdValue.toFixed(2) : cvdValue}</strong>`;
                                volumeRow.innerHTML = `Volume: <strong>${typeof volumeValue === 'number' ? volumeValue.toFixed(2) : volumeValue}</strong>`;
                            }
                        });

                        chart.timeScale().fitContent();
                        setLoading(null);
                    }
                })
                .catch(error => {
                    console.error('Error fetching coin chart data:', error);
                });
        }
    }, [selectedCoin, timezoneOffset]);

    return (
        <div>
            <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
            <div className="container mx-auto p-4">
                <h1 className="text-2xl font-bold mb-4">Charts</h1>
                <div className="flex flex-row gap-5 items-start justify-start">
                    <div className="w-64">

                        <Listbox value={selectedCoin} onChange={setSelectedCoin}>
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
                                    <ListboxOptions className="z-10 absolute mt-1 max-h-60 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                        {coins.map((coin) => (
                                            <ListboxOption key={coin.id} value={coin} className="cursor-pointer select-none relative py-2 pl-3 pr-9">
                                                {coin.name}
                                            </ListboxOption>
                                        ))}
                                    </ListboxOptions>
                                </>
                            )}
                        </Listbox>
                    </div>
                </div>

                <div ref={chartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '500px', }}>
                    {loading &&
                        <div className="flex justify-center items-center h-full">
                            <div type="button" class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 transition ease-in-out duration-150">
                                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                {loading}
                            </div></div>}
                </div>
            </div>
        </div>
    );
}

export default Charts;