import { Accessibility, AlertTriangle, CircleCheck, Loader2, Volume1, Volume2, VolumeX } from 'lucide-react';

export default function GuidancePanel({ 
  detectionResponse, 
  detectionStatus, 
  voiceEnabled, 
  toggleVoice, 
  isSpeaking, 
  isSupported 
}) {
  
  let content = null;

  if (detectionStatus === 'error') {
    content = (
      <div className="guidance-text error" aria-live="assertive" role="alert" style={{ color: '#c53030', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
        <AlertTriangle size={32} />
        <p>فشل تحليل الصورة، يرجى المحاولة مرة أخرى.</p>
      </div>
    );
  } else if (!detectionResponse) {
    content = (
      <div className="guidance-text" aria-live="polite" role="status">
        بانتظار تحليل الصورة...
      </div>
    );
  } else if (detectionResponse.success && detectionResponse.guidance) {
    content = (
      <div className="guidance-text" aria-live="polite" role="status">
        {detectionResponse.guidance.summary}
      </div>
    );
  } else {
    content = (
      <div className="guidance-text" aria-live="polite" role="status">
        لم يتم التعرف على المشهد الحالي.
      </div>
    );
  }

  // Determine header icon based on status
  let HeaderIcon = Accessibility;
  if (detectionStatus === 'analyzing' || detectionStatus === 'capturing') {
    HeaderIcon = Loader2;
  } else if (detectionStatus === 'success') {
    HeaderIcon = CircleCheck;
  } else if (detectionStatus === 'error') {
    HeaderIcon = AlertTriangle;
  }

  // Voice Icon State
  let VoiceIcon = VolumeX;
  if (voiceEnabled) {
    VoiceIcon = isSpeaking ? Volume2 : Volume1;
  }

  return (
    <section 
      className="guidance-panel card-panel" 
      aria-label="توجيهات وإرشادات البيئة المحيطة"
      style={{ marginTop: '1.5rem' }}
    >
      <div className="guidance-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <HeaderIcon size={20} className={HeaderIcon === Loader2 ? 'lucide-spin' : ''} />
          <h2>الإرشاد الصوتي والنصي</h2>
        </div>
        
        {isSupported && (
          <button 
            onClick={toggleVoice}
            aria-pressed={voiceEnabled}
            aria-label={voiceEnabled ? "إيقاف الإرشاد الصوتي" : "تفعيل الإرشاد الصوتي"}
            title={voiceEnabled ? "إيقاف الإرشاد الصوتي" : "تفعيل الإرشاد الصوتي"}
            style={{
              background: voiceEnabled ? '#047857' : '#e2e8f0',
              color: voiceEnabled ? '#ffffff' : '#4a5568',
              border: 'none',
              borderRadius: '8px',
              padding: '0.4rem 0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.9rem',
              transition: 'background 0.2s ease'
            }}
          >
            <VoiceIcon size={18} />
            <span>{voiceEnabled ? "مُفَعَّل" : "تفعيل"}</span>
          </button>
        )}
      </div>
      
      <div className="guidance-content">
        {content}
      </div>
    </section>
  );
}
