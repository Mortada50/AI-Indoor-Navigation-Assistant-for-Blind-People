import { useState, useEffect } from 'react';
import { Server, CircleCheck, CircleX, RefreshCw } from 'lucide-react';
import api from '../services/api';

export default function StatusBar() {
  const [backendStatus, setBackendStatus] = useState('loading'); // 'loading', 'connected', 'error'

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      if (active && backendStatus !== 'loading' && backendStatus !== 'connected') {
         setBackendStatus('loading');
      }
      try {
        const response = await api.get('/api/health');
        if (response.status === 200 && active) {
          setBackendStatus('connected');
        } else if (active) {
          setBackendStatus('error');
        }
      } catch (err) {
        if (active) {
          setBackendStatus('error');
        }
      }
    }

    // Initial check
    checkHealth();

    // Poll every 10 seconds for backend health
    const intervalId = setInterval(checkHealth, 10000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  let backendLabel = 'جاري الاتصال...';
  let StatusIcon = RefreshCw;
  
  if (backendStatus === 'connected') {
    backendLabel = 'الخادم متصل';
    StatusIcon = CircleCheck;
  }
  if (backendStatus === 'error') {
    backendLabel = 'تعذر الاتصال بالخادم';
    StatusIcon = CircleX;
  }

  return (
    <footer className="status-bar" aria-label="شريط حالة النظام">
      <div 
        className={`status-item ${backendStatus}`} 
        aria-label={`حالة الخادم: ${backendLabel}`}
      >
        <StatusIcon 
          size={18} 
          aria-hidden="true" 
          className={backendStatus === 'loading' ? 'lucide-spin' : ''} 
        />
        <span>{backendLabel}</span>
      </div>
      <div className="status-item">
        <Server size={18} aria-hidden="true" />
        <span>الإرشاد الذكي</span>
      </div>
    </footer>
  );
}
