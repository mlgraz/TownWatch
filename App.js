import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Provider as PaperProvider } from 'react-native-paper';
import { View, Text } from 'react-native';

// Debug environment configuration
import { logEnvironmentDebug } from './src/utils/debugEnv';

// Log environment on app start
console.log('🚀 App starting...');
try {
  logEnvironmentDebug();
} catch (error) {
  console.error('❌ Error loading environment debug:', error);
}

// Import with error catching
let DocumentProvider, ThemeProvider, useTheme, AppNavigator;

try {
  const docContext = require('./src/context/DocumentContext');
  DocumentProvider = docContext.DocumentProvider;
  console.log('✅ DocumentContext loaded');
} catch (error) {
  console.error('❌ Error loading DocumentContext:', error);
}

try {
  const themeContext = require('./src/context/ThemeContext');
  ThemeProvider = themeContext.ThemeProvider;
  useTheme = themeContext.useTheme;
  console.log('✅ ThemeContext loaded');
} catch (error) {
  console.error('❌ Error loading ThemeContext:', error);
}

try {
  const nav = require('./src/navigation/AppNavigator');
  AppNavigator = nav.default;
  console.log('✅ AppNavigator loaded');
} catch (error) {
  console.error('❌ Error loading AppNavigator:', error);
}

function AppContent() {
  try {
    const { theme, isDark } = useTheme();

    return (
      <PaperProvider theme={theme}>
        <DocumentProvider>
          <AppNavigator />
          <StatusBar style={isDark ? 'light' : 'dark'} />
        </DocumentProvider>
      </PaperProvider>
    );
  } catch (error) {
    console.error('❌ Error in AppContent:', error);
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
        <Text style={{ color: 'red', fontSize: 16, textAlign: 'center' }}>
          Error loading app: {error.message}
        </Text>
      </View>
    );
  }
}

export default function App() {
  try {
    return (
      <GestureHandlerRootView style={{ flex: 1 }}>
        <ThemeProvider>
          <AppContent />
        </ThemeProvider>
      </GestureHandlerRootView>
    );
  } catch (error) {
    console.error('❌ Error in App:', error);
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
        <Text style={{ color: 'red', fontSize: 16, textAlign: 'center' }}>
          Fatal error: {error.message}
        </Text>
      </View>
    );
  }
}
