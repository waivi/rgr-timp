import React, { useState, useEffect } from 'react';
import axios from 'axios';

function SecurityPage({ user, onLogout }) {
  const [tab, setTab] = useState('generate');
  const [users, setUsers] = useState([]);
  const [doors, setDoors] = useState([]);
  const [allKeys, setAllKeys] = useState([]);
  const [statistics, setStatistics] = useState([]);

  const [selectedUser, setSelectedUser] = useState('');
  const [selectedDoor, setSelectedDoor] = useState('');
  const [hours, setHours] = useState(2);
  const [message, setMessage] = useState('');

  const token = localStorage.getItem('token');
  const headers = { 'Authorization': `Bearer ${token}` };

  useEffect(() => {
    loadUsers();
    loadDoors();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadUsers = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/security/users', { headers });
      setUsers(res.data);
    } catch (err) {
      if (err.response && err.response.status === 401) { localStorage.removeItem('token'); onLogout(); }
    }
  };

  const loadDoors = async () => {
    const res = await axios.get('http://localhost:5000/api/doors');
    setDoors(res.data);
  };

  const loadKeys = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/security/keys', { headers });
      setAllKeys(res.data);
    } catch (err) {
      if (err.response && err.response.status === 401) { localStorage.removeItem('token'); onLogout(); }
    }
  };

  const loadStatistics = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/security/statistics', { headers });
      setStatistics(res.data);
    } catch (err) {
      if (err.response && err.response.status === 401) { localStorage.removeItem('token'); onLogout(); }
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setMessage('');

    try {
      const res = await axios.post('http://localhost:5000/api/security/keys/generate', {
        userId: parseInt(selectedUser),
        doorId: parseInt(selectedDoor),
        hours: hours
      }, { headers });

      if (res.data.success) {
        setMessage(`Код ${res.data.key.pin} создан для ${res.data.key.userName}`);
        setSelectedUser('');
        setSelectedDoor('');
        setHours(2);
      }
    } catch (err) {
      if (err.response && err.response.status === 401) { localStorage.removeItem('token'); onLogout(); }
      else setMessage('Ошибка при создании кода');
    }
  };

  const handleRevoke = async (keyId) => {
    if (!window.confirm('Вы уверены что хотите отозвать ключ?')) return;
    try {
      await axios.post(`http://localhost:5000/api/security/keys/${keyId}/revoke`, {}, { headers });
      loadKeys();
    } catch (err) {
      if (err.response && err.response.status === 401) { localStorage.removeItem('token'); onLogout(); }
    }
  };

  const handleTabClick = (tabName) => {
    setTab(tabName);
    setMessage('');
    if (tabName === 'keys') loadKeys();
    if (tabName === 'stats') loadStatistics();
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return '✅ Активен';
      case 'expired': return '⏰ Истёк';
      case 'revoked': return '❌ Отозван';
      default: return status;
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#1890ff', color: 'white' }}>
        <h2>Панель безопасности</h2>
        <div>
          <span style={{ marginRight: '20px' }}>{user.name}</span>
          <button onClick={onLogout} style={{ background: '#fff', color: '#1890ff' }}>Выйти</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', padding: '10px 20px', background: '#e0e0e0' }}>
        <button onClick={() => handleTabClick('generate')}
          style={tabBtnStyle(tab === 'generate', '#1890ff')}>Создать код</button>
        <button onClick={() => handleTabClick('keys')}
          style={tabBtnStyle(tab === 'keys', '#1890ff')}>Все коды</button>
        <button onClick={() => handleTabClick('stats')}
          style={tabBtnStyle(tab === 'stats', '#1890ff')}>Статистика</button>
      </div>

      <div style={{ padding: '20px' }}>

        {tab === 'generate' && (
          <div>
            <h3>Создать новый код доступа</h3>
            <form onSubmit={handleGenerate}>
              <div style={formGroup}>
                <label>Сотрудник: </label>
                <select value={selectedUser} onChange={(e) => setSelectedUser(e.target.value)} required>
                  <option value="">Выберите сотрудника</option>
                  {users.map(u => (
                    <option key={u.id} value={u.id}>{u.fullName} ({u.positionName || 'без должности'})</option>
                  ))}
                </select>
              </div>
              <div style={formGroup}>
                <label>Дверь: </label>
                <select value={selectedDoor} onChange={(e) => setSelectedDoor(e.target.value)} required>
                  <option value="">Выберите дверь</option>
                  {doors.map(d => (
                    <option key={d.id} value={d.id}>{d.name} ({d.location})</option>
                  ))}
                </select>
              </div>
              <div style={formGroup}>
                <label>На сколько часов: </label>
                <input type="number" value={hours} onChange={(e) => setHours(parseInt(e.target.value))} min="1" max="24" />
              </div>
              <button type="submit" style={{ background: '#1890ff', color: '#fff', padding: '10px 24px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Создать</button>
            </form>
            {message && <p style={{ marginTop: '10px', fontWeight: 'bold', color: '#1890ff' }}>{message}</p>}
          </div>
        )}

        {tab === 'keys' && (
          <div>
            <h3>Все выданные коды</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: '#f0f0f0' }}>
                    <th style={thStyle}>PIN</th><th style={thStyle}>Сотрудник</th>
                    <th style={thStyle}>Должность</th><th style={thStyle}>Дверь</th>
                    <th style={thStyle}>Действует до</th><th style={thStyle}>Статус</th>
                    <th style={thStyle}>Выдал</th><th style={thStyle}>Действие</th>
                  </tr>
                </thead>
                <tbody>
                  {allKeys.map(key => (
                    <tr key={key.id}>
                      <td style={{ ...tdStyle, fontWeight: 'bold', fontSize: '18px', letterSpacing: '4px' }}>{key.pin}</td>
                      <td style={tdStyle}>{key.userName}</td>
                      <td style={tdStyle}>{key.userPosition || '—'}</td>
                      <td style={tdStyle}>{key.doorName}</td>
                      <td style={tdStyle}>{new Date(key.validUntil).toLocaleString('ru-RU')}</td>
                      <td style={tdStyle}>{getStatusBadge(key.status)}</td>
                      <td style={tdStyle}>{key.issuedByName}</td>
                      <td style={tdStyle}>
                        {key.status === 'active' && (
                          <button onClick={() => handleRevoke(key.id)}
                            style={{ background: '#ff4d4f', color: '#fff', border: 'none', padding: '4px 12px', borderRadius: '4px', cursor: 'pointer' }}>
                            Отозвать
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {allKeys.length === 0 && (
                    <tr><td colSpan="8" style={{ ...tdStyle, textAlign: 'center' }}>Нет выданных кодов</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {tab === 'stats' && (
          <div>
            <h3>Статистика доступов</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f0f0f0' }}>
                  <th style={thStyle}>Помещение</th><th style={thStyle}>Категория</th><th style={thStyle}>Активных кодов</th>
                </tr>
              </thead>
              <tbody>
                {statistics.map(stat => (
                  <tr key={stat.doorId}>
                    <td style={tdStyle}>{stat.doorName}</td>
                    <td style={tdStyle}>{stat.doorCategory}</td>
                    <td style={{ ...tdStyle, fontWeight: 'bold', textAlign: 'center' }}>{stat.activeKeys}</td>
                  </tr>
                ))}
                {statistics.length === 0 && (
                  <tr><td colSpan="3" style={{ ...tdStyle, textAlign: 'center' }}>Нет данных</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}

      </div>
    </div>
  );
}

const tabBtnStyle = (active, color) => ({
  padding: '8px 16px',
  background: active ? color : '#fff',
  color: active ? '#fff' : '#000',
  border: `1px solid ${color}`,
  borderRadius: '4px',
  cursor: 'pointer',
  fontWeight: active ? 'bold' : 'normal'
});

const formGroup = { marginBottom: '15px' };
const thStyle = { border: '1px solid #ccc', padding: '8px', textAlign: 'left' };
const tdStyle = { border: '1px solid #ccc', padding: '8px' };

export default SecurityPage;