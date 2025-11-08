import { createClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';
import { SUPABASE_URL as ENV_SUPABASE_URL, SUPABASE_ANON_KEY as ENV_SUPABASE_ANON_KEY } from '@env';

const readString = (value) => (typeof value === 'string' ? value.trim() : '');

const getExpoExtra = () => {
  const extra = Constants?.expoConfig?.extra ?? Constants?.manifest?.extra ?? {};
  return typeof extra === 'object' && extra !== null ? extra : {};
};

export const getSupabaseCredentials = () => {
  const extra = getExpoExtra();
  const url = readString(extra.supabaseUrl) || readString(ENV_SUPABASE_URL);
  const anonKey = readString(extra.supabaseAnonKey) || readString(ENV_SUPABASE_ANON_KEY);
  return { url, anonKey };
};

export const isSupabaseConfigured = () => {
  const { url, anonKey } = getSupabaseCredentials();
  return Boolean(url && anonKey && url.startsWith('http') && anonKey.length > 20);
};

let supabaseClient = null;

export const getSupabase = () => {
  if (!isSupabaseConfigured()) {
    throw new Error('Supabase is not configured. Provide SUPABASE_URL and SUPABASE_ANON_KEY via environment variables or expoConfig.extra.');
  }

  if (!supabaseClient) {
    const { url, anonKey } = getSupabaseCredentials();
    supabaseClient = createClient(url, anonKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
      },
    });
  }

  return supabaseClient;
};

export const supabase = new Proxy({}, {
  get: (_target, prop) => {
    if (!isSupabaseConfigured()) {
      console.warn('⚠️ Supabase accessed but not configured. This is OK in development mode if using AsyncStorage.');
      return () => {
        throw new Error('Supabase is not configured. In development you can rely on AsyncStorage, or provide credentials.');
      };
    }
    const client = getSupabase();
    return client[prop];
  }
});
