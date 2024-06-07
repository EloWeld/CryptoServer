import React, { useEffect, useState } from 'react';
import axios from 'axiosConfig';
import Navbar from '../components/Navbar';
import { toast } from 'react-toastify';
import { CustomNumberInput, CustomFloatInput } from '../components/CustomNumberInput';

function Settings({ isAuthenticated, setIsAuthenticated }) {
  const [settings, setSettings] = useState({
    domain: '',

    rapid_delay: 0,
    smooth_delay: 0,
    check_per_minutes_rapid: 0,
    check_per_minutes_smooth: 0,

    rapid_pump_webhook: '',
    rapid_pump_data: '',
    rapid_enable_pump: false,

    rapid_dump_webhook: '',
    rapid_dump_data: '',
    rapid_enable_dump: false,

    smooth_pump_webhook: '',
    smooth_pump_data: '',
    smooth_enable_pump: false,

    smooth_dump_webhook: '',
    smooth_dump_data: '',
    smooth_enable_dump: false,

    max_save_minutes: 0,
    price_change_percent: '',
    price_change_trigger_percent: '',
    oi_change_percent: '',
    cvd_change_percent: '',
    v_volumes_change_percent: '',
    use_spot: false,
    use_wicks: false,
    tg_id: -1,
  });

  useEffect(() => {
    async function fetchData() {
      const result = await axios.get('/api/settings');
      setSettings(result.data);
    }
    fetchData();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/settings', settings);
      toast.success('Settings saved successfully')
    } catch (error) {
      toast.error('Error saving settings')
      console.error('Error saving settings:', error);
    }
  };

  return (
    <div>

      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <div className="container mx-auto p-4 ">
        <div className="flex flex-row gap-5 items-start justify-start">
          {/* <button className="w-9 h-9 bg-blue-500 text-white rounded-full flex items-center justify-center" onClick={() => window.location.href = '/'}>
            ←
          </button> */}
          <h1 className="text-2xl font-bold mb-4">Settings</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="domain" className="block text-sm font-medium text-gray-700">Domain</label>
            <input
              type="text" id="domain" name="domain" value={settings.domain} onChange={handleChange} required className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
            />
          </div>
          <div>
            <label htmlFor="tg_id" className="block text-sm font-medium text-gray-700">Telegram ID</label>
            <CustomNumberInput type="text" id="tg_id" name="tg_id" value={settings.tg_id} onChange={handleChange} required />
          </div>
          <div className="border-2 border-gray-300 shadow-lg rounded p-4">
            <h1 className="text-xl font-bold mb-2 text-center">Requests settings</h1>
            <div className="flex flex-row justify-between gap-5">
              <div className="w-full">
                <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">Быстрый рост</h2>

                <div>
                  <label htmlFor="rapid_pump_webhook" className="block text-sm font-medium text-gray-700">Pump Webhook</label>
                  <input
                    type="text" id="rapid_pump_webhook" name="rapid_pump_webhook" value={settings.rapid_pump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div>
                  <label htmlFor="rapid_pump_data" className="block text-sm font-medium text-gray-700">Pump Data</label>
                  <textarea
                    id="rapid_pump_data" name="rapid_pump_data" rows="4" value={settings.rapid_pump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div className="flex items-center mb-2">
                  <input
                    id="rapid_enable_pump" name="rapid_enable_pump" type="checkbox" checked={settings.rapid_enable_pump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="rapid_enable_pump" className="ml-2 text-sm font-medium text-gray-900">Enable Pump</label>
                </div>
                <div>
                  <label htmlFor="rapid_dump_webhook" className="block text-sm font-medium text-gray-700">Dump Webhook</label>
                  <input
                    type="text" id="rapid_dump_webhook" name="rapid_dump_webhook" value={settings.rapid_dump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div>
                  <label htmlFor="rapid_dump_data" className="block text-sm font-medium text-gray-700">Dump Data</label>
                  <textarea
                    id="rapid_dump_data" name="rapid_dump_data" rows="4" value={settings.rapid_dump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div className="flex items-center mb-2">
                  <input
                    id="rapid_enable_dump" name="rapid_enable_dump" type="checkbox" checked={settings.rapid_enable_dump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="rapid_enable_dump" className="ml-2 text-sm font-medium text-gray-900">Enable Dump</label>
                </div>
              </div>
              <div className="w-full">
                <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">Плавный рост</h2>
                <div>
                  <label htmlFor="smooth_pump_webhook" className="block text-sm font-medium text-gray-700">Pump Webhook</label>
                  <input
                    type="text" id="smooth_pump_webhook" name="smooth_pump_webhook" value={settings.smooth_pump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div>
                  <label htmlFor="smooth_pump_data" className="block text-sm font-medium text-gray-700">Pump Data</label>
                  <textarea
                    id="smooth_pump_data" name="smooth_pump_data" rows="4" value={settings.smooth_pump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div className="flex items-center mb-2">
                  <input
                    id="smooth_enable_pump" name="smooth_enable_pump" type="checkbox" checked={settings.smooth_enable_pump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="smooth_enable_pump" className="ml-2 text-sm font-medium text-gray-900">Enable Pump</label>
                </div>
                <div>
                  <label htmlFor="smooth_dump_webhook" className="block text-sm font-medium text-gray-700">Dump Webhook</label>
                  <input
                    type="text" id="smooth_dump_webhook" name="smooth_dump_webhook" value={settings.smooth_dump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div>
                  <label htmlFor="smooth_dump_data" className="block text-sm font-medium text-gray-700">Dump Data</label>
                  <textarea
                    id="smooth_dump_data" name="smooth_dump_data" rows="4" value={settings.smooth_dump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                  />
                </div>
                <div className="flex items-center mb-2">
                  <input
                    id="smooth_enable_dump" name="smooth_enable_dump" type="checkbox" checked={settings.smooth_enable_dump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="smooth_enable_dump" className="ml-2 text-sm font-medium text-gray-900">Enable Dump</label>
                </div>
              </div>
            </div>
          </div>
          <div className="border-2 border-gray-300 shadow-lg rounded p-4">
            <h1 className="text-xl font-bold mb-2 text-center">Trade settings</h1>
            <div className="flex flex-row justify-between gap-3">
              <label htmlFor="max_save_minutes" className="block text-sm font-medium text-gray-700">Сколько предыдущих минут рассматриваем</label>
              <CustomNumberInput type="number"
                id="max_save_minutes"
                name="max_save_minutes"
                value={settings.max_save_minutes}
                onChange={handleChange}
                required />
            </div>
            <div className="flex flex-row justify-between gap-3">
              <div className="w-2/4">
                <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">Быстрый рост</h2>

                <label htmlFor="rapid_delay" className="block text-sm font-medium text-gray-700">Интервал между повторными сигналами</label>
                <CustomNumberInput type="number"
                  id="rapid_delay"
                  name="rapid_delay"
                  value={settings.rapid_delay}
                  onChange={handleChange}
                  required />
                <label htmlFor="check_per_minutes_rapid" className="block text-sm font-medium text-gray-700">Временной интервал, мин</label>
                <CustomNumberInput type="number"
                  id="check_per_minutes_rapid"
                  name="check_per_minutes_rapid"
                  value={settings.check_per_minutes_rapid}
                  onChange={handleChange}
                  required />
                <label htmlFor="price_change_percent" className="block text-sm font-medium text-gray-700">Процент изменения цены</label>
                <CustomFloatInput
                  id="price_change_percent"
                  name="price_change_percent"
                  value={settings.price_change_percent}
                  onChange={handleChange}
                  required />
              </div>
              <div className="w-2/4">
                <h2 className="border-b-2 border-gray-300 text-lg font-bold mb-2">Плавный рост</h2>

                <label htmlFor="smooth_delay" className="block text-sm font-medium text-gray-700">Интервал между повторными сигналами</label>
                <CustomNumberInput type="number"
                  id="smooth_delay"
                  name="smooth_delay"
                  value={settings.rapid_delay}
                  onChange={handleChange}
                  required />
                <label htmlFor="check_per_minutes_smooth" className="block text-sm font-medium text-gray-700">Временной интервал, мин</label>
                <input
                  type="number"
                  id="check_per_minutes_smooth"
                  name="check_per_minutes_smooth"
                  value={settings.check_per_minutes_smooth}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
                />
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
              </div>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Другие опции</label>
            <div className="flex items-center mb-2">
              <input
                id="use_spot"
                name="use_spot"
                type="checkbox"
                checked={settings.use_spot}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="use_spot" className="ml-2 text-sm font-medium text-gray-900">Use spot?</label>
            </div>
            <div className="flex items-center mb-2">
              <input
                id="use_wicks"
                name="use_wicks"
                type="checkbox"
                checked={settings.use_wicks}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="use_wicks" className="ml-2 text-sm font-medium text-gray-900">Use wicks?</label>
            </div>
          </div>
          <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">Save</button>
        </form>

      </div>
    </div>
  );
}

export default Settings;
