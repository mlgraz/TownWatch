import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { lightTheme, darkTheme } from '../theme/paperTheme';
import { getColors } from '../theme/colors';

const ThemeContext = createContext();

const THEME_STORAGE_KEY = '@TownWatch:theme_preference';

export const ThemeProvider = ({ children }) => {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeMode] = useState('auto'); // 'light', 'dark', 'auto'
  const [isLoading, setIsLoading] = useState(true);

  // Determine effective dark mode based on theme mode and system preference
  const isDark = themeMode === 'auto'
    ? systemColorScheme === 'dark'
    : themeMode === 'dark';

  const theme = isDark ? darkTheme : lightTheme;
  const colors = getColors(isDark);

  // Load saved theme preference
  useEffect(() => {
    loadThemePreference();
  }, []);

  const loadThemePreference = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme) {
        setThemeMode(savedTheme);
      }
    } catch (error) {
      console.error('Error loading theme preference:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const setTheme = async (mode) => {
    try {
      setThemeMode(mode);
      await AsyncStorage.setItem(THEME_STORAGE_KEY, mode);
    } catch (error) {
      console.error('Error saving theme preference:', error);
    }
  };

  const toggleTheme = () => {
    const nextMode = isDark ? 'light' : 'dark';
    setTheme(nextMode);
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        colors,
        isDark,
        themeMode,
        setTheme,
        toggleTheme,
        isLoading,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
