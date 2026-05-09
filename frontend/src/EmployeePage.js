import React, { useState, useEffect } from 'react';
import axios from 'axios';

function EmployeePage({ user, onLogout }) {
  const [keys, setKeys] = useState([]);

  useEffect(() => {
    loadKeys();
    const interval = setInterval(loadKeys, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadKeys = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/employee/${user.id}/keys`);
      setKeys(response.data);
    } catch (err) {
      console.error('Ошибка загрузки ключей:', err);
    }
  };

  const getTimeLeft = (validUntil) => {
    const now = new Date();
    const end = new Date(validUntil);
    const diff = end - now;

    if (diff <= 0) return 'Истёк';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}ч ${minutes}мин`;
  };

  const getStatusColor = (validUntil) => {
    const now = new Date();
    const end = new Date(validUntil);
    const diff = end - now;

    if (diff <= 0) return '#ff4d4f';
    if (diff < 30 * 60 * 1000) return '#faad14';
    return '#52c41a';
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 20px', background: '#52c41a', color: 'white' }}>
        <h2>Мои доступы</h2>
        <div>
          <span style={{ marginRight: '20px' }}>
            {user.name} {user.position && `(${user.position})`}
          </span>
          <button onClick={onLogout} style={{ background: '#fff', color: '#52c41a' }}>Выйти</button>
        </div>
      </div>

      <div style={{ padding: '20px' }}>
        {keys.length === 0 ? (
          <p>У вас нет активных кодов доступа.</p>
        ) : (
          keys.map(key => (
            <div key={key.id} style={{
              border: '2px solid #d9d9d9',
              borderRadius: '8px',
              padding: '20px',
              marginBottom: '15px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '48px', fontWeight: 'bold', letterSpacing: '10px', marginBottom: '10px' }}>
                {key.pin}
              </div>
              <div style={{ fontSize: '18px', marginBottom: '5px' }}>
                Дверь: <strong>{key.doorName}</strong>
              </div>
              <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
                {key.doorLocation}
              </div>
              <div style={{
                fontSize: '16px',
                color: getStatusColor(key.validUntil),
                fontWeight: 'bold'
              }}>
                Действует ещё: {getTimeLeft(key.validUntil)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default EmployeePage;