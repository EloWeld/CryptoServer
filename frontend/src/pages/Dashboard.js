import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { Listbox, ListboxOption, ListboxOptions, ListboxButton } from '@headlessui/react';
import { io } from 'socket.io-client';
import { toast } from 'react-toastify';
import { FiVolume2, FiVolumeX } from 'react-icons/fi'; // Импорт иконок



function Dashboard({ isAuthenticated, setIsAuthenticated }) {
  const [settings, setSettings] = useState({ webhooks: [], received_hooks: [], blocked_hooks: 0 });
  const [lastPumps, setLastPumps] = useState([]);
  const [lastDumps, setLastDumps] = useState([]);
  const [timezoneOffset, setTimezoneOffset] = useState(5); // Default timezone offset
  const audioRef = useRef(null);

  const timezones = [
    { value: -5, label: 'UTC-5' },
    { value: -4, label: 'UTC-4' },
    { value: -3, label: 'UTC-3' },
    { value: -2, label: 'UTC-2' },
    { value: -1, label: 'UTC-1' },
    { value: 0, label: 'UTC' },
    { value: 1, label: 'UTC+1' },
    { value: 2, label: 'UTC+2' },
    { value: 3, label: 'UTC+3' },
    { value: 4, label: 'UTC+4' },
    { value: 5, label: 'UTC+5' },
    // Add other timezones as needed
  ];

  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const logsEndRef = useRef(null);
  const [audioEnabled, setAudioEnabled] = useState(false);



  useEffect(() => {
    try {
      const token = localStorage.getItem('token');
      const socket = io('http://127.0.0.1:5000', {
        withCredentials: true,
        auth: {
          token: token,
        },
      });

      socket.on('connect', () => {
        console.log('Connected to server');
      });

      socket.on('log', (message) => {
        console.log(message)
        setLogs((prevLogs) => [...prevLogs, message.data]);
      });

      socket.on('connect_error', (err) => {
        console.log('Connection error:', err);
      });

      return () => {
        socket.off('log');
        socket.off('connect_error');
        socket.disconnect();
      };
    } catch (error) {
      console.log(error);
      toast.error("Not connected to websocket")
      return;
    }
  }, []);

  const startProcess = async () => {
    try {
      const response = await axios.post('/api/start_process');
      if (response.data.status === 'Process started') {
        setIsRunning(true);
      } else {
        toast.error(`Error: ${response.data.status}`);
        console.error(response.data)
      }
    } catch (err) {
      toast.error(`Error: ${err.message}`);
    }
  };

  const stopProcess = async () => {
    try {
      const response = await axios.post('/api/stop_process');
      if (response.data.status === 'Process stopped') {
        setIsRunning(false);
      } else {
        toast.error(`Error: ${response.data.status}`);
        console.error(response.data)
      }
    } catch (err) {
      toast.error(`Error: ${err.message}`);
    }
  };

  useEffect(() => {
    async function fetchUserData() {
      try {
        const userResponse = await axios.get('/api/user');
        console.log(userResponse.data.timezone_offset)
        setTimezoneOffset(userResponse.data.timezone_offset);
      } catch (error) {
        toast.error(`'Error fetching user data: ${error}`)
      }
    }

    async function fetchData() {
      try {
        const result = await axios.get('/api/settings');
        setSettings(result.data);
      } catch (error) {
        toast.error(`'Error fetching settings: ${error}`)
      }
    }

    async function fetchProcessStatus() {
      try {
        const result = await axios.get("/api/get_process_status");
        setIsRunning(result.data.is_running);
      } catch (error) {
        toast.error(`'Error fetching settings: ${error}`)
      }
    }

    fetchUserData();
    fetchData();
    fetchProcessStatus();
  }, []);

  const lastFetchTimeRef = useRef(Date.now());
  useEffect(() => {
    async function fetchChanges() {
      if (Date.now() - lastFetchTimeRef.current < 5000) {
        return;
      }
      lastFetchTimeRef.current = Date.now();
      try {
        const response = await axios.get('/changes_log');
        const data = response.data;
        console.log(data);

        let newPumps = data.filter(item => item.type === 'pump');
        let newDumps = data.filter(item => item.type === 'dump');

        newPumps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        newDumps.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        if (lastPumps.length > 0 || lastDumps.length > 0) {
          const newPumpChanges = newPumps.filter(np => !lastPumps.some(lp => lp.id === np.id));
          const newDumpChanges = newDumps.filter(nd => !lastDumps.some(ld => ld.id === nd.id));

          console.log('Last Pumps:', lastPumps);
          console.log('Last Dumps:', lastDumps);
          console.log('New Pump Changes:', newPumpChanges);
          console.log('New Dump Changes:', newDumpChanges);

          if (newPumpChanges.length > 0 || newDumpChanges.length > 0) {
            if (audioEnabled) {
              audioRef.current.play().catch(error => console.log('Audio play error:', error));
            }

            newPumpChanges.forEach(change => {
              toast.success(`New Pump: ${change.symbol} on ${change.exchange}`);
            });

            newDumpChanges.forEach(change => {
              toast.error(`New Dump: ${change.symbol} on ${change.exchange}`);
            });
          }
        }

        setLastPumps(newPumps);
        setLastDumps(newDumps);
      } catch (error) {
        console.log('Error fetching changes:', error);
      }
    }

    fetchChanges();
    const interval = setInterval(fetchChanges, 5000);
    return () => clearInterval(interval);
  }, [lastPumps, lastDumps, audioEnabled]);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const handleTimezoneChange = async (selectedOffset) => {
    setTimezoneOffset(selectedOffset);

    try {
      await axios.post('/api/user/timezone', { timezone_offset: selectedOffset });
    } catch (error) {
      console.error('Error updating timezone:', error);
    }
  };

  const formatDate = (date, offset) => {
    const utcDate = date.getTime() + (-180 * 60000);
    const newDate = new Date(utcDate + (3600000 * offset) + 3600000 * ((new Date()).getTimezoneOffset() / -60));
    return newDate.toISOString().slice(5, 19).replace('T', ' ');
  };

  const enableAudio = () => {
    const audio = audioRef.current;
    if (audioEnabled) {
      setAudioEnabled(false);
      audio.pause();

    }
    audio.play().then(() => {
      setAudioEnabled(true);
      audio.pause();
      audio.currentTime = 0;
    }).catch(error => {
      console.log('Audio enable error:', error);
    });
  };

  const deleteWebhook = async (webhook_id) => {
    try {
      const result = await axios.delete(`/api/webhook/${webhook_id}`);
      if (result.data.result === "ok") {
        toast.info("Webhook deleted");
        console.log(result.data);
        setSettings(result.data.settings)
      } else {
        toast.warn(`Webhook may not deleted, ${result.data.result}`);
      }
    } catch (error) {
      toast.error(`Error during deleting webhook, ${error}`);
    }
  }

  return (
    <div>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <div className="container mx-auto p-4">
        <audio ref={audioRef} src="/notification.mp3" />


        <div className="mt-4 border rounded flex flex-row justify-between">
          <div className='p-2'>
            <label htmlFor="timezone" className="block text-lg font-bold mb-2">Select Timezone:</label>
            <Listbox value={timezoneOffset} onChange={handleTimezoneChange}>
              {({ open }) => (
                <>
                  <ListboxButton className="block w-40 p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm relative text-left">
                    {timezones.find(tz => tz.value === timezoneOffset).label}
                    <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                      <svg className={`w-5 h-5 text-gray-400 transform ${open ? 'rotate-180' : 'rotate-0'}`} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                        <path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.87l3.71-3.64a.75.75 0 011.08 1.04l-4.25 4.17a.75.75 0 01-1.06 0L5.23 8.27a.75.75 0 01.02-1.06z" clipRule="evenodd" />
                      </svg>
                    </span>
                  </ListboxButton>
                  <ListboxOptions className="absolute mt-1 max-h-60 overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                    {timezones.map((timezone) => (
                      <ListboxOption key={timezone.value} value={timezone.value} className="cursor-pointer select-none relative py-2 pl-3 pr-9">
                        {timezone.label}
                      </ListboxOption>
                    ))}
                  </ListboxOptions>
                </>)}
            </Listbox>
          </div>
          <button onClick={enableAudio} className="bg-blue-500 text-white px-4 py-2 rounded my-auto mr-4">
            {!audioEnabled ? (
              <FiVolume2 className="inline-block mr-2" />
            ) : (
              <FiVolumeX className="inline-block mr-2" />
            )}
            {audioEnabled ? 'Disable Audio Notifications' : 'Enable Audio Notifications'}
          </button>
        </div>
        {/* ——————— Hooks list ——————— */}
        <div className="mt-4 p-2 border rounded">
          <h2 className="text-xl font-bold">Webhooks list</h2>
          {settings.webhooks.length === 0 ?
            (<div className="bg-gray-400 text-gray-200 rounded p-0.5 w-min">Empty</div>)
            : (<ul className="mt-4">
              {settings.webhooks.map((webhook) => (
                <li key={webhook.webhook} className="mb-2 p-2 border rounded flex justify-between items-center">
                  <p>
                    Webhook: <a href={`${settings.domain}/webhook/${webhook.webhook}`} className="text-blue-500">{`${settings.domain}/webhook/${webhook.webhook}`}</a> | Delay: {webhook.delay} seconds | Redirect to: {webhook.redirect_to_url}
                  </p>
                  <button onClick={((e) => { deleteWebhook(webhook.webhook);})} className="bg-red-500 text-white px-4 py-2 rounded ml-4">Delete</button>
                </li>
              ))}
            </ul>)}

        </div>
        {/* ——————— Received hooks ——————— */}
        <div className="mt-4 p-2 border rounded">
          <h2 className="text-xl font-bold">Received Webhooks</h2>
          {settings.received_hooks.length === 0 ?
            (<div className="bg-gray-400 text-gray-200 rounded p-0.5 w-min">Empty</div>)
            : (
              <ul>
                {settings.received_hooks.map((hook) => (
                  <li key={hook.hook_id}>Webhook ID: {hook.hook_id} | Time: {formatDate(new Date(parseFloat(hook.time)), timezoneOffset)}</li>
                ))}
              </ul>)}
        </div>
        {/* ——————— Blocked Hooks ——————— */}
        <div className="mt-4 p-2 border rounded">
          <h2 className="text-xl font-bold">Blocked Hooks</h2>
          <p>Total Blocked Hooks: {settings.blocked_hooks}</p>
        </div>
        {/* ——————— Parsing process ——————— */}
        <div className='mt-4'>
          <button onClick={startProcess} disabled={isRunning} className={"bg-green-500 text-white px-4 py-2 rounded" + (isRunning ? " opacity-25" : "")}>
            Start Process
          </button>
          <button onClick={stopProcess} disabled={!isRunning} className={"bg-red-500 text-white px-4 py-2 rounded ml-4" + (!isRunning ? " opacity-25" : "")}>
            Stop Process
          </button>
          <div className="mt-4 p-4 border rounded">
            <h2 className="text-xl font-bold">Logs</h2>
            <div className="h-44 overflow-y-scroll bg-gray-100 p-2">
              {logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))}
            </div>
          </div>
        </div>
        {/* ——————— Pumps list ——————— */}
        <div className="flex flex-col md:flex-row gap-3 justify-between">
          <div className="mt-4 p-2 border rounded w-full">
            <h2 className="text-xl font-bold border-b">Last <span className="text-green-600">PUMP</span>s</h2>
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2 text-start">Exchange</th>
                  <th className="py-2">Coin</th>
                  <th className="py-2 text-start">Change</th>
                  <th className="py-2 text-start">Interval</th>
                  <th className="py-2 text-start">Created At</th>
                </tr>
              </thead>
              <tbody id="pumps" className="text-center">
                {lastPumps.map((item) => (
                  <tr key={item.id}>
                    <td className="py-2">{item.exchange}</td>
                    <td className="py-2"><a className="text-blue-500" href={`https://www.coinglass.com/tv/Binance_${item.symbol}`}>{item.symbol}</a></td>
                    <td className="py-2">{item.change_amount}</td>
                    <td className="py-2">{item.interval} min</td>
                    <td className="py-2">{formatDate(new Date(item.created_at), timezoneOffset)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* ——————— Dumps list ——————— */}
          <div className="mt-4 p-2 border rounded w-full">
            <h2 className="text-xl font-bold border-b">Last <span className="text-red-600">DUMP</span>s</h2>
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="py-2">Exchange</th>
                  <th className="py-2">Coin</th>
                  <th className="py-2">Change</th>
                  <th className="py-2">Interval</th>
                  <th className="py-2">Created At</th>
                </tr>
              </thead>
              <tbody id="dumps" className="text-center">
                {lastDumps.map((item) => (
                  <tr key={item.id}>
                    <td className="py-2">{item.exchange}</td>
                    <td className="py-2"><a className="text-blue-500" href={`https://www.coinglass.com/tv/Binance_${item.symbol}`}>{item.symbol}</a></td>
                    <td className="py-2">{item.change_amount}</td>
                    <td className="py-2">{item.interval} min</td>
                    <td className="py-2">{formatDate(new Date(item.created_at), timezoneOffset)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
