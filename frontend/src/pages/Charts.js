import React, { useState, useRef, useEffect } from 'react';
import { createChart } from 'lightweight-charts';
import Navbar from '../components/Navbar';
import { Listbox, ListboxOption, ListboxOptions, ListboxButton } from '@headlessui/react';

import axios from 'axiosConfig';
import { toast } from 'react-toastify';

function Charts({ isAuthenticated, setIsAuthenticated }) {
    const [coins, setCoins] = useState([]);
    const [selectedCoin, setSelectedCoin] = useState(null);
    const chartContainerRef = useRef();
    const chartRef = useRef();

    useEffect(() => {
        axios.get('/api/coins')
            .then(response => {
                setCoins(response.data);
                if (response.data.length > 0) {
                    setSelectedCoin(response.data[0]);
                }
            })
            .catch(error => {
                console.error('Error fetching coins:', error);
            });
    }, []);

    useEffect(() => {
        if (selectedCoin) {
            axios.get(`/api/coins/${selectedCoin.id}/chart`)
                .then(response => {
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
                            },
                            width: chartContainerRef.current.clientWidth,
                            height: chartContainerRef.current.clientHeight,
                        });

                        chartRef.current = chart;

                        const firstPrice = response.data['price'][0][1];

                        const lineData = response.data['price'].map(item => ({
                            time: item[0] * 60, // Используйте Unix timestamp в секундах
                            value: ((item[1] - firstPrice) / firstPrice) * 100 // Процентное изменение
                        }));

                        const lineSeries = chart.addLineSeries({ color: '#2962FF', }); // Purple
                        lineSeries.setData(lineData);

                        const firstOi = response.data['oi'][0][1];
                        const oiData = response.data['oi'].map(item => ({
                            time: item[0] * 60, // Используйте Unix timestamp в секундах
                            value: ((item[1] - firstOi) / firstOi) * 100 // Процентное изменение
                        }));
                        const oiSeries = chart.addLineSeries({ color: '#FF5733', }); // Orange
                        oiSeries.setData(oiData);

                        const firstCvd = response.data['cvd'][0][1];
                        const cvdData = response.data['cvd'].map(item => ({
                            time: item[0] * 60, // Используйте Unix timestamp в секундах
                            value: ((item[1] - firstCvd) / firstCvd) * 100 // Процентное изменение
                        }));
                        const cvdSeries = chart.addLineSeries({ color: '#33FF57', }); // Green
                        cvdSeries.setData(cvdData);

                        const firstVolume = response.data['volumes'][0][1];
                        const volumesData = response.data['volumes'].map(item => ({
                            time: item[0] * 60, // Используйте Unix timestamp в секундах
                            value: ((item[1] - firstVolume) / firstVolume) * 100 // Процентное изменение
                        }));
                        const volumeSeries = chart.addLineSeries({ color: '#FF33A6', }); // Pink
                        volumeSeries.setData(volumesData);



                        // Добавляем легенду для выбранной монеты
                        const legend = document.createElement('div');
                        legend.style.position = 'absolute';
                        legend.style.top = '10px';
                        legend.style.left = '10px';
                        legend.style.color = 'white';
                        legend.setAttribute("class", "rounded bg-indigo-600");
                        legend.style.padding = '5px';
                        legend.style.zIndex = '5';
                        chartContainerRef.current.appendChild(legend);

                        const firstRow = document.createElement('div');
                        firstRow.innerHTML = selectedCoin.name;
                        firstRow.style.color = 'white';
                        legend.appendChild(firstRow);

                        chart.subscribeCrosshairMove(param => {
                            let priceFormatted = '';
                            if (param.time) {
                                const data = param.seriesData.get(lineSeries);
                                if (data) {
                                    const price = data.value !== undefined ? data.value : data.close;
                                    priceFormatted = price.toFixed(2);
                                }
                            }
                            firstRow.innerHTML = `${selectedCoin.name} <strong>${priceFormatted}</strong>`;
                        });

                        chart.timeScale().fitContent();
                    }
                })
                .catch(error => {
                    console.error('Error fetching coin chart data:', error);
                });
        }
    }, [selectedCoin]);

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
                <div ref={chartContainerRef} className='rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-500 my-4' style={{ position: 'relative', width: '100%', height: '500px', }} />
            </div>
        </div>
    );
}

export default Charts;