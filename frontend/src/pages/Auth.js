import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import axios from 'axiosConfig';
import instance from 'axiosConfig';

function Auth({ setIsAuthenticated }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const history = useHistory();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await instance.post('/api/login', { username, password });
      if (response.status === 200) {
        const { token } = response.data;
        localStorage.setItem('token', token);
        setIsAuthenticated(true);
        history.push('/dashboard');
      }
    } catch (error) {
      setError(`Invalid credentials ${error}`);
      console.log(error);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-200 p-4 sm:p-6 md:p-8">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <div className="mb-4">
          <label className="block mb-1 font-semibold">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block mb-1 font-semibold">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-700 transition duration-300"
        >
          Login
        </button>
      </form>
    </div>
  );
}

export default Auth;
