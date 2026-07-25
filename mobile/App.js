import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, I18nManager } from 'react-native';
import { SafeAreaView, SafeAreaProvider } from 'react-native-safe-area-context';
import { Navigation } from 'lucide-react-native';
import CameraScreen from './src/components/CameraScreen';
import GuidancePanel from './src/components/GuidancePanel';
import StatusBar from './src/components/StatusBar';
import useSpeech from './src/hooks/useSpeech';
import { theme } from './src/styles/theme';

// Force RTL layout for Arabic
if (!I18nManager.isRTL) {
  I18nManager.allowRTL(true);
  I18nManager.forceRTL(true);
}

export default function App() {
  const [detectionResponse, setDetectionResponse] = useState(null);
  const [detectionStatus, setDetectionStatus] = useState('idle');
  const [detectionErrorMsg, setDetectionErrorMsg] = useState('');
  
  // Voice state
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [detectionMode, setDetectionMode] = useState('online'); // 'online' | 'offline'
  const [isCameraActive, setIsCameraActive] = useState(true);
  const lastSpokenTextRef = useRef('');
  
  const { isSpeaking, arabicAvailable, speak, cancel } = useSpeech();

  // Handle Voice Toggle
  const toggleVoice = () => {
    const newState = !voiceEnabled;
    setVoiceEnabled(newState);
    if (!newState) {
      cancel();
      lastSpokenTextRef.current = '';
    }
  };

  // Handle Mode Toggle
  const toggleMode = () => {
    setDetectionMode(prev => prev === 'online' ? 'offline' : 'online');
  };

  // TTS queue: holds the next text to speak after current speech ends
  const pendingTextRef = useRef('');

  // Speak next pending text when current speech finishes
  const speakNext = useCallback((text) => {
    if (!text) return;
    speak(text);
    pendingTextRef.current = '';
    lastSpokenTextRef.current = text;
  }, [speak]);

  // Trigger next queued text when speech stops
  useEffect(() => {
    if (!isSpeaking && pendingTextRef.current) {
      speakNext(pendingTextRef.current);
    }
  }, [isSpeaking, speakNext]);

  // TTS Triggers on new Guidance
  useEffect(() => {
    if (!voiceEnabled) return;
    
    if (detectionStatus !== 'success' || !detectionResponse?.guidance?.summary) {
       return;
    }

    const rawSummary = detectionResponse.guidance.summary;
    const normalizedSummary = rawSummary.trim().replace(/\s+/g, ' ');

    if (!normalizedSummary) return;

    // Skip if the same text as last spoken or currently queued
    if (normalizedSummary === lastSpokenTextRef.current) return;
    if (normalizedSummary === pendingTextRef.current) return;

    if (isSpeaking) {
      // TTS is busy → queue the new text (overwrite old pending)
      pendingTextRef.current = normalizedSummary;
    } else {
      // TTS is free → speak immediately
      speakNext(normalizedSummary);
    }

  }, [detectionResponse, detectionStatus, voiceEnabled, speakNext, isSpeaking]);

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <View style={styles.header} accessible={true} accessibilityRole="header">
          <View style={styles.titleContainer}>
            <Navigation size={28} color={theme.colors.surface} />
            <Text style={styles.title}>مساعد الإرشاد المكاني</Text>
          </View>
          <Text style={styles.description}>
            تطبيق صمم لمساعدة المكفوفين وضعاف البصر على إدراك البيئة المحيطة.
          </Text>
        </View>

        <View style={styles.modeContainer}>
          <Text style={styles.modeText}>الوضع الحالي:</Text>
          <TouchableOpacity 
            style={[styles.modeButton, detectionMode === 'online' ? styles.modeButtonOnline : styles.modeButtonOffline]}
            onPress={toggleMode}
          >
            <Text style={styles.modeButtonText}>
              {detectionMode === 'online' ? '🌐 متصل (سريع/دقيق)' : '📵 محلي (بدون نت)'}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.cameraContainer}>
          <CameraScreen 
            isActive={isCameraActive} 
            onToggle={() => setIsCameraActive(!isCameraActive)}
            detectionMode={detectionMode}
            setDetectionResponse={setDetectionResponse} 
            detectionStatus={detectionStatus}
            setDetectionStatus={setDetectionStatus}
            detectionErrorMsg={detectionErrorMsg}
            setDetectionErrorMsg={setDetectionErrorMsg}
          />
        </View>
        <GuidancePanel 
          detectionResponse={detectionResponse} 
          detectionStatus={detectionStatus} 
          voiceEnabled={voiceEnabled}
          toggleVoice={toggleVoice}
          isSpeaking={isSpeaking}
          arabicAvailable={arabicAvailable}
        />

        <StatusBar />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    backgroundColor: theme.colors.primary,
    padding: theme.spacing.lg,
    paddingTop: theme.spacing.xl,
    borderBottomLeftRadius: theme.borderRadius.lg,
    borderBottomRightRadius: theme.borderRadius.lg,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    zIndex: 10,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: theme.spacing.sm,
  },
  title: {
    ...theme.typography.h1,
    color: theme.colors.surface,
  },
  description: {
    ...theme.typography.caption,
    color: '#d1fae5',
    fontSize: 16,
  },
  modeContainer: {
    flexDirection: 'row-reverse',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: theme.spacing.sm,
    paddingHorizontal: theme.spacing.md,
    gap: 10,
  },
  modeText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  modeButton: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
  },
  modeButtonOnline: {
    backgroundColor: '#3b82f6',
  },
  modeButtonOffline: {
    backgroundColor: '#10b981',
  },
  modeButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 13,
  },
  cameraContainer: {
    flex: 1,
  },
});
