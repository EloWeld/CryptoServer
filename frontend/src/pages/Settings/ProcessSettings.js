import React from 'react';
import { CustomNumberInput, CustomFloatInput } from 'components/CustomNumberInput';

const ProcessSettings = ({ settings, handleChange }) => {
    return (
        <div className="border-2 border-gray-300 shadow-lg rounded p-4">
            <h1 className="text-xl font-bold mb-2 text-center">Настройки процесса</h1>
            <div className="flex flex-row justify-between gap-3">
                <label htmlFor="max_save_minutes" className="block text-sm font-medium text-gray-700">Сколько предыдущих минут рассматриваем</label>
                <CustomNumberInput
                    type="number"
                    id="max_save_minutes"
                    name="max_save_minutes"
                    value={settings.max_save_minutes}
                    onChange={handleChange}
                    required
                />
            </div>
            <div className="flex flex-row justify-between gap-3">
                <ProcessTypeSettings settings={settings} handleChange={handleChange} type="rapid" title="Быстрый рост" />
                <ProcessTypeSettings settings={settings} handleChange={handleChange} type="smooth" title="Плавный рост" />
            </div>
        </div>
    );
};

const ProcessTypeSettings = ({ settings, handleChange, type, title }) => {
    const isRapid = type === 'rapid';

    return (
        <div className="w-2/4">
            <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">{title}</h2>
            <label htmlFor={`${type}_delay`} className="block text-sm font-medium text-gray-700">Интервал между повторными сигналами</label>
            <CustomNumberInput
                type="number"
                id={`${type}_delay`}
                name={`${type}_delay`}
                value={settings[`${type}_delay`]}
                onChange={handleChange}
                required
            />
            <label htmlFor={`check_per_minutes_${type}`} className="block text-sm font-medium text-gray-700">Временной интервал, мин</label>
            <CustomNumberInput
                type="number"
                id={`check_per_minutes_${type}`}
                name={`check_per_minutes_${type}`}
                value={settings[`check_per_minutes_${type}`]}
                onChange={handleChange}
                required
            />
            {isRapid && (<><label htmlFor="price_change_percent" className="block text-sm font-medium text-gray-700">Процент изменения цены</label>
                <CustomFloatInput
                    id="price_change_percent"
                    name="price_change_percent"
                    value={settings.price_change_percent}
                    onChange={handleChange}
                    required
                /></>)}
            {!isRapid && (
                <>
                    <label htmlFor="price_change_trigger_percent" className="block text-sm font-medium text-gray-700">Процент изменения цены для проверки других параметров</label>
                    <input
                        type="text"
                        id="price_change_trigger_percent"
                        name="price_change_trigger_percent"
                        pattern="([0-9]+.{0,1}[0-9]*,{0,1})*[0-9]"
                        value={settings.price_change_trigger_percent}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
                    />
                    <label htmlFor="oi_change_percent" className="block text-sm font-medium text-gray-700">Процент изменения OI</label>
                    <input
                        type="text"
                        id="oi_change_percent"
                        name="oi_change_percent"
                        pattern="([0-9]+.{0,1}[0-9]*,{0,1})*[0-9]"
                        value={settings.oi_change_percent}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
                    />
                    <label htmlFor="cvd_change_percent" className="block text-sm font-medium text-gray-700">Процент изменения CVD</label>
                    <input
                        type="text"
                        id="cvd_change_percent"
                        name="cvd_change_percent"
                        pattern="([0-9]+.{0,1}[0-9]*,{0,1})*[0-9]"
                        value={settings.cvd_change_percent}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
                    />
                    <label htmlFor="v_volumes_change_percent" className="block text-sm font-medium text-gray-700">Процент изменения объёмов</label>
                    <input
                        type="text"
                        id="v_volumes_change_percent"
                        name="v_volumes_change_percent"
                        pattern="([0-9]+.{0,1}[0-9]*,{0,1})*[0-9]"
                        value={settings.v_volumes_change_percent}
                        onChange={handleChange}
                        required
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
                    />
                </>
            )}
        </div>
    );
};

export default ProcessSettings;
