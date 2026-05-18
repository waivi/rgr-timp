import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function InsidePage() {
  const [doorInfo, setDoorInfo] = useState(null);
  const [pin, setPin] = useState('');
  const [timeInside, setTimeInside] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem('doorInfo');
    const savedPin = localStorage.getItem('doorPin');
    if (saved) {
      setDoorInfo(JSON.parse(saved));
    }
    if (savedPin) {
      setPin(savedPin);
    }
    if (!saved || !savedPin) {
      navigate('/door');
    }
  }, [navigate]);

  useEffect(() => {
    if (!doorInfo) return;
    const interval = setInterval(() => {
      const now = new Date();
      const entered = new Date(doorInfo.enteredAt);
      const diff = now - entered;
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      setTimeInside(`${hours}ч ${minutes}мин ${seconds}сек`);
    }, 1000);
    return () => clearInterval(interval);
  }, [doorInfo]);

  const handleExit = async () => {
    try {
      const res = await axios.post('http://localhost:5000/api/door/exit', { pin });
      if (res.data.success) {
        localStorage.removeItem('doorPin');
        localStorage.removeItem('doorInfo');
        navigate('/door');
      }
    } catch (err) {
      alert('Ошибка при выходе: ' + (err.response?.data?.message || 'Неизвестная ошибка'));
    }
  };

  if (!doorInfo) {
    return <div style={{ color: 'white', textAlign: 'center', padding: '50px' }}>Загрузка...</div>;
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f3460 0%, #16213e 100%)',
      color: 'white',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '20px'
    }}>
      <div style={{
        textAlign: 'center',
        background: '#1a1a2e',
        padding: '40px',
        borderRadius: '16px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        maxWidth: '450px',
        width: '100%'
      }}>
        <h1 style={{ fontSize: '64px', marginBottom: '20px' }}>🚪</h1>
        <h2>Вы внутри помещения</h2>
        
        <div style={{
          background: '#e94560',
          padding: '20px',
          borderRadius: '12px',
          marginTop: '20px',
          marginBottom: '20px'
        }}>
          <h3 style={{ margin: '0 0 10px 0' }}>{doorInfo.doorName}</h3>
          <p style={{ margin: '0', opacity: '0.8' }}>{doorInfo.doorLocation}</p>
        </div>

        <div style={{ marginBottom: '20px', fontSize: '14px', color: '#aaa' }}>
          <p>Вы: <strong style={{ color: 'white' }}>{doorInfo.userName}</strong></p>
          <p>Должность: {doorInfo.userPosition || '—'}</p>
        </div>

        <div style={{
          background: '#16213e',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '30px'
        }}>
          <p style={{ margin: '0', color: '#aaa', fontSize: '14px' }}>Время внутри:</p>
          <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
            {timeInside}
          </p>
        </div>

        <button
          onClick={handleExit}
          style={{
            width: '100%',
            padding: '16px',
            background: '#e94560',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '18px',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
        >
          Выйти из помещения
        </button>
      </div>
    </div>
  );
}

export default InsidePage;