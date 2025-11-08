/**
 * Color definitions for light and dark themes
 */

export const lightColors = {
  // Primary colors
  primary: '#6200ee',
  primaryDark: '#3700b3',
  accent: '#e91e63',

  // Background colors
  background: '#f5f5f5',
  surface: '#ffffff',
  card: '#ffffff',

  // Text colors
  text: '#333333',
  textSecondary: '#666666',
  textTertiary: '#999999',

  // Border colors
  border: '#e0e0e0',
  divider: '#e0e0e0',

  // Status colors
  error: '#b00020',
  success: '#4caf50',
  warning: '#ff9800',
  info: '#2196f3',

  // Document type colors
  legislature: '#6200ee',
  council: '#1976d2',
  board: '#00897b',
  planning: '#43a047',
  transportation: '#fb8c00',
  budget: '#e53935',
  default: '#757575',
};

export const darkColors = {
  // Primary colors
  primary: '#bb86fc',
  primaryDark: '#3700b3',
  accent: '#cf6679',

  // Background colors
  background: '#121212',
  surface: '#1e1e1e',
  card: '#2d2d2d',

  // Text colors
  text: '#ffffff',
  textSecondary: '#b0b0b0',
  textTertiary: '#808080',

  // Border colors
  border: '#3a3a3a',
  divider: '#3a3a3a',

  // Status colors
  error: '#cf6679',
  success: '#81c784',
  warning: '#ffb74d',
  info: '#64b5f6',

  // Document type colors (slightly lighter for dark mode)
  legislature: '#bb86fc',
  council: '#64b5f6',
  board: '#4db6ac',
  planning: '#81c784',
  transportation: '#ffb74d',
  budget: '#e57373',
  default: '#9e9e9e',
};

export const getColors = (isDark) => isDark ? darkColors : lightColors;
