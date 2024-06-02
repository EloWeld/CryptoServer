import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { toast } from 'react-toastify';
import { CustomNumberInput, CustomFloatInput } from '../components/CustomNumberInput';

function Settings({ isAuthenticated, setIsAuthenticated }) {
  const [settings, setSettings] = useState({
    domain: '',
    pump_webhook: '',
    pump_data: '',
    enable_pump: false,
    dump_webhook: '',
    dump_data: '',
    enable_dump: false,
    max_save_minutes: 0,
    check_per_minutes: 0,
    price_change_percent: '',
    check_per_minutes_mode_2: 0,
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
          <div className="flex flex-row justify-between gap-5">
            <div className="col w-full">
              <div>
                <label htmlFor="pump_webhook" className="block text-sm font-medium text-gray-700">Pump Webhook</label>
                <input
                  type="text" id="pump_webhook" name="pump_webhook" value={settings.pump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
              </div>
              <div>
                <label htmlFor="pump_data" className="block text-sm font-medium text-gray-700">Pump Data</label>
                <textarea
                  id="pump_data" name="pump_data" rows="4" value={settings.pump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
              </div>
              <div className="flex items-center mb-2">
                <input
                  id="enable_pump" name="enable_pump" type="checkbox" checked={settings.enable_pump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="enable_pump" className="ml-2 text-sm font-medium text-gray-900">Enable pump</label>
              </div>
            </div>
            <div className="col w-full">
              <div>
                <label htmlFor="dump_webhook" className="block text-sm font-medium text-gray-700">Dump Webhook</label>
                <input
                  type="text" id="dump_webhook" name="dump_webhook" value={settings.dump_webhook} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
              </div>
              <div>
                <label htmlFor="dump_data" className="block text-sm font-medium text-gray-700">Dump Data</label>
                <textarea
                  id="dump_data" name="dump_data" rows="4" value={settings.dump_data} onChange={handleChange} className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-1"
                />
              </div>
              <div className="flex items-center mb-2">
                <input
                  id="enable_dump" name="enable_dump" type="checkbox" checked={settings.enable_dump} onChange={handleChange} className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="enable_dump" className="ml-2 text-sm font-medium text-gray-900">Enable dump</label>
              </div>
            </div>
          </div>
          <div className="flex flex-row justify-between gap-3">
            <label htmlFor="max_save_minutes" className="block text-sm font-medium text-gray-700">Maximum save minutes</label>
            <CustomNumberInput type="number"
              id="max_save_minutes"
              name="max_save_minutes"
              value={settings.max_save_minutes}
              onChange={handleChange}
              required />
          </div>
          <div className="flex flex-row justify-between gap-3">
            <div className="w-2/4">
              <label className="block text-lg font-medium text-gray-700">Mode Simple</label>
              <label htmlFor="check_per_minutes" className="block text-sm font-medium text-gray-700">Check per minutes</label>
              <CustomNumberInput type="number"
                id="check_per_minutes"
                name="check_per_minutes"
                value={settings.check_per_minutes}
                onChange={handleChange}
                required />
              <label htmlFor="price_change_percent" className="block text-sm font-medium text-gray-700">Price change percent</label>
              <CustomFloatInput
                id="price_change_percent"
                name="price_change_percent"
                value={settings.price_change_percent}
                onChange={handleChange}
                required />
            </div>
            <div className="w-2/4">
              <label className="block text-lg font-medium text-gray-700">Mode Hard</label>
              <label htmlFor="check_per_minutes_mode_2" className="block text-sm font-medium text-gray-700">Check per minutes hard</label>
              <input
                type="number"
                id="check_per_minutes_mode_2"
                name="check_per_minutes_mode_2"
                value={settings.check_per_minutes_mode_2}
                onChange={handleChange}
                required
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2"
              />
              <label htmlFor="price_change_trigger_percent" className="block text-sm font-medium text-gray-700">Price change trigger percent</label>
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
              <label htmlFor="oi_change_percent" className="block text-sm font-medium text-gray-700">OI change percent</label>
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
              <label htmlFor="cvd_change_percent" className="block text-sm font-medium text-gray-700">CVD change percent</label>
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
              <label htmlFor="v_volumes_change_percent" className="block text-sm font-medium text-gray-700">Vertical Volumes change percent</label>
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Options</label>
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
