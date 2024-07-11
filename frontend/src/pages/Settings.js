import React, { useEffect, useState } from 'react';
import axios from 'axiosConfig';
import Navbar from '../components/Navbar';
import { toast } from 'react-toastify';
import { CustomNumberInput, CustomFloatInput } from 'components/CustomNumberInput';
import {
  Combobox, ComboboxInput, ComboboxButton, ComboboxOptions, ComboboxOption,
} from '@headlessui/react';
import ProcessSettings from './Settings/ProcessSettings';
import WebhookSettings from './Settings/WebhookSettings';
import BlacklistSettings from './Settings/BlacklistSettings';

function Settings({ isAuthenticated, setIsAuthenticated }) {
  const [settings, setSettings] = useState({
    domain: '',

    rapid_delay: 0,
    smooth_delay: 0,
    check_per_minutes_rapid: 0,
    check_per_minutes_smooth: 0,

    rapid_pump_webhook: '',
    rapid_pump_data: '',
    reverse_rapid_pump_webhook: '',
    reverse_rapid_pump_data: '',
    rapid_enable_pump: false,
    reverse_rapid_enable_pump: false,

    rapid_dump_webhook: '',
    rapid_dump_data: '',
    reverse_rapid_dump_webhook: '',
    reverse_rapid_dump_data: '',
    rapid_enable_dump: false,
    reverse_rapid_enable_dump: false,

    smooth_pump_webhook: '',
    smooth_pump_data: '',
    reverse_smooth_pump_webhook: '',
    reverse_smooth_pump_data: '',
    smooth_enable_pump: false,
    reverse_smooth_enable_pump: false,

    smooth_dump_webhook: '',
    smooth_dump_data: '',
    reverse_smooth_dump_webhook: '',
    reverse_smooth_dump_data: '',
    smooth_enable_dump: false,
    reverse_smooth_enable_dump: false,

    max_save_minutes: 0,
    price_change_percent: '',
    price_change_trigger_percent: '',
    oi_change_percent: '',
    cvd_change_percent: '',
    v_volumes_change_percent: '',
    use_spot: false,
    use_wicks: false,
    tg_id: -1,
    coins_blacklist: [],
    use_only_usdt: false,

    default_vol_usd: 20,
    reverse_vol_usd: 20,
    reverse_last_order_dist: 8,
    reverse_full_orders_count: 10,
    reverse_orders_count: 8,
    reverse_multiplier: 1.5,
    reverse_density: 0.7,
  });
  // ————— Blacklist —————

  const [selectedBlacklistItem, setSelectedBlacklistItem] = useState('');
  const [blacklistOptions, setBlacklistOptions] = useState([]);
  // ————— Tabs —————
  const [tabs, setTabs] = useState({ webhook: 'default' });


  const blacklistOptionsFiltered =
    selectedBlacklistItem === ''
      ? blacklistOptions
      : blacklistOptions.filter((coin) =>
        coin.toLowerCase().includes(selectedBlacklistItem.toLowerCase())
      );

  useEffect(() => {
    async function fetchData() {
      const result = await axios.get('/api/settings');
      setSettings(result.data);
    }
    fetchData();
    async function fetchCoins() {
      const result = await axios.get('/api/coins');
      console.log('asdasd', result)
      if (result.data && result.data.message === undefined) {
        setBlacklistOptions(result.data.map(x => x.name))
      }
    }
    fetchCoins();
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


  const handleSelectBlackList = (item) => {
    if (!settings.coins_blacklist.includes(item)) {
      setSettings({ ...settings, coins_blacklist: [...settings.coins_blacklist, item] });
    }
    setSelectedBlacklistItem('');
  };

  const handleRemoveFromBlackList = (item) => {
    setSettings({ ...settings, coins_blacklist: settings.coins_blacklist.filter(x => x !== item) });
  };

  return (
    <div>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <div className="container mx-auto p-4">
        <div className="flex flex-row gap-5 items-start justify-start">
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
            <CustomNumberInput
              type="text" id="tg_id" name="tg_id" value={settings.tg_id} onChange={handleChange} required
            />
          </div>
          <WebhookSettings settings={settings} handleChange={handleChange} tabs={tabs} setTabs={setTabs} />
          <ProcessSettings settings={settings} handleChange={handleChange} />
          <BlacklistSettings
            settings={settings} setSettings={setSettings} blacklistOptions={blacklistOptions}
          />
          <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">Save</button>
        </form>
      </div>
    </div>
  );
}

export default Settings;
