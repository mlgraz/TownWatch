import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';
import { lightColors, darkColors } from './colors';

export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: lightColors.primary,
    primaryContainer: lightColors.primaryDark,
    secondary: lightColors.accent,
    background: lightColors.background,
    surface: lightColors.surface,
    error: lightColors.error,
    onSurface: lightColors.text,
    onBackground: lightColors.text,
  },
};

export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: darkColors.primary,
    primaryContainer: darkColors.primaryDark,
    secondary: darkColors.accent,
    background: darkColors.background,
    surface: darkColors.surface,
    error: darkColors.error,
    onSurface: darkColors.text,
    onBackground: darkColors.text,
  },
};
