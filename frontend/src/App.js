import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './Login';
import EmployeePage from './EmployeePage';
import SecurityPage from './SecurityPage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  // Проверяем сохранённого пользователя при загрузке
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

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={
            !user ? <Login onLogin={handleLogin} /> :
            user.role === 'security' ? <SecurityPage user={user} onLogout={handleLogout} /> :
            <EmployeePage user={user} onLogout={handleLogout} />
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;