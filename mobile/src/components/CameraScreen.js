import React, { useRef, useState, useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, TouchableOpacity } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { CameraOff, Camera } from 'lucide-react-native';
import useDetectionLoop from '../hooks/useDetectionLoop';
import { theme } from '../styles/theme';

export default function CameraScreen({ 
  setDetectionResponse, 
  detectionStatus, 
  setDetectionStatus, 
  detectionErrorMsg, 
  setDetectionErrorMsg 
}) {
  const [permission, requestPermission] = useCameraPermissions();
  const [isActive, setIsActive] = useState(true);
  const cameraRef = useRef(null);

  // Use the custom hook to handle the picture taking and Axios uploading loop
  useDetectionLoop({
    cameraRef,
    isActive: isActive && permission?.granted,
    setDetectionResponse,
    setDetectionStatus,
    setDetectionErrorMsg
  });

  // Handle permission loading state
  if (!permission) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  // Handle permission denied state
  if (!permission.granted) {
    return (
      <View style={styles.centerContainer}>
        <CameraOff size={64} color={theme.colors.textLight} />
        <Text style={styles.messageText}>نحتاج إلى صلاحية استخدام الكاميرا للتعرف على محيطك.</Text>
        <TouchableOpacity 
          style={styles.permissionButton} 
          onPress={requestPermission}
          accessible={true}
          accessibilityRole="button"
          accessibilityLabel="منح صلاحية الكاميرا"
        >
          <Text style={styles.permissionButtonText}>منح الصلاحية</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.cameraWrapper}>
        <CameraView 
          style={styles.camera} 
          facing="back" 
          ref={cameraRef}
          mute={true}
          shutterSound={false}
        />
        
        {/* Overlay showing analysis status */}
        <View style={styles.overlay}>
          {detectionStatus === 'error' ? (
            <View style={[styles.statusBadge, styles.statusError]}>
              <Text style={styles.statusTextError}>{detectionErrorMsg || 'فشل التحليل'}</Text>
            </View>
          ) : detectionStatus === 'capturing' || detectionStatus === 'analyzing' ? (
            <View style={[styles.statusBadge, styles.statusLoading]}>
              <ActivityIndicator size="small" color={theme.colors.primaryDark} />
              <Text style={styles.statusTextLoading}>جارِ التحليل...</Text>
            </View>
          ) : null}
        </View>

        {/* Toggle Camera Button */}
        <TouchableOpacity
          style={styles.toggleButton}
          onPress={() => setIsActive(!isActive)}
          accessible={true}
          accessibilityRole="button"
          accessibilityLabel={isActive ? "إيقاف الكاميرا مؤقتاً" : "تشغيل الكاميرا"}
        >
          {isActive ? <Camera size={24} color="#fff" /> : <CameraOff size={24} color="#fff" />}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.xl,
    backgroundColor: theme.colors.background,
  },
  cameraWrapper: {
    flex: 1,
    position: 'relative',
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    margin: theme.spacing.md,
    backgroundColor: '#000',
  },
  camera: {
    flex: 1,
  },
  messageText: {
    ...theme.typography.body,
    textAlign: 'center',
    color: theme.colors.text,
    marginVertical: theme.spacing.lg,
  },
  permissionButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.borderRadius.md,
  },
  permissionButtonText: {
    color: '#fff',
    ...theme.typography.h2,
  },
  overlay: {
    position: 'absolute',
    top: theme.spacing.md,
    left: theme.spacing.md,
    right: theme.spacing.md,
    flexDirection: 'row',
    justifyContent: 'center',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: theme.borderRadius.full,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
  },
  statusLoading: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
  },
  statusError: {
    backgroundColor: 'rgba(254, 242, 242, 0.9)',
    borderColor: theme.colors.error,
    borderWidth: 1,
  },
  statusTextLoading: {
    color: theme.colors.primaryDark,
    fontWeight: '600',
  },
  statusTextError: {
    color: theme.colors.error,
    fontWeight: '600',
  },
  toggleButton: {
    position: 'absolute',
    bottom: theme.spacing.lg,
    alignSelf: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    padding: theme.spacing.md,
    borderRadius: theme.borderRadius.full,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  }
});
