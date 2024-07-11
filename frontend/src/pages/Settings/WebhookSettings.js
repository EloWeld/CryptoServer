import { CustomNumberInput, CustomFloatInput } from 'components/CustomNumberInput';
import React from 'react';

const WebhookSettings = ({ settings, handleChange, tabs, setTabs }) => {
    return (
        <div className="border-2 border-gray-300 shadow-lg rounded p-4">
            <h1 className="text-xl font-bold mb-2 text-center">Настройки вебхуков процесса</h1>
            <ul className="text-sm font-medium text-center text-gray-500 rounded-lg shadow flex dark:divide-gray-700 dark:text-gray-400 mb-4">
                <li className="w-full focus-within:z-10">
                    <a href="#" className={"inline-block w-full p-4 border-r-1 rounded-l-lg border-gray-200 focus:ring-blue-300 focus:ring-4 focus:outline-none " + (tabs.webhook === 'default' ? "text-gray-900 bg-gray-100 hover:bg-gray-100" : "bg-white hover:bg-gray-50")} aria-current="page" onClick={() => setTabs({ ...tabs, webhook: 'default' })}>Обычный</a>
                </li>
                <li className="w-full focus-within:z-10">
                    <a href="#" className={"inline-block w-full p-4 border-r-0 rounded-r-lg border-gray-200 focus:ring-blue-300 focus:ring-4 focus:outline-none " + (tabs.webhook === 'reverse' ? "text-gray-900 bg-gray-100 hover:bg-gray-100" : "bg-white hover:bg-gray-50")} aria-current="page" onClick={() => setTabs({ ...tabs, webhook: 'reverse' })}>Разворотный</a>
                </li>
            </ul>

            <div id="default-tab-content">
                <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">* В отправляемых данных текст {"{{ticker}}"} будет заменён на текущую валютную пару</p>
                <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">* В отправляемых данных текст {"{{volume_usd}}"} будет заменён на значение Объёма USD</p>
                <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">* В разворотных настройках флажки включения позиций отвечают за возможность разворота этой позиции</p>
                <div className={tabs.webhook === 'default' ? "p-4 rounded-lg bg-gray-50 dark:bg-gray-800 flex gap-3" : "hidden"} id="profile" role="tabpanel" aria-labelledby="profile-tab">
                    <WebhookTypeSettings settings={settings} handleChange={handleChange} type="rapid" title="Быстрый рост" />
                    <WebhookTypeSettings settings={settings} handleChange={handleChange} type="smooth" title="Плавный рост" />
                </div>
                <div className={tabs.webhook === 'reverse' ? "p-4 rounded-lg bg-gray-50 dark:bg-gray-800 flex gap-3" : "hidden"} id="dashboard" role="tabpanel" aria-labelledby="dashboard-tab">
                    <WebhookTypeSettings settings={settings} handleChange={handleChange} type="rapid" title="Быстрый рост" reverse />
                    <WebhookTypeSettings settings={settings} handleChange={handleChange} type="smooth" title="Плавный рост" reverse />
                </div>
            </div>
            {tabs.webhook === 'default' && (<div>
                <label className="block text-sm font-medium text-gray-700">Объём USD</label>
                <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">В отправляемых данных текст {"{{volume_usd}}"} будет заменён на это значение</p>
                <CustomFloatInput
                    name="default_vol_usd"
                    value={settings.default_vol_usd}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
            </div>)}
            {tabs.webhook === 'reverse' && (
                <div className="flex flex-col gap-4" style={{}}>
                    <div>
                        <label className="whitespace-nowrap block text-sm font-medium text-gray-700">Объём USD при развороте</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">В отправляемых данных текст {"{{volume_usd}}"} будет заменён на это значение</p>
                        <CustomFloatInput
                            name="reverse_vol_usd"
                            value={settings.reverse_vol_usd}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-xs border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                    <div>
                        <label className="whitespace-nowrap block text-sm font-medium text-gray-700">Отступ последнего ордера, %</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">Отступ последнего ордера в сетке заявок в процентах от исходной цены</p>
                        <CustomFloatInput
                            name="reverse_last_order_dist"
                            value={settings.reverse_last_order_dist}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-xs border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                    <div>
                        <label className="whitespace-nowrap block text-sm font-medium text-gray-700">Количество ордеров</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">Количество ордеров в сетке заявок</p>
                        <CustomNumberInput
                            name="reverse_full_orders_count"
                            value={settings.reverse_full_orders_count}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-xs border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                    <div>
                        <label className="whitespace-nowrap block text-sm font-medium text-gray-700">Количество ордеров для разворота позиции</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">Количество ордеров, "сдавших свои позиции" для разворота позиции</p>
                        <CustomNumberInput
                            name="reverse_orders_count"
                            value={settings.reverse_orders_count}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-xs border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                    <div>
                        <label className="whitespace-nowrap block text-sm max-w-xs font-medium text-gray-700">Множитель</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1"><i>Пока что не работает</i>Регулирует распределение объёма в сетке. Например, Factor = 2, то каждая последующая заявка в 2 раза больше предыдущей.</p>
                        <CustomFloatInput
                            name="reverse_multiplier"
                            value={settings.reverse_multiplier}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-xs border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                    <div>
                        <label className="whitespace-nowrap block text-sm max-w-lg font-medium text-gray-700">Плотность сетки</label>
                        <p className="block text-xs font-light text-gray-700 pt-0.5 pb-1">Если выбрана “Плотность” равная 1, то заявки будут распределены в сетке равномерно, если больше 1, то заявки будут сконцентрированы ближе к концу сетки, если меньше 1, то ближе к началу.</p>
                        <CustomFloatInput
                            name="reverse_density"
                            value={settings.reverse_density}
                            onChange={handleChange}
                            className="mt-1 block w-full max-w-lg border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

const WebhookTypeSettings = ({ settings, handleChange, type, title, reverse = false }) => {
    let prefix = type;
    if (reverse) {
        prefix = "reverse_".concat(prefix);
    }
    console.log(`${prefix}_pump_webhook`);
    return (
        <div className="w-1/2">

            <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">{title}</h2>
            <div>
                <label className="block text-sm font-medium text-gray-700">{reverse ? 'Reverse ' : ''}Pump Webhook</label>
                <input
                    type="text"
                    name={`${prefix}_pump_webhook`}
                    value={settings[`${prefix}_pump_webhook`]}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">{reverse ? 'Reverse ' : ''}Pump Data</label>
                <textarea
                    rows="4"
                    name={`${prefix}_pump_data`}
                    value={settings[`${prefix}_pump_data`]}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
            </div>
            <div className="flex items-center mb-2">
                <input
                    type="checkbox"
                    name={`${prefix}_enable_pump`}
                    checked={settings[`${prefix}_enable_pump`]}
                    onChange={handleChange}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor={`${prefix}_enable_pump`} className="ml-2 text-sm font-medium text-gray-900">
                    Enable {reverse ? 'Reverse ' : ''}Pump
                </label>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">{reverse ? 'Reverse ' : ''}Dump Webhook</label>
                <input
                    type="text"
                    name={`${prefix}_dump_webhook`}
                    value={settings[`${prefix}_dump_webhook`]}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-700">{reverse ? 'Reverse ' : ''}Dump Data</label>
                <textarea
                    rows="4"
                    name={`${prefix}_dump_data`}
                    value={settings[`${prefix}_dump_data`]}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
            </div>
            <div className="flex items-center mb-2">
                <input
                    type="checkbox"
                    name={`${prefix}_enable_dump`}
                    checked={settings[`${prefix}_enable_dump`]}
                    onChange={handleChange}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor={`${prefix}_enable_dump`} className="ml-2 text-sm font-medium text-gray-900">
                    Enable {reverse ? 'Reverse ' : ''}Dump
                </label>
            </div>

        </div>
    );
};

export default WebhookSettings;