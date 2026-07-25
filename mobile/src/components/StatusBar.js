import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Server, CircleCheck, CircleX, RefreshCw } from 'lucide-react-native';
import api from '../services/api';
import { theme } from '../styles/theme';

export default function StatusBar() {
  const [backendStatus, setBackendStatus] = useState('loading'); // 'loading', 'connected', 'error'

  useEffect(() => {
    let active = true;

    async function checkHealth() {
      if (active && backendStatus !== 'loading' && backendStatus !== 'connected') {
        setBackendStatus('loading');
      }
      try {
        const response = await api.get('/api/health');
        if (response.status === 200 && active) {
          setBackendStatus('connected');
        } else if (active) {
          setBackendStatus('error');
        }
      } catch (err) {
        if (active) {
          setBackendStatus('error');
        }
      }
    }

    // Initial check
    checkHealth();

    // Poll every 10 seconds for backend health
    const intervalId = setInterval(checkHealth, 10000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, []);

  let backendLabel = 'جاري الاتصال...';
  let StatusIcon = RefreshCw;
  let statusColor = theme.colors.textLight;

  if (backendStatus === 'connected') {
    backendLabel = 'الخادم متصل';
    StatusIcon = CircleCheck;
    statusColor = theme.colors.success;
  }
  if (backendStatus === 'error') {
    backendLabel = 'تعذر الاتصال بالخادم';
    StatusIcon = CircleX;
    statusColor = theme.colors.error;
  }

  return (
    <View style={styles.container} accessible={true} accessibilityRole="text" accessibilityLabel={`حالة النظام: ${backendLabel}`}>
      <View style={styles.statusItem}>
        <StatusIcon size={18} color={statusColor} />
        <Text style={[styles.statusText, { color: statusColor }]}>{backendLabel}</Text>
      </View>
      <View style={styles.statusItem}>
        <Server size={18} color={theme.colors.secondary} />
        <Text style={styles.statusText}>الإرشاد الذكي</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
  },
  statusItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusText: {
    fontSize: 14,
    color: theme.colors.textLight,
    fontWeight: '500',
  }
});
