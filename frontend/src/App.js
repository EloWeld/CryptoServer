import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import AddWebhook from './pages/AddWebhook';
import Charts from './pages/Charts';
import axios from './axiosConfig';



function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      console.log("Found token, try to verify");
      axios.get('/api/verify-token', {
        headers: {
          'Authorization': token
        }
      })
        .then(response => {
          const data = response.data;
          console.log("Verify-result", data);
          if (data.message === "Token is valid") {
            setIsAuthenticated(true);
          } else {
            setIsAuthenticated(false);
          }
        })
        .catch((e) => {
          console.log("Verify request error", e);
          setIsAuthenticated(false);
        });
    } else {
      console.log("No token");
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

  const PublicRoute = ({ component: Component, ...rest }) => (
    <Route
      {...rest}
      render={(props) =>
        !isAuthenticated ? (
          <Component {...props} setIsAuthenticated={setIsAuthenticated} />
        ) : (
          <Redirect to="/dashboard" />
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
        <PublicRoute path="/login" component={Auth} />
        <ProtectedRoute path="/charts" component={Charts} />
        <ProtectedRoute path="/add-webhook" component={AddWebhook} />
        <ProtectedRoute path="/dashboard" component={Dashboard} />
        <ProtectedRoute path="/settings" component={Settings} />
      </Switch>
    </Router>
  );
}

export default App;