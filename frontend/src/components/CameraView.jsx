import { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, AlertTriangle, Loader2 } from 'lucide-react';
import api from '../services/api';

const DETECTION_INTERVAL_MS = parseInt(import.meta.env.VITE_DETECTION_INTERVAL_MS) || 3000;
const MAX_DIMENSION = 1280;

export default function CameraView({ 
  setDetectionResponse, 
  detectionStatus, 
  setDetectionStatus,
  detectionErrorMsg,
  setDetectionErrorMsg
}) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);
  const requestInProgressRef = useRef(false);
  const [status, setStatus] = useState('loading'); // loading, granted, denied, unsupported, error
  const [errorMessage, setErrorMessage] = useState('');

  // 1. Camera Initialization Loop
  useEffect(() => {
    let active = true;

    async function startCamera() {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (active) {
          setStatus('unsupported');
          setErrorMessage('المتصفح لا يدعم الوصول إلى الكاميرا.');
        }
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }
        });
        
        if (active) {
          streamRef.current = stream;
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
          setStatus('granted');
        } else {
          stream.getTracks().forEach(track => track.stop());
        }
      } catch (err) {
        if (active) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            setStatus('denied');
            setErrorMessage('تم رفض الوصول إلى الكاميرا. يرجى منح الصلاحية من إعدادات المتصفح.');
          } else if (err.name === 'NotFoundError') {
            setStatus('error');
            setErrorMessage('لم يتم العثور على كاميرا في هذا الجهاز.');
          } else {
            setStatus('error');
            setErrorMessage('حدث خطأ أثناء محاولة تشغيل الكاميرا.');
          }
        }
      }
    }

    startCamera();

    return () => {
      active = false;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // Ensure video element gets the stream after mounting
  useEffect(() => {
    if (status === 'granted' && videoRef.current && streamRef.current) {
      if (videoRef.current.srcObject !== streamRef.current) {
        videoRef.current.srcObject = streamRef.current;
      }
    }
  }, [status]);

  // 2. Detection Capture Loop
  useEffect(() => {
    let intervalId;

    const captureAndAnalyze = async () => {
      // Prevent overlapping requests
      if (requestInProgressRef.current) return;
      // Only proceed if camera is active
      if (status !== 'granted' || !videoRef.current || !canvasRef.current) return;
      
      const video = videoRef.current;
      if (video.videoWidth === 0 || video.videoHeight === 0) return;

      requestInProgressRef.current = true;
      setDetectionStatus('analyzing');

      try {
        // Calculate scaling preserving aspect ratio
        let width = video.videoWidth;
        let height = video.videoHeight;

        if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
          if (width > height) {
            height = Math.round((height * MAX_DIMENSION) / width);
            width = MAX_DIMENSION;
          } else {
            width = Math.round((width * MAX_DIMENSION) / height);
            height = MAX_DIMENSION;
          }
        }

        const canvas = canvasRef.current;
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, width, height);

        // Convert to Blob asynchronously
        const blob = await new Promise((resolve) => {
          canvas.toBlob(resolve, 'image/jpeg', 0.8);
        });

        if (!blob) {
          throw new Error("Failed to generate image blob.");
        }

        const formData = new FormData();
        formData.append('image', blob, 'camera-frame.jpg');

        const response = await api.post('/api/detect', formData);
        
        if (response.data && response.data.success) {
          setDetectionResponse(response.data);
          setDetectionStatus('success');
        } else {
          throw new Error("Backend reported failure.");
        }
        
      } catch (err) {
        setDetectionStatus('error');
        if (err.response) {
           if (err.response.status === 400) {
             setDetectionErrorMsg('تعذر معالجة الصورة. الرجاء المحاولة مجدداً.');
           } else if (err.response.status === 413) {
             setDetectionErrorMsg('حجم الصورة كبير جداً.');
           } else if (err.response.status >= 500) {
             setDetectionErrorMsg('فشل تحليل الذكاء الاصطناعي مؤقتاً.');
           } else {
             setDetectionErrorMsg('حدث خطأ في الاتصال بالخادم.');
           }
        } else {
           setDetectionErrorMsg('تم قطع الاتصال بالخادم.');
        }
        console.error('Detection error:', err);
      } finally {
        requestInProgressRef.current = false;
      }
    };

    if (status === 'granted') {
       intervalId = setInterval(captureAndAnalyze, DETECTION_INTERVAL_MS);
    }

    return () => {
       if (intervalId) {
         clearInterval(intervalId);
       }
    };
  }, [status, setDetectionStatus, setDetectionResponse, setDetectionErrorMsg]);

  return (
    <section className="camera-container card-panel" aria-label="قسم الكاميرا">
      
      <div className="camera-header">
        {status === 'granted' ? <Camera size={20} /> : <CameraOff size={20} />}
        <h2>كاميرا البيئة المحيطة</h2>
      </div>

      {status === 'loading' && (
        <div className="camera-message" aria-live="polite">
          <Loader2 size={32} className="lucide-spin" />
          <p>جاري طلب الوصول إلى الكاميرا...</p>
        </div>
      )}

      {status === 'granted' && (
        <div style={{ position: 'relative', width: '100%' }}>
          <video
            ref={videoRef}
            className="camera-video"
            autoPlay
            playsInline
            muted
            aria-label="بث مباشر من كاميرا الجهاز الخلفية"
          ></video>
          {detectionStatus === 'error' && (
             <div style={{ position: 'absolute', bottom: '10px', left: '10px', right: '10px', background: 'rgba(197, 48, 48, 0.9)', color: 'white', padding: '0.5rem', borderRadius: '4px', textAlign: 'center', fontSize: '0.9rem' }}>
                {detectionErrorMsg}
             </div>
          )}
        </div>
      )}

      {(status === 'denied' || status === 'unsupported' || status === 'error') && (
        <div className="camera-message error" aria-live="assertive" role="alert">
          <AlertTriangle size={40} />
          <p>{errorMessage}</p>
        </div>
      )}

      {/* Hidden canvas for taking frame captures */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
    </section>
  );
}
