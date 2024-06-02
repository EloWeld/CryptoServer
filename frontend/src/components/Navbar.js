import React from 'react';
import { Link, useHistory } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

function Navbar({ isAuthenticated, setIsAuthenticated }) {
  const history = useHistory();

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout');
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      history.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      toast.error(`Logout error: ${error}`)
    }
  };

  return (
    <nav className="bg-indigo-50  shadow-md p-2">
      <div className="container mx-auto flex justify-between items-center">
      
          <Link to="/"><div className="text-2xl font-bold flex flex-row items-center gap-2"><img alt="logo" className="w-10 h-10" src="/images/logo.png"/><span>DaVinchi's</span></div></Link>
        
        <div className="flex space-x-4">
          {isAuthenticated ? (
            <>
            <Link to="/add-webhook" className="text-gray-800 hover:text-gray-600 p-2">
                Add Webhook
              </Link>
              <Link to="/dashboard" className="text-gray-800 hover:text-gray-600 p-2">
                Dashboard
              </Link>
              <Link to="/settings" className="text-gray-800 hover:text-gray-600 p-2">
                Settings
              </Link>
              <button onClick={handleLogout} className="text-white bg-red-400 rounded hover:bg-red-700 transition duration-300 p-2">
                Logout
              </button>
            </>
          ) : (
            <Link to="/login" className="text-gray-800 hover:text-gray-600">
              Login
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
