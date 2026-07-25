import { useEffect, useRef, useCallback } from 'react';
import { manipulateAsync, SaveFormat } from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import { Buffer } from 'buffer';
import jpeg from 'jpeg-js';
import { useTensorflowModel } from 'react-native-fast-tflite';
import { yoloPostProcess } from '../utils/yoloPostProcess';
import { spatialAnalyzer } from '../utils/spatialAnalyzer';
import { generateGuidance } from '../utils/guidanceGenerator';

export default function useOnDeviceDetection({ 
  cameraRef, 
  isActive, 
  setDetectionResponse, 
  setDetectionStatus, 
  setDetectionErrorMsg 
}) {
  const requestInProgressRef = useRef(false);
  const intervalRef = useRef(null);
  const actualModelRef = useRef(null);

  // Load the TFLite model from assets
  const model = useTensorflowModel(require('../../assets/models/best.tflite'));

  // Sync model ref without triggering detection loop re-creation
  useEffect(() => {
    actualModelRef.current = model.state === 'loaded' ? model.model : null;
  }, [model.state, model.model]);

  const intervalMs = parseInt(process.env.EXPO_PUBLIC_DETECTION_INTERVAL_MS || '5000', 10);

  const performDetection = useCallback(async () => {
    if (!isActive || !cameraRef?.current || requestInProgressRef.current) return;

    const actualModel = actualModelRef.current;

    // Show model state once — no spam
    if (!actualModel) {
      if (model.state === 'loading') {
        setDetectionStatus('analyzing');
        setDetectionErrorMsg('جاري تحميل نموذج الذكاء الاصطناعي...');
      } else if (model.state === 'error') {
        setDetectionStatus('error');
        setDetectionErrorMsg('فشل تحميل النموذج المحلي');
      }
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

      setDetectionStatus('analyzing');

      // 2. Resize image to 640x640
      const manipResult = await manipulateAsync(
        photo.uri,
        [{ resize: { width: 640, height: 640 } }],
        { compress: 1, format: SaveFormat.JPEG }
      );

      // 3. Decode JPEG to raw RGB pixels
      const base64Data = await FileSystem.readAsStringAsync(manipResult.uri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      const imgBuffer = Buffer.from(base64Data, 'base64');
      const rawImageData = jpeg.decode(imgBuffer, { useTArray: true }); // returns Uint8Array RGBA

      // YOLOv8 TFLite Float32 requires normalized [0, 1] RGB
      const numPixels = 640 * 640;
      const rgbFloatArray = new Float32Array(numPixels * 3);
      for (let i = 0; i < numPixels; i++) {
        rgbFloatArray[i * 3] = rawImageData.data[i * 4] / 255.0;       // R
        rgbFloatArray[i * 3 + 1] = rawImageData.data[i * 4 + 1] / 255.0; // G
        rgbFloatArray[i * 3 + 2] = rawImageData.data[i * 4 + 2] / 255.0; // B
      }

      // 4. Run inference
      const outputTensors = await actualModel.run([rgbFloatArray]);
      const outputTensor = new Float32Array(outputTensors[0]);


      // 5. Post-process
      const detections = yoloPostProcess(outputTensor, 640, 640);
      const analyzedDetections = spatialAnalyzer(detections, 640, 640);
      const guidance = generateGuidance(analyzedDetections);

      setDetectionResponse({
        success: true,
        source: 'offline',
        detections: analyzedDetections,
        guidance: guidance
      });
      setDetectionStatus('success');

    } catch (err) {
      console.log('Offline Detection error:', err.message);
      
      // Ignore common camera warmup errors to avoid flashing errors on UI
      if (!err.message.includes('not ready') && !err.message.includes('camera')) {
        setDetectionStatus('error');
        setDetectionErrorMsg(err.message || 'فشل التحليل المحلي');
      } else {
        // Just reset to idle silently if it's a camera hiccup
        setDetectionStatus('idle');
      }
    } finally {
      requestInProgressRef.current = false;
      
      // Schedule the next detection securely
      if (isActive && intervalRef.current !== false) {
        intervalRef.current = setTimeout(performDetection, intervalMs);
      }
    }
  }, [isActive, cameraRef, setDetectionResponse, setDetectionStatus, setDetectionErrorMsg, model.state, intervalMs]);

  useEffect(() => {
    // intervalRef is used as both a flag and a timer ID
    if (!isActive) {
      if (intervalRef.current) clearTimeout(intervalRef.current);
      intervalRef.current = false; // Mark as stopped
      setDetectionStatus('idle');
      requestInProgressRef.current = false;
      return;
    }

    // Start loop
    if (intervalRef.current === false || intervalRef.current === null) {
      intervalRef.current = setTimeout(performDetection, 500); // initial delay
    }

    return () => {
      if (intervalRef.current) clearTimeout(intervalRef.current);
      intervalRef.current = false;
    };
  }, [isActive, performDetection]);
}
