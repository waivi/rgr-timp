import React, { useState, useEffect } from 'react';
import axios from 'axios';

function AdminPage({ user, onLogout }) {
  const [tab, setTab] = useState('users');
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [positions, setPositions] = useState([]);
  const [roles, setRoles] = useState([]);
  const [message, setMessage] = useState('');

  // Форма создания пользователя
  const [newUser, setNewUser] = useState({
    login: '', password: '', lastName: '', firstName: '',
    middleName: '', roleId: '', positionId: '', phone: ''
  });

  useEffect(() => {
    loadUsers();
    loadPositions();
    loadRoles();
  }, []);

  const loadUsers = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/users');
    setUsers(res.data);
  };

  const loadLogs = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/logs');
    setLogs(res.data);
  };

  const loadStats = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/statistics');
    setStats(res.data);
  };

  const loadPositions = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/positions');
    setPositions(res.data);
  };

  const loadRoles = async () => {
    const res = await axios.get('http://localhost:5000/api/admin/roles');
    setRoles(res.data);
  };

  const handleTabClick = (tabName) => {
    setTab(tabName);
    setMessage('');
    if (tabName === 'logs') loadLogs();
    if (tabName === 'stats') loadStats();
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const res = await axios.post('http://localhost:5000/api/admin/users', {
        login: newUser.login,
        password: newUser.password,
        lastName: newUser.lastName,
        firstName: newUser.firstName,
        middleName: newUser.middleName,
        roleId: parseInt(newUser.roleId),
        positionId: newUser.positionId ? parseInt(newUser.positionId) : null,
        phone: newUser.phone,
        createdBy: user.id
      });
      if (res.data.success) {
        setMessage(`✅ Пользователь "${res.data.user.login}" создан`);
        loadUsers();
        setNewUser({ login: '', password: '', lastName: '', firstName: '',
                     middleName: '', roleId: '', positionId: '', phone: '' });
      }
    } catch (err) {
      setMessage('❌ Ошибка при создании пользователя');
    }
  };

  const handleBlockUser = async (userId, isActive) => {
    const action = isActive ? 'заблокировать' : 'разблокировать';
    if (!window.confirm(`Вы уверены что хотите ${action} пользователя?`)) return;

    await axios.put(`http://localhost:5000/api/admin/users/${userId}`, {
      isActive: !isActive,
      updatedBy: user.id
    });
    loadUsers();
  };

  const getRoleDisplay = (roleName) => {
    switch (roleName) {
      case 'администратор': return '👑 Администратор';
      case 'менеджер безопасности': return '🛡️ Менеджер безопасности';
      case 'сотрудник': return '👤 Сотрудник';
      default: return roleName;
    }
  };

  return (
    <div>
      {/* Шапка */}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#722ed1', color: 'white' }}>
        <h2>Панель администратора</h2>
        <div>
          <span style={{ marginRight: '20px' }}>{user.name}</span>
          <button onClick={onLogout} style={{ background: '#fff', color: '#722ed1', padding: '6px 16px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Выйти</button>
        </div>
      </div>

      {/* Вкладки */}
      <div style={{ display: 'flex', gap: '10px', padding: '10px 20px', background: '#f0f0f0' }}>
        {[
          { key: 'users', label: 'Пользователи' },
          { key: 'create', label: 'Создать пользователя' },
          { key: 'stats', label: 'Статистика' },
          { key: 'logs', label: 'Журнал действий' }
        ].map(t => (
          <button key={t.key} onClick={() => handleTabClick(t.key)}
            style={tabBtnStyle(tab === t.key, '#722ed1')}>
            {t.label}
          </button>
        ))}
      </div>

      <div style={{ padding: '20px' }}>

        {/* Вкладка: Пользователи */}
        {tab === 'users' && (
          <div>
            <h3>Все пользователи</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead><tr style={{ background: '#f0f0f0' }}>
                  <th style={thStyle}>ID</th>
                  <th style={thStyle}>ФИО</th>
                  <th style={thStyle}>Логин</th>
                  <th style={thStyle}>Роль</th>
                  <th style={thStyle}>Должность</th>
                  <th style={thStyle}>Телефон</th>
                  <th style={thStyle}>Активен</th>
                  <th style={thStyle}>Действие</th>
                </tr></thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td style={tdStyle}>{u.id}</td>
                      <td style={tdStyle}>{u.fullName}</td>
                      <td style={tdStyle}>{u.login}</td>
                      <td style={tdStyle}>{getRoleDisplay(u.roleName)}</td>
                      <td style={tdStyle}>{u.positionName || '—'}</td>
                      <td style={tdStyle}>{u.phone}</td>
                      <td style={tdStyle}>{u.isActive ? '✅' : '❌'}</td>
                      <td style={tdStyle}>
                        {u.login !== 'system' && (
                          <button onClick={() => handleBlockUser(u.id, u.isActive)}
                            style={{
                              background: u.isActive ? '#ff4d4f' : '#52c41a',
                              color: '#fff', border: 'none',
                              padding: '4px 12px', borderRadius: '4px', cursor: 'pointer'
                            }}>
                            {u.isActive ? 'Заблокировать' : 'Разблокировать'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Вкладка: Создать пользователя */}
        {tab === 'create' && (
          <div>
            <h3>Создать нового пользователя</h3>
            <form onSubmit={handleCreateUser}>
              <div style={formRow}>
                <label>Логин *: <input value={newUser.login} onChange={e => setNewUser({ ...newUser, login: e.target.value })} required /></label>
                <label>Пароль *: <input type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required /></label>
              </div>
              <div style={formRow}>
                <label>Фамилия *: <input value={newUser.lastName} onChange={e => setNewUser({ ...newUser, lastName: e.target.value })} required /></label>
                <label>Имя *: <input value={newUser.firstName} onChange={e => setNewUser({ ...newUser, firstName: e.target.value })} required /></label>
                <label>Отчество: <input value={newUser.middleName} onChange={e => setNewUser({ ...newUser, middleName: e.target.value })} /></label>
              </div>
              <div style={formRow}>
                <label>Роль *:
                  <select value={newUser.roleId} onChange={e => setNewUser({ ...newUser, roleId: e.target.value })} required>
                    <option value="">Выберите</option>
                    {roles.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
                  </select>
                </label>
                <label>Должность:
                  <select value={newUser.positionId} onChange={e => setNewUser({ ...newUser, positionId: e.target.value })}>
                    <option value="">Без должности</option>
                    {positions.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                  </select>
                </label>
                <label>Телефон: <input value={newUser.phone} onChange={e => setNewUser({ ...newUser, phone: e.target.value })} placeholder="+79000000000" /></label>
              </div>
              <button type="submit" style={{ background: '#722ed1', color: '#fff', padding: '10px 24px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Создать</button>
            </form>
            {message && <p style={{ marginTop: '15px', fontWeight: 'bold' }}>{message}</p>}
          </div>
        )}

        {/* Вкладка: Статистика */}
        {tab === 'stats' && stats && (
          <div>
            <h3>Общая статистика системы</h3>
            <div style={{ display: 'flex', gap: '20px', marginTop: '20px', flexWrap: 'wrap' }}>
              <div style={statCard}>
                <h2>{stats.totalUsers}</h2>
                <p>Активных пользователей</p>
              </div>
              <div style={statCard}>
                <h2>{stats.totalActiveKeys}</h2>
                <p>Активных ключей</p>
              </div>
              <div style={statCard}>
                <h2>{stats.totalKeysToday}</h2>
                <p>Выдано сегодня</p>
              </div>
            </div>
          </div>
        )}

        {/* Вкладка: Логи */}
        {tab === 'logs' && (
          <div>
            <h3>Журнал действий (последние 500)</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={tableStyle}>
                <thead><tr style={{ background: '#f0f0f0' }}>
                  <th style={thStyle}>Время</th>
                  <th style={thStyle}>Пользователь</th>
                  <th style={thStyle}>Действие</th>
                  <th style={thStyle}>Сущность</th>
                  <th style={thStyle}>Детали</th>
                  <th style={thStyle}>IP</th>
                </tr></thead>
                <tbody>
                  {logs.map(log => (
                    <tr key={log.id}>
                      <td style={tdStyle}>{new Date(log.createdAt).toLocaleString('ru-RU')}</td>
                      <td style={tdStyle}>{log.userName}</td>
                      <td style={tdStyle}>{log.action}</td>
                      <td style={tdStyle}>{log.entityType} #{log.entityId}</td>
                      <td style={{ ...tdStyle, maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{log.details}</td>
                      <td style={tdStyle}>{log.ipAddress}</td>
                    </tr>
                  ))}
                  {logs.length === 0 && (
                    <tr><td colSpan="6" style={{ ...tdStyle, textAlign: 'center' }}>Логов пока нет</td></tr>
                  )}
                </tbody>
              </table>
            </div>
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

const tableStyle = { width: '100%', borderCollapse: 'collapse', marginTop: '10px' };
const thStyle = { border: '1px solid #ccc', padding: '8px', textAlign: 'left', background: '#f0f0f0' };
const tdStyle = { border: '1px solid #ccc', padding: '8px' };
const formRow = { display: 'flex', gap: '15px', marginBottom: '15px', flexWrap: 'wrap' };
const statCard = {
  border: '2px solid #722ed1', borderRadius: '8px', padding: '20px 30px',
  textAlign: 'center', minWidth: '150px', background: '#fafafa'
};

export default AdminPage;