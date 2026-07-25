import { useState, useEffect, useRef } from 'react';
import CameraView from './components/CameraView';
import GuidancePanel from './components/GuidancePanel';
import StatusBar from './components/StatusBar';
import useSpeechSynthesis from './hooks/useSpeechSynthesis';
import { Navigation } from 'lucide-react';
import './App.css';

function App() {
  const [detectionResponse, setDetectionResponse] = useState(null);
  const [detectionStatus, setDetectionStatus] = useState('idle');
  const [detectionErrorMsg, setDetectionErrorMsg] = useState('');
  
  // Voice state
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const lastSpokenTextRef = useRef('');
  
  const { isSupported, isSpeaking, speak, cancel } = useSpeechSynthesis();

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
    if (!voiceEnabled || !isSupported) return;
    
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

  }, [detectionResponse, detectionStatus, voiceEnabled, isSupported, speak]);

  return (
    <>
      <header className="app-header">
        <div className="app-title-container" tabIndex="0">
          <Navigation size={28} aria-hidden="true" />
          <h1 className="app-title">مساعد الإرشاد المكاني</h1>
        </div>
        <p className="app-description" tabIndex="0">
          تطبيق صمم لمساعدة المكفوفين وضعاف البصر على إدراك البيئة المحيطة من خلال التعرف الذكي.
        </p>
      </header>

      <main>
        <CameraView 
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
          isSupported={isSupported}
        />
      </main>

      <StatusBar />
    </>
  );
}

export default App;
