import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import AddWebhook from './pages/AddWebhook';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
  
    useEffect(() => {
      const token = localStorage.getItem('token');
      if (token) {
        setIsAuthenticated(true);
      }
    }, []);
  
    return (
    <Router>
      <Switch>
        <Route path="/" exact>
          {!isAuthenticated ? (<Home />) : (<Dashboard isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />)}
        </Route>
        
        <Route path="/login">
          <Auth setIsAuthenticated={setIsAuthenticated} />
        </Route>
        <Route path="/add-webhook">
          <AddWebhook isAuthenticated={isAuthenticated} />
        </Route>
        <Route path="/dashboard">
          <Dashboard isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
        </Route>
        <Route path="/settings">
          <Settings isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
        </Route>
      </Switch>
    </Router>
  );
}

export default App;
