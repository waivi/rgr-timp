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
        onLogin(response.data.user);
      }
    } catch (err) {
      setError('Неверный логин или пароль');
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
        {error && <p style={{color: 'red'}}>{error}</p>}
        <button type="submit">Войти</button>
      </form>
      <p style={{marginTop: '20px', color: '#666'}}>
        Для теста: логин "security" / пароль "123" (охранник)<br/>
        Или: логин "plumber" / пароль "123" (сантехник)
      </p>
    </div>
  );
}

export default Login;