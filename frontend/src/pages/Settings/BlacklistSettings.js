import { useState } from 'react';
import { Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption } from '@headlessui/react';

const BlacklistSettings = ({ settings, setSettings, blacklistOptions }) => {
    const [selectedBlacklistItem, setSelectedBlacklistItem] = useState('');

    const handleSelectBlackList = (item) => {
        if (!settings.coins_blacklist.includes(item)) {
            setSettings({ ...settings, coins_blacklist: [...settings.coins_blacklist, item] });
        }
        setSelectedBlacklistItem('');
    };

    const handleRemoveFromBlackList = (item) => {
        setSettings({ ...settings, coins_blacklist: settings.coins_blacklist.filter(x => x !== item) });
    };

    const blacklistOptionsFiltered =
        selectedBlacklistItem === ''
            ? blacklistOptions
            : blacklistOptions.filter((coin) =>
                coin.toLowerCase().includes(selectedBlacklistItem.toLowerCase())
            );

    return (
        <div className="border-2 border-gray-300 shadow-lg rounded p-4">
            <h1 className="text-xl font-bold mb-2 text-center">Ещё</h1>
            <h2 className="text-lg font-bold mb-2">Блэк-лист пар</h2>
            <Combobox value={selectedBlacklistItem} onChange={handleSelectBlackList}>
                <div className="relative mt-1">
                    <div className="relative w-full text-left bg-white border border-gray-300 rounded-md shadow-sm cursor-default focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm overflow-hidden">
                        <ComboboxInput
                            className="w-full border-none focus:ring-0 py-2 pl-3 pr-10 text-sm leading-5 text-gray-900"
                            placeholder="BTCUSDT"
                            onChange={(e) => setSelectedBlacklistItem(e.target.value)}
                        />
                        <ComboboxButton className="absolute inset-y-0 right-0 flex items-center pr-2">
                            <svg className="w-5 h-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.87l3.71-3.64a.75.75 0 011.08 1.04l-4.25 4.17a.75.75 0 01-1.06 0L5.23 8.27a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                            </svg>
                        </ComboboxButton>
                    </div>
                    <ComboboxOptions className="absolute z-20 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
                        {blacklistOptionsFiltered.map((coin) => (
                            <ComboboxOption
                                key={coin}
                                value={coin}
                                className={({ active }) =>
                                    `cursor-pointer select-none relative py-2 pl-3 pr-9 ${active ? 'text-white bg-indigo-600' : 'text-gray-900'}`
                                }
                            >
                                {({ selected, active }) => (
                                    <>
                                        <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>{coin}</span>
                                    </>
                                )}
                            </ComboboxOption>
                        ))}
                    </ComboboxOptions>
                </div>
            </Combobox>
            <div className="flex flex-wrap mt-2">
                {settings.coins_blacklist.map((item, index) => (
                    <div key={index} className="flex items-center bg-red-600 text-white px-2 py-1 rounded-full m-1">
                        <span className="ml-2">{item}</span>
                        <button
                            onClick={() => handleRemoveFromBlackList(item)}
                            className="ml-2 -mr-1 text-red-800 hover:text-red-800 focus:outline-none rounded-full bg-red-300 w-6 h-6 flex items-center justify-center"
                        >
                            &times;
                        </button>
                    </div>
                ))}
            </div>
            <div className="flex items-center mb-2">
                <input
                    id="use_spot"
                    name="use_spot"
                    type="checkbox"
                    checked={settings.use_spot}
                    onChange={(e) => setSettings({ ...settings, use_spot: e.target.checked })}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="use_spot" className="ml-2 text-sm font-medium text-gray-900">Использовать спот, а не фьючерсы</label>
            </div>
            <div className="flex items-center mb-2">
                <input
                    id="use_wicks"
                    name="use_wicks"
                    type="checkbox"
                    checked={settings.use_wicks}
                    onChange={(e) => setSettings({ ...settings, use_wicks: e.target.checked })}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="use_wicks" className="ml-2 text-sm font-medium text-gray-900">Использовать максимальное отклонение цены, а не цену открытия</label>
            </div>
            <div className="flex items-center mb-2">
                <input
                    id="use_only_usdt"
                    name="use_only_usdt"
                    type="checkbox"
                    checked={settings.use_only_usdt}
                    onChange={(e) => setSettings({ ...settings, use_only_usdt: e.target.checked })}
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="use_only_usdt" className="ml-2 text-sm font-medium text-gray-900">Только монеты с USDT (Без USDC)</label>
            </div>
        </div>
    );
};

export default BlacklistSettings;
