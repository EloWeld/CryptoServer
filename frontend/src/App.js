import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import AddWebhook from './pages/AddWebhook';
import Charts from './pages/Charts';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log("Token found");
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>; // Или любой другой индикатор загрузки
  }

  const ProtectedRoute = ({ component: Component, ...rest }) => (
    <Route
      {...rest}
      render={(props) =>
        isAuthenticated ? (
          <Component {...props} isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );

  return (
    <Router>
      <Switch>
        <Route path="/" exact>
          {!isAuthenticated ? <Home /> : <Dashboard isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />}
        </Route>
        <Route path="/login">
          <Auth setIsAuthenticated={setIsAuthenticated} />
        </Route>
        <ProtectedRoute path="/charts" component={Charts} />
        <ProtectedRoute path="/add-webhook" component={AddWebhook} />
        <ProtectedRoute path="/dashboard" component={Dashboard} />
        <ProtectedRoute path="/settings" component={Settings} />
      </Switch>
    </Router>
  );
}

export default App;