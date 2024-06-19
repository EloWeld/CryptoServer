import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import axios from 'axiosConfig';
import { toast } from 'react-toastify';
import { CustomNumberInput } from 'components/CustomNumberInput';

function AddWebhook({ isAuthenticated, setIsAuthenticated }) {
  const [formData, setFormData] = useState({
    webhook: '',
    redirect_to_url: '',
    delay: '',
    calls_amount: '',
    strategy: 'single'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/webhook', formData);
      toast.success('Webhook added successfully');
    } catch (error) {
      toast.error('Error during adding webhook');
      console.error('Error saving settings:', error);
    }
  };

  return (
    <div>
      <Navbar isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
      <div className="w-full mx-auto max-w-lg py-5">
        <div className="text-center border-b border-gray-200">
          <h1 className="text-2xl font-bold mb-2">Add Webhook</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 mt-2">
          <div className="md:flex md:items-center mb-6">
            <div className="md:w-1/3">
              <label htmlFor="webhook" className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4">Webhook ID</label>
            </div>
            <div className="md:w-2/3">
              <input
                type="text"
                id="webhook"
                name="webhook"
                value={formData.webhook}
                onChange={handleChange}
                required
                className="bg-white-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500"
              />
            </div>
          </div>
          <div className="md:flex md:items-center mb-6">
            <div className="md:w-1/3">
              <label htmlFor="redirect_to_url" className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4">Redirect to URL</label>
            </div>
            <div className="md:w-2/3">
              <input
                type="text"
                id="redirect_to_url"
                name="redirect_to_url"
                value={formData.redirect_to_url}
                onChange={handleChange}
                placeholder="https://google.com"
                required
                className="bg-white-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500"
              />
            </div>
          </div>
          <div className="md:flex md:items-center mb-6">
            <div className="md:w-1/3">
              <label htmlFor="delay" className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4">Delay (seconds)</label>
            </div>
            <div className="md:w-2/3">
              <CustomNumberInput id="delay"
                name="delay"
                value={formData.delay}
                onChange={handleChange}
                required />
            </div>
          </div>
          <div className="md:flex md:items-center mb-6">
            <div className="md:w-1/3">
              <label htmlFor="calls_amount" className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4">Calls amount</label>
            </div>
            <div className="md:w-2/3">
              <CustomNumberInput id="calls_amount"
                name="calls_amount"
                value={formData.calls_amount}
                onChange={handleChange}
                required />
            </div>
          </div>
          <div className="md:flex md:items-center mb-6">
            <div className="md:w-1/3">
              <label htmlFor="strategy" className="block text-gray-500 font-bold md:text-right mb-1 md:mb-0 pr-4">Strategy</label>
            </div>
            <div className="md:w-2/3">
              <ul className="items-center w-full text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg sm:flex dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                <li className="w-full border-b border-gray-200 sm:border-b-0 sm:border-r dark:border-gray-600">
                  <div className="flex items-center px-3 gap-3">
                    <input
                      id="strategy_single"
                      type="radio"
                      value="single"
                      name="strategy"
                      checked={formData.strategy === 'single'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                    />
                    <label htmlFor="strategy_single" className="w-full py-3 text-sm font-medium text-gray-900 dark:text-gray-300">Single Call</label>
                  </div>
                </li>
                <li className="w-full border-b border-gray-200 sm:border-b-0 sm:border-r dark:border-gray-600">
                  <div className="flex items-center px-3 gap-3">
                    <input
                      id="strategy_mult"
                      type="radio"
                      value="mult"
                      name="strategy"
                      checked={formData.strategy === 'mult'}
                      onChange={handleChange}
                      className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                    />
                    <label htmlFor="strategy_mult" className="w-full py-3 text-sm font-medium text-gray-900 dark:text-gray-300">Multiple Calls</label>
                  </div>
                </li>
              </ul>
            </div>
          </div>
          <div className="md:flex md:items-center">
            <div className="md:w-1/3"></div>
            <div className="md:w-2/3">
              <button
                type="submit"
                className="shadow bg-green-500 hover:bg-green-400 focus:shadow-outline focus:outline-none text-white font-bold py-2 px-4 rounded"
              >
                Add
              </button>
            </div>
          </div>
        </form>

      </div>
    </div>
  );
}

export default AddWebhook;
