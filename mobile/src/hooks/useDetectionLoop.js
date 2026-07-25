import { useEffect, useRef, useCallback } from 'react';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import api from '../services/api';

export default function useDetectionLoop({ 
  cameraRef, 
  isActive, 
  setDetectionResponse, 
  setDetectionStatus, 
  setDetectionErrorMsg 
}) {
  const requestInProgressRef = useRef(false);
  const timeoutRef = useRef(null);

  // Interval in milliseconds (default to 3000ms if not provided in env)
  const intervalMs = process.env.EXPO_PUBLIC_DETECTION_INTERVAL_MS 
    ? parseInt(process.env.EXPO_PUBLIC_DETECTION_INTERVAL_MS, 10) 
    : 3000;

  const performDetection = useCallback(async () => {
    // Safety checks
    if (!isActive || !cameraRef?.current || requestInProgressRef.current) {
      return;
    }

    try {
      requestInProgressRef.current = true;
      setDetectionStatus('capturing');

      // 1. Capture Frame
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.5,
        skipProcessing: true,
        mute: true,
      });

      // 2. Resize and Compress Image (Reduce payload size for the CPU-only Backend)
      const manipResult = await manipulateAsync(
        photo.uri,
        [{ resize: { width: 640 } }], // Resize width to 640px (YOLO standard)
        { compress: 0.7, format: SaveFormat.JPEG }
      );

      setDetectionStatus('analyzing');

      // 3. Prepare FormData for API
      const formData = new FormData();
      formData.append('image', {
        uri: manipResult.uri,
        name: 'frame.jpg',
        type: 'image/jpeg',
      });

      // 4. Send to Backend
      const response = await api.post('/api/detect', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 5. Handle Response
      if (response.data && response.data.success) {
        setDetectionResponse(response.data);
        setDetectionStatus('success');
      } else {
        throw new Error(response.data?.error || 'Unknown server error');
      }

    } catch (err) {
      console.error('Detection error:', err);
      setDetectionStatus('error');
      setDetectionErrorMsg(err.message || 'فشل الاتصال بالخادم');
    } finally {
      requestInProgressRef.current = false;
      
      // Schedule the next cycle only if we are still active
      if (isActive) {
        timeoutRef.current = setTimeout(performDetection, intervalMs);
      }
    }
  }, [isActive, cameraRef, intervalMs, setDetectionResponse, setDetectionStatus, setDetectionErrorMsg]);

  useEffect(() => {
    if (isActive) {
      // Start the loop
      performDetection();
    } else {
      // Clean up if inactive
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      setDetectionStatus('idle');
      requestInProgressRef.current = false;
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isActive, performDetection]);
}
