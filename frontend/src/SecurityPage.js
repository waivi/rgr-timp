import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SecurityPage({ user, onLogout }) {
  const [tab, setTab] = useState('generate'); // generate / keys / stats
  const [users, setUsers] = useState([]);
  const [doors, setDoors] = useState([]);
  const [allKeys, setAllKeys] = useState([]);
  const [statistics, setStatistics] = useState([]);
  
  // Для формы генерации
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedDoor, setSelectedDoor] = useState('');
  const [hours, setHours] = useState(2);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadUsers();
    loadDoors();
  }, []);

  const loadUsers = async () => {
    const res = await axios.get('http://localhost:5000/api/security/users');
    setUsers(res.data);
  };

  const loadDoors = async () => {
    const res = await axios.get('http://localhost:5000/api/security/doors');
    setDoors(res.data);
  };

  const loadKeys = async () => {
    const res = await axios.get('http://localhost:5000/api/security/keys');
    setAllKeys(res.data);
  };

  const loadStatistics = async () => {
    const res = await axios.get('http://localhost:5000/api/security/statistics');
    setStatistics(res.data);
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setMessage('');
    
    try {
      const res = await axios.post('http://localhost:5000/api/security/keys/generate', {
        userId: parseInt(selectedUser),
        doorId: parseInt(selectedDoor),
        hours: hours
      });
      
      if (res.data.success) {
        setMessage(`Код ${res.data.key.pin} создан для ${res.data.key.userName}`);
        setSelectedUser('');
        setSelectedDoor('');
      }
    } catch (err) {
      setMessage('Ошибка при создании кода');
    }
  };

  const handleRevoke = async (keyId) => {
    await axios.post(`http://localhost:5000/api/security/keys/${keyId}/revoke`);
    loadKeys();
  };

  const handleTabClick = (tabName) => {
    setTab(tabName);
    if (tabName === 'keys') loadKeys();
    if (tabName === 'stats') loadStatistics();
  };

  return (
    <div>
      {/* Шапка */}
      <div style={{display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#f0f0f0'}}>
        <h2>Панель безопасности</h2>
        <div>
          <span style={{marginRight: '20px'}}>{user.name}</span>
          <button onClick={onLogout}>Выйти</button>
        </div>
      </div>

      {/* Вкладки */}
      <div style={{display: 'flex', gap: '10px', padding: '10px 20px', background: '#e0e0e0'}}>
        <button onClick={() => handleTabClick('generate')} 
                style={{padding: '8px 16px', background: tab === 'generate' ? '#1890ff' : '#fff'}}>
          Создать код
        </button>
        <button onClick={() => handleTabClick('keys')}
                style={{padding: '8px 16px', background: tab === 'keys' ? '#1890ff' : '#fff'}}>
          Все коды
        </button>
        <button onClick={() => handleTabClick('stats')}
                style={{padding: '8px 16px', background: tab === 'stats' ? '#1890ff' : '#fff'}}>
          Статистика
        </button>
      </div>

      {/* Содержимое вкладок */}
      <div style={{padding: '20px'}}>
        
        {/* Вкладка: Создать код */}
        {tab === 'generate' && (
          <div>
            <h3>Создать новый код доступа</h3>
            <form onSubmit={handleGenerate}>
              <div style={{marginBottom: '10px'}}>
                <label>Сотрудник: </label>
                <select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)} required>
                  <option value="">Выберите сотрудника</option>
                  {users.filter(u => u.role === 'employee').map(u => (
                    <option key={u.id} value={u.id}>{u.name}</option>
                  ))}
                </select>
              </div>
              <div style={{marginBottom: '10px'}}>
                <label>Дверь: </label>
                <select value={selectedDoor} onChange={(e) => setSelectedDoor(e.target.value)} required>
                  <option value="">Выберите дверь</option>
                  {doors.map(d => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>
              <div style={{marginBottom: '10px'}}>
                <label>На сколько часов: </label>
                <input type="number" value={hours} onChange={(e) => setHours(parseInt(e.target.value))} min="1" max="24" />
              </div>
              <button type="submit">Создать</button>
            </form>
            {message && <p style={{marginTop: '10px', fontWeight: 'bold'}}>{message}</p>}
          </div>
        )}

        {/* Вкладка: Все коды */}
        {tab === 'keys' && (
          <div>
            <h3>Все выданные коды</h3>
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead>
                <tr style={{background: '#f0f0f0'}}>
                  <th style={thStyle}>PIN</th>
                  <th style={thStyle}>Сотрудник</th>
                  <th style={thStyle}>Дверь</th>
                  <th style={thStyle}>Действует до</th>
                  <th style={thStyle}>Статус</th>
                  <th style={thStyle}>Действие</th>
                </tr>
              </thead>
              <tbody>
                {allKeys.map(key => (
                  <tr key={key.id}>
                    <td style={tdStyle}>{key.pin}</td>
                    <td style={tdStyle}>{key.userName}</td>
                    <td style={tdStyle}>{key.doorName}</td>
                    <td style={tdStyle}>{new Date(key.validUntil).toLocaleString('ru-RU')}</td>
                    <td style={tdStyle}>{key.status === 'active' ? '✅ Активен' : '❌ Отозван'}</td>
                    <td style={tdStyle}>
                      {key.status === 'active' && (
                        <button onClick={() => handleRevoke(key.id)}>Отозвать</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Вкладка: Статистика */}
        {tab === 'stats' && (
          <div>
            <h3>Статистика доступов</h3>
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead>
                <tr style={{background: '#f0f0f0'}}>
                  <th style={thStyle}>Помещение</th>
                  <th style={thStyle}>Активных кодов</th>
                </tr>
              </thead>
              <tbody>
                {statistics.map(stat => (
                  <tr key={stat.doorId}>
                    <td style={tdStyle}>{stat.doorName}</td>
                    <td style={tdStyle}>{stat.activeKeys}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </div>
  );
}

const thStyle = {border: '1px solid #ccc', padding: '8px', textAlign: 'left'};
const tdStyle = {border: '1px solid #ccc', padding: '8px'};

export default SecurityPage;