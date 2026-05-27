import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './Login';
import AdminPage from './AdminPage';
import EmployeePage from './EmployeePage';
import SecurityPage from './SecurityPage';
import DoorPage from './DoorPage';
import InsidePage from './InsidePage';
import './App.css';

function App() {
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
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
        <Routes>
          <Route path="/" element={getDashboard()} />
          <Route path="/door" element={<DoorPage />} />
          <Route path="/inside" element={<InsidePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;