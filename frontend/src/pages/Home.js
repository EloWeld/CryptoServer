import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-10 rounded-lg shadow-lg text-center">
        <img alt="logo" className="w-24 h-24 m-auto" src="/images/logo.png"/>
        <h1 className="text-5xl font-bold text-gray-800 mb-6">Welcome to DaVinchi's server</h1>
        <p className="text-gray-600 mb-8">Your ultimate solution for trading projects.</p>
        <Link to="/login" className="px-6 py-2 bg-blue-500 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition duration-300">
          Login
        </Link>
      </div>
    </div>
  );
}

export default Home;
