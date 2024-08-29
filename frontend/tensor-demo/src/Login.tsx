import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import './Login.css';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = () => {
    // Static credentials check
    if (username === 'weekend' && password === 'playbook') {
      login();
      navigate('/');
    } else {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>Initech Knowledge Portal (demo app)</h2>
        <form onSubmit={(e) => { e.preventDefault(); handleLogin(); }}>
          <label>
            Username:
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </label>
          <label>
            Password:
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
          {error && <div className="error-message">{error}</div>}
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
