import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, SafeAreaView, I18nManager } from 'react-native';
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

  // TTS Triggers on new Guidance
  useEffect(() => {
    if (!voiceEnabled) return;
    
    if (detectionStatus !== 'success' || !detectionResponse?.guidance?.summary) {
       return;
    }

    const rawSummary = detectionResponse.guidance.summary;
    const normalizedSummary = rawSummary.trim().replace(/\s+/g, ' ');

    if (!normalizedSummary) return;

    if (normalizedSummary !== lastSpokenTextRef.current) {
       speak(normalizedSummary);
       lastSpokenTextRef.current = normalizedSummary;
    }

  }, [detectionResponse, detectionStatus, voiceEnabled, speak]);

  return (
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

      <View style={styles.mainContent}>
        <CameraScreen 
          setDetectionResponse={setDetectionResponse} 
          detectionStatus={detectionStatus}
          setDetectionStatus={setDetectionStatus}
          detectionErrorMsg={detectionErrorMsg}
          setDetectionErrorMsg={setDetectionErrorMsg}
        />
        <GuidancePanel 
          detectionResponse={detectionResponse} 
          detectionStatus={detectionStatus} 
          voiceEnabled={voiceEnabled}
          toggleVoice={toggleVoice}
          isSpeaking={isSpeaking}
          arabicAvailable={arabicAvailable}
        />
      </View>

      <StatusBar />
    </SafeAreaView>
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
    paddingTop: theme.spacing.xl, // Safe area for notch
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
    color: '#d1fae5', // Light emerald
    fontSize: 16,
  },
  mainContent: {
    flex: 1,
    justifyContent: 'space-between',
  }
});
