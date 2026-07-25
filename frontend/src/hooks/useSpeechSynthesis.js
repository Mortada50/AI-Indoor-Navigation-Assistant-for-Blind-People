import { useState, useEffect, useRef, useCallback } from 'react';

export default function useSpeechSynthesis() {
  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const voicesRef = useRef([]);

  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      setIsSupported(true);

      const updateVoices = () => {
        voicesRef.current = window.speechSynthesis.getVoices();
      };

      updateVoices();

      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = updateVoices;
      }
    }
    
    return () => {
       if (typeof window !== 'undefined' && window.speechSynthesis) {
          window.speechSynthesis.cancel();
       }
    };
  }, []);

  const getBestArabicVoice = () => {
    const voices = voicesRef.current;
    if (!voices || voices.length === 0) return null;

    // 1. Prefer explicitly ar-SA
    let best = voices.find(v => v.lang.toLowerCase() === 'ar-sa');
    if (best) return best;

    // 2. Prefer any Arabic voice
    best = voices.find(v => v.lang.toLowerCase().startsWith('ar'));
    if (best) return best;

    // 3. Fallback to default browser voice
    return voices.find(v => v.default) || voices[0];
  };

  const cancel = useCallback(() => {
    if (isSupported) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [isSupported]);

  const speak = useCallback((text) => {
    if (!isSupported || !text) return;

    // Cancel currently playing speech before starting new
    cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Configure Arabic preferences
    utterance.lang = 'ar-SA';
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    const arabicVoice = getBestArabicVoice();
    if (arabicVoice) {
      utterance.voice = arabicVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    
    utterance.onend = () => setIsSpeaking(false);
    
    utterance.onerror = (e) => {
      console.error('SpeechSynthesis error:', e);
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  }, [isSupported, cancel]);

  return {
    isSupported,
    isSpeaking,
    speak,
    cancel
  };
}
