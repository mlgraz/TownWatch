const fs = require('fs');
const path = require('path');

module.exports = function(api) {
  api.cache(true);

  // Determine which .env file to use based on NODE_ENV
  const preferredEnvFile = process.env.NODE_ENV === 'production'
    ? '.env.production'
    : process.env.NODE_ENV === 'test'
    ? '.env.test'
    : '.env.development';

  const preferredPath = path.resolve(__dirname, preferredEnvFile);
  const resolvedEnvFile = fs.existsSync(preferredPath) ? preferredEnvFile : '.env.example';

  if (resolvedEnvFile !== preferredEnvFile) {
    console.warn(`⚠️  Expected ${preferredEnvFile} but it was not found. Falling back to ${resolvedEnvFile}.`);
  }

  console.log(`🌍 Loading environment from: ${resolvedEnvFile}`);

  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['module:react-native-dotenv', {
        moduleName: '@env',
        path: resolvedEnvFile,
        blacklist: null,
        whitelist: null,
        safe: false,
        allowUndefined: true
      }],
      'react-native-reanimated/plugin'
    ],
  };
};
