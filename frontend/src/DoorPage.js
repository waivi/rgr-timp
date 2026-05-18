import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function DoorPage() {
  const [doors, setDoors] = useState([]);
  const [selectedDoorId, setSelectedDoorId] = useState('');
  const [pin, setPin] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadDoors();
  }, []);

  const loadDoors = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/doors');
      setDoors(res.data.filter(d => d.isActive));
    } catch (err) {
      console.error('Ошибка загрузки дверей:', err);
    }
  };

  const handleEnter = async (e) => {
    e.preventDefault();
    setMessage('');
    setMessageType('');

    if (!selectedDoorId) {
      setMessage('Выберите помещение');
      setMessageType('error');
      return;
    }

    if (pin.length !== 4 || !/^\d+$/.test(pin)) {
      setMessage('Введите ровно 4 цифры');
      setMessageType('error');
      return;
    }

    try {
      const res = await axios.post('http://localhost:5000/api/door/enter', { 
        pin,
        doorId: parseInt(selectedDoorId)
      });
      if (res.data.success) {
        localStorage.setItem('doorPin', pin);
        localStorage.setItem('doorInfo', JSON.stringify(res.data.session));
        navigate('/inside');
      }
    } catch (err) {
      if (err.response && err.response.data) {
        setMessage(err.response.data.message);
      } else {
        setMessage('Ошибка соединения с сервером');
      }
      setMessageType('error');
    }
  };

  const selectedDoor = doors.find(d => d.id === parseInt(selectedDoorId));

  return (
    <div style={{ minHeight: '100vh', background: '#1a1a2e', color: 'white', padding: '20px' }}>
      <div style={{ textAlign: 'center', paddingTop: '40px' }}>
        <h1 style={{ fontSize: '48px', marginBottom: '10px' }}>🚪</h1>
        <h2>Доступ в техническое помещение</h2>
        <p style={{ color: '#aaa' }}>Выберите помещение и введите PIN-код</p>
      </div>

      <div style={{ maxWidth: '400px', margin: '30px auto' }}>
        <form onSubmit={handleEnter}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>Помещение:</label>
            <select
              value={selectedDoorId}
              onChange={(e) => setSelectedDoorId(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                fontSize: '16px',
                borderRadius: '8px',
                border: '2px solid #e94560',
                background: '#16213e',
                color: 'white',
                boxSizing: 'border-box'
              }}
            >
              <option value="">— Выберите помещение —</option>
              {doors.map(door => (
                <option key={door.id} value={door.id}>
                  {door.name} ({door.location})
                </option>
              ))}
            </select>
          </div>

          {selectedDoor && (
            <div style={{
              background: '#16213e',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px'
            }}>
              <p style={{ margin: '0 0 5px 0' }}><strong>{selectedDoor.name}</strong></p>
              <p style={{ margin: '0 0 5px 0', color: '#aaa', fontSize: '14px' }}>{selectedDoor.location}</p>
              <p style={{ margin: '0', color: '#aaa', fontSize: '14px' }}>
                Категория: {selectedDoor.category} | Этаж: {selectedDoor.floor}
              </p>
            </div>
          )}

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>PIN-код:</label>
            <input
              type="text"
              value={pin}
              onChange={(e) => {
                const val = e.target.value.replace(/[^0-9]/g, '');
                if (val.length <= 4) setPin(val);
              }}
              placeholder="Введите 4-значный PIN"
              maxLength={4}
              style={{
                width: '100%',
                padding: '16px',
                fontSize: '32px',
                textAlign: 'center',
                letterSpacing: '20px',
                borderRadius: '8px',
                border: '2px solid #e94560',
                background: '#16213e',
                color: 'white',
                boxSizing: 'border-box'
              }}
              autoFocus
            />
          </div>

          <button
            type="submit"
            style={{
              width: '100%',
              marginTop: '10px',
              padding: '14px',
              background: '#e94560',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '18px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            Войти в помещение
          </button>
        </form>

        {message && (
          <div style={{
            marginTop: '20px',
            padding: '15px',
            borderRadius: '8px',
            background: messageType === 'error' ? '#ff4d4f' : '#52c41a',
            color: 'white',
            textAlign: 'center',
            fontWeight: 'bold',
            fontSize: '16px'
          }}>
            {message}
          </div>
        )}
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <a href="/" style={{ color: '#aaa', textDecoration: 'none' }}>← Вернуться ко входу</a>
      </div>
    </div>
  );
}

export default DoorPage;