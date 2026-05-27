import React, { useState } from 'react';
import axios from 'axios';

function Login({ onLogin }) {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        login: login,
        password: password
      });

      if (response.data.success) {
        localStorage.setItem('token', response.data.token);
        onLogin(response.data.user);
      }
    } catch (err) {
      if (err.response && err.response.status === 429) {
        setError('Слишком много попыток. Подождите минуту.');
      } else {
        setError('Неверный логин или пароль');
      }
    }
  };

  return (
    <div className="login-container">
      <h1>Доступ в технические помещения</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Логин:</label>
          <input
            type="text"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Пароль:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <button type="submit">Войти</button>
      </form>

      <div style={{ marginTop: '20px', padding: '15px', background: '#f9f9f9', borderRadius: '8px' }}>
        <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>
          Тестовые учётные записи (пароль везде "123"):
        </p>
        <table style={{ width: '100%', fontSize: '13px', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#e0e0e0' }}>
              <th style={thStyle}>Логин</th>
              <th style={thStyle}>Роль</th>
              <th style={thStyle}>Кто</th>
            </tr>
          </thead>
          <tbody>
            <tr><td style={tdStyle}>admin</td><td style={tdStyle}>Администратор</td><td style={tdStyle}>Админов В.С.</td></tr>
            <tr><td style={tdStyle}>security</td><td style={tdStyle}>Менеджер безопасности</td><td style={tdStyle}>Охранников С.П.</td></tr>
            <tr><td style={tdStyle}>security2</td><td style={tdStyle}>Менеджер безопасности</td><td style={tdStyle}>Безопасникова А.И.</td></tr>
            <tr><td style={tdStyle}>plumber</td><td style={tdStyle}>Сотрудник (сантехник)</td><td style={tdStyle}>Сантехников П.А.</td></tr>
            <tr><td style={tdStyle}>electric</td><td style={tdStyle}>Сотрудник (электрик)</td><td style={tdStyle}>Электриков В.И.</td></tr>
            <tr><td style={tdStyle}>maid</td><td style={tdStyle}>Сотрудник (горничная)</td><td style={tdStyle}>Горничная М.С.</td></tr>
            <tr><td style={tdStyle}>tech</td><td style={tdStyle}>Сотрудник (техник)</td><td style={tdStyle}>Технический Н.Д.</td></tr>
            <tr><td style={tdStyle}>manager</td><td style={tdStyle}>Сотрудник (завхоз)</td><td style={tdStyle}>Завхозов И.П.</td></tr>
            <tr><td style={tdStyle}>lift</td><td style={tdStyle}>Сотрудник (лифтёр)</td><td style={tdStyle}>Лифтов А.Н.</td></tr>
            <tr><td style={tdStyle}>cleaner</td><td style={tdStyle}>Сотрудник (уборщик)</td><td style={tdStyle}>Уборщиков Д.С.</td></tr>
          </tbody>
        </table>
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '14px' }}>
        <a href="/door" style={{ 
          color: '#e94560', 
          textDecoration: 'none',
          fontWeight: 'bold',
          fontSize: '16px'
        }}>
          🚪 Зайти в помещение (симуляция двери)
        </a>
      </div>
    </div>
  );
}

const thStyle = { border: '1px solid #ccc', padding: '4px 8px', textAlign: 'left' };
const tdStyle = { border: '1px solid #ccc', padding: '4px 8px' };

export default Login;