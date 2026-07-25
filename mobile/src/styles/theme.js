export const theme = {
  colors: {
    primary: '#047857', // Emerald
    primaryDark: '#065f46',
    secondary: '#115e59', // Teal
    background: '#f8fafc', // Off White
    surface: '#ffffff',
    text: '#1e293b', // Slate 800
    textLight: '#64748b', // Slate 500
    error: '#dc2626', // Red 600
    errorBackground: '#fef2f2',
    success: '#16a34a', // Green 600
    successBackground: '#f0fdf4',
    border: '#e2e8f0', // Slate 200
  },
  typography: {
    fontFamily: 'System', // Will map to Roboto on Android
    h1: {
      fontSize: 24,
      fontWeight: 'bold',
    },
    h2: {
      fontSize: 20,
      fontWeight: '600',
    },
    body: {
      fontSize: 18,
      lineHeight: 28, // Better readability
    },
    caption: {
      fontSize: 14,
      color: '#64748b',
    }
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    full: 9999,
  }
};
