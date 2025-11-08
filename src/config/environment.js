/**
 * Environment configuration for TownWatch
 *
 * Determines which storage backend to use based on environment
 */

// Import environment variables using react-native-dotenv
import { NODE_ENV } from '@env';
import { getSupabaseCredentials, isSupabaseConfigured } from './supabase';

// Get environment from imported env or default to development
const ENV = NODE_ENV || process.env.NODE_ENV || 'development';

// Check if Supabase credentials are actually configured
// Environment configurations
const environments = {
  development: {
    name: 'Development',
    preferSupabase: true,
    enableLogging: true,
  },
  test: {
    name: 'Testing',
    preferSupabase: true,
    enableLogging: true,
  },
  production: {
    name: 'Production',
    preferSupabase: true,
    enableLogging: false,
  },
};

// Get current environment config
const currentConfig = environments[ENV] || environments.development;

// Determine which storage to use
const shouldUseSupabase = () => {
  if (!currentConfig.preferSupabase) {
    return false;
  }
  return isSupabaseConfigured();
};

export default {
  env: ENV,
  name: currentConfig.name,
  useSupabase: shouldUseSupabase(),
  enableLogging: currentConfig.enableLogging,
  supabase: getSupabaseCredentials(),
};

// Helper to log environment info
export const logEnvironment = () => {
  if (currentConfig.enableLogging) {
    const { url, anonKey } = getSupabaseCredentials();
    const maskedKey = anonKey ? `${anonKey.slice(0, 6)}…${anonKey.slice(-4)}` : 'Not set';
    const maskedUrl = url ? `${url.replace(/^(https?:\/\/)/, '')}` : 'Not set';
    console.log('═══════════════════════════════════════');
    console.log('🌍 TownWatch Environment Configuration');
    console.log('═══════════════════════════════════════');
    console.log(`Environment: ${currentConfig.name} (${ENV})`);
    console.log(`Storage Backend: ${shouldUseSupabase() ? 'Supabase (Cloud)' : 'AsyncStorage (Local)'}`);
    console.log(`Supabase URL: ${maskedUrl}`);
    console.log(`Supabase Key: ${isSupabaseConfigured() ? maskedKey : 'Not set'}`);
    console.log('═══════════════════════════════════════');
  }
};
