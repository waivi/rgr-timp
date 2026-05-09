import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Login';
import AdminPage from './AdminPage';
import EmployeePage from './EmployeePage';
import SecurityPage from './SecurityPage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  React.useEffect(() => {
    const saved = localStorage.getItem('user');
    if (saved) {
      setUser(JSON.parse(saved));
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const getDashboard = () => {
    if (!user) return <Login onLogin={handleLogin} />;

    switch (user.role) {
      case 'администратор':
        return <AdminPage user={user} onLogout={handleLogout} />;
      case 'менеджер безопасности':
        return <SecurityPage user={user} onLogout={handleLogout} />;
      case 'сотрудник':
        return <EmployeePage user={user} onLogout={handleLogout} />;
      default:
        return <Login onLogin={handleLogin} />;
    }
  };

  return (
    <Router>
      <div className="App">
        {/* Кнопка быстрого входа как администратор — видна только на странице входа */}
        {!user && (
          <div style={{ position: 'absolute', top: '10px', right: '20px', zIndex: 1000 }}>
            <button
              onClick={async () => {
                try {
                  const axios = (await import('axios')).default;
                  const res = await axios.post('http://localhost:5000/api/login', {
                    login: 'admin',
                    password: '123'
                  });
                  if (res.data.success) {
                    handleLogin(res.data.user);
                  }
                } catch (err) {
                  console.error('Ошибка быстрого входа:', err);
                }
              }}
              style={{
                padding: '8px 16px',
                background: '#722ed1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Войти как администратор
            </button>
          </div>
        )}

        {getDashboard()}
      </div>
    </Router>
  );
}

export default App;