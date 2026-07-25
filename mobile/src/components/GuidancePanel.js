import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, Linking } from 'react-native';
import { Accessibility, AlertTriangle, CircleCheck, Loader2, Volume1, Volume2, VolumeX } from 'lucide-react-native';
import { theme } from '../styles/theme';

export default function GuidancePanel({ 
  detectionResponse, 
  detectionStatus, 
  voiceEnabled, 
  toggleVoice, 
  isSpeaking,
  arabicAvailable,
}) {
  
  let content = null;
  let statusText = '';
  let statusType = 'normal'; // 'normal', 'error', 'success'

  if (detectionStatus === 'error') {
    statusType = 'error';
    content = (
      <View style={styles.contentWrapper} accessible={true} accessibilityRole="alert" accessibilityLabel="فشل تحليل الصورة، يرجى المحاولة مرة أخرى">
        <AlertTriangle size={32} color={theme.colors.error} />
        <Text style={[styles.messageText, { color: theme.colors.error }]}>فشل تحليل الصورة، يرجى المحاولة مرة أخرى.</Text>
      </View>
    );
  } else if (!detectionResponse) {
    content = (
      <View style={styles.contentWrapper} accessible={true} accessibilityRole="text" accessibilityLabel="بانتظار تحليل الصورة">
        <Text style={styles.messageText}>بانتظار تحليل الصورة...</Text>
      </View>
    );
  } else if (detectionResponse.success && detectionResponse.guidance) {
    statusType = 'success';
    content = (
      <View style={styles.contentWrapper} accessible={true} accessibilityRole="text" accessibilityLabel={detectionResponse.guidance.summary}>
        <Text style={styles.guidanceText}>{detectionResponse.guidance.summary}</Text>
      </View>
    );
  } else {
    content = (
      <View style={styles.contentWrapper} accessible={true} accessibilityRole="text" accessibilityLabel="لم يتم التعرف على المشهد الحالي">
        <Text style={styles.messageText}>لم يتم التعرف على المشهد الحالي.</Text>
      </View>
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
  let voiceLabel = 'تفعيل';
  if (voiceEnabled) {
    VoiceIcon = isSpeaking ? Volume2 : Volume1;
    voiceLabel = 'مُفَعَّل';
  }

  return (
    <View style={styles.container} accessible={true} accessibilityRole="adjustable" accessibilityLabel="لوحة التوجيهات والإرشادات">
      
      {/* Arabic TTS Warning Banner */}
      {arabicAvailable === false && (
        <TouchableOpacity
          style={styles.ttsBanner}
          onPress={() => Linking.openSettings()}
          accessible={true}
          accessibilityRole="button"
          accessibilityLabel="الصوت العربي غير متاح، اضغط لفتح الإعدادات"
        >
          <AlertTriangle size={16} color="#92400e" />
          <Text style={styles.ttsBannerText}>
            ⚠️ الصوت العربي غير مثبت — اضغط هنا لفتح إعدادات الجهاز وتحميله
          </Text>
        </TouchableOpacity>
      )}

      <View style={styles.header}>
        <View style={styles.headerTitleRow}>
          {HeaderIcon === Loader2 ? (
             <ActivityIndicator size="small" color={theme.colors.text} />
          ) : (
             <HeaderIcon size={24} color={theme.colors.text} />
          )}
          <Text style={styles.headerTitle}>الإرشاد الصوتي والنصي</Text>
        </View>
        
        <TouchableOpacity 
          style={[styles.voiceButton, voiceEnabled ? styles.voiceButtonActive : styles.voiceButtonInactive]}
          onPress={toggleVoice}
          accessible={true}
          accessibilityRole="button"
          accessibilityState={{ selected: voiceEnabled }}
          accessibilityLabel={voiceEnabled ? "إيقاف الإرشاد الصوتي" : "تفعيل الإرشاد الصوتي"}
        >
          <VoiceIcon size={20} color={voiceEnabled ? '#fff' : theme.colors.textLight} />
          <Text style={[styles.voiceButtonText, { color: voiceEnabled ? '#fff' : theme.colors.textLight }]}>{voiceLabel}</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.content}>
        {content}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  ttsBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#fef3c7',
    borderColor: '#f59e0b',
    borderWidth: 1,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
    marginBottom: theme.spacing.sm,
  },
  ttsBannerText: {
    flex: 1,
    fontSize: 12,
    color: '#92400e',
    fontWeight: '600',
    textAlign: 'right',
  },
  container: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.md,
    margin: theme.spacing.md,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
    paddingBottom: theme.spacing.md,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerTitle: {
    ...theme.typography.h2,
    color: theme.colors.text,
  },
  voiceButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: theme.borderRadius.md,
  },
  voiceButtonActive: {
    backgroundColor: theme.colors.primary,
  },
  voiceButtonInactive: {
    backgroundColor: theme.colors.border,
  },
  voiceButtonText: {
    fontWeight: 'bold',
    fontSize: 14,
  },
  content: {
    minHeight: 100,
    justifyContent: 'center',
  },
  contentWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
    padding: theme.spacing.md,
  },
  messageText: {
    ...theme.typography.body,
    textAlign: 'center',
    color: theme.colors.textLight,
  },
  guidanceText: {
    ...theme.typography.h1,
    textAlign: 'center',
    color: theme.colors.primaryDark,
    lineHeight: 36,
  }
});
