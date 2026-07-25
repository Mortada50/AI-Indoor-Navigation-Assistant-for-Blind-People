import { useState, useCallback, useEffect, useRef } from 'react';
import * as Speech from 'expo-speech';

export default function useSpeech() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [arabicAvailable, setArabicAvailable] = useState(null); // null = checking, true/false
  const arabicLangRef = useRef('ar');

  // On mount: find the best available Arabic voice
  useEffect(() => {
    const detectArabicVoice = async () => {
      try {
        const voices = await Speech.getAvailableVoicesAsync();
        console.log('Available TTS voices:', voices.map(v => `${v.identifier} (${v.language})`).join(', '));

        // Priority: ar-SA → ar-EG → ar-001 → ar-XA → any 'ar'
        const priorities = ['ar-SA', 'ar-EG', 'ar-001', 'ar-XA'];
        let found = null;

        for (const lang of priorities) {
          found = voices.find(v => v.language?.startsWith(lang));
          if (found) break;
        }

        if (!found) {
          found = voices.find(v => v.language?.startsWith('ar'));
        }

        if (found) {
          arabicLangRef.current = found.language;
          setArabicAvailable(true);
          console.log('✅ Arabic TTS voice found:', found.identifier, found.language);
        } else {
          setArabicAvailable(false);
          console.warn('⚠️ No Arabic TTS voice found on this device.');
        }
      } catch (e) {
        setArabicAvailable(false);
        console.warn('Could not fetch TTS voices:', e);
      }
    };
    detectArabicVoice();
  }, []);

  const cancel = useCallback(async () => {
    await Speech.stop();
    setIsSpeaking(false);
  }, []);

  const speak = useCallback(async (text) => {
    if (!text || arabicAvailable === false) return;

    await cancel();
    setIsSpeaking(true);

    Speech.speak(text, {
      language: arabicLangRef.current,
      rate: 0.85,
      pitch: 1.0,
      onDone: () => setIsSpeaking(false),
      onStopped: () => setIsSpeaking(false),
      onError: (e) => {
        console.error('SpeechSynthesis error:', e);
        setIsSpeaking(false);
      }
    });
  }, [cancel, arabicAvailable]);

  return {
    isSpeaking,
    arabicAvailable,
    speak,
    cancel
  };
}
