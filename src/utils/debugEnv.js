/**
 * Debug utility to check environment configuration
 */

import env from '../config/environment';

export const logEnvironmentDebug = () => {
  console.log('\n╔═══════════════════════════════════════════════════════════╗');
  console.log('║       POLLYVIEW ENVIRONMENT DEBUG                         ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`🌍 Environment: ${env.env} (${env.name})`);
  console.log(`📦 Storage Backend: ${env.useSupabase ? 'Supabase (Cloud)' : 'AsyncStorage (Local)'}`);
  console.log('');
  console.log('🔑 Supabase Configuration:');
  console.log(`   URL: ${env.supabase.url ? env.supabase.url.substring(0, 30) + '...' : 'NOT SET'}`);
  console.log(`   Key: ${env.supabase.anonKey ? env.supabase.anonKey.substring(0, 20) + '...' : 'NOT SET'}`);
  console.log(`   Configured: ${env.useSupabase ? '✅ YES' : '❌ NO'}`);
  console.log('');
  console.log('═══════════════════════════════════════════════════════════');
  console.log('');

  // Return config for further inspection
  return {
    environment: env.env,
    useSupabase: env.useSupabase,
    hasUrl: !!env.supabase.url,
    hasKey: !!env.supabase.anonKey,
  };
};

export default {
  logEnvironmentDebug,
};
