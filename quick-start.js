#!/usr/bin/env node

import { logger } from './src/utils/logger.js';
import fs from 'fs';
import path from 'path';

console.log('🚀 GotLockz Bot - Quick Start Guide\n');

// Check environment variables
const requiredEnvVars = ['DISCORD_TOKEN', 'CLIENT_ID', 'OWNER_ID'];
const optionalEnvVars = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY', 'GUILD_ID'];

console.log('📋 Environment Variables Check:');
console.log('================================');

let allRequiredSet = true;
requiredEnvVars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    console.log(`✅ ${varName}: Set`);
  } else {
    console.log(`❌ ${varName}: MISSING`);
    allRequiredSet = false;
  }
});

console.log('\nOptional Variables:');
optionalEnvVars.forEach(varName => {
  const value = process.env[varName];
  if (value) {
    console.log(`✅ ${varName}: Set`);
  } else {
    console.log(`⚠️  ${varName}: Not set (optional)`);
  }
});

// Check file structure
console.log('\n📁 File Structure Check:');
console.log('========================');

const requiredFiles = [
  'package.json',
  'package-lock.json',
  'src/index.js',
  'src/commands/pick.js',
  'src/commands/admin.js',
  'src/services/aiService.js',
  'src/services/ocrService.js',
  'src/services/mlbService.js',
  'src/services/bettingService.js',
  'deploy-commands.js',
  'Dockerfile',
  'render.yaml'
];

let allFilesExist = true;
requiredFiles.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file}: Missing`);
    allFilesExist = false;
  }
});

// Check Node.js version
console.log('\n🔧 System Check:');
console.log('================');
const nodeVersion = process.version;
const requiredVersion = '18.0.0';
console.log(`Node.js Version: ${nodeVersion}`);

if (nodeVersion >= requiredVersion) {
  console.log('✅ Node.js version is compatible');
} else {
  console.log(`❌ Node.js version ${requiredVersion} or higher required`);
}

// Deployment instructions
console.log('\n🚀 Deployment Instructions:');
console.log('============================');

if (!allRequiredSet) {
  console.log('\n❌ MISSING REQUIRED ENVIRONMENT VARIABLES');
  console.log('Please set the following environment variables:');
  requiredEnvVars.forEach(varName => {
    if (!process.env[varName]) {
      console.log(`   ${varName}`);
    }
  });
  console.log('\nFor Render deployment:');
  console.log('1. Go to your Render dashboard');
  console.log('2. Select your web service');
  console.log('3. Go to Environment tab');
  console.log('4. Add the missing variables');
  console.log('5. Redeploy the service');
} else {
  console.log('✅ All required environment variables are set!');
  console.log('Ready for deployment.');
}

if (!allFilesExist) {
  console.log('\n❌ MISSING REQUIRED FILES');
  console.log('Please ensure all required files are present in the repository.');
} else {
  console.log('✅ All required files are present!');
}

console.log('\n📖 Next Steps:');
console.log('==============');
console.log('1. If deploying to Render:');
console.log('   - Connect your GitHub repository');
console.log('   - Set environment variables');
console.log('   - Deploy the service');
console.log('\n2. If running locally:');
console.log('   - Run: npm install');
console.log('   - Run: npm run deploy');
console.log('   - Run: npm start');
console.log('\n3. Test the bot:');
console.log('   - Use /pick command in Discord');
console.log('   - Check /admin status');
console.log('   - Visit /health endpoint');

console.log('\n📚 Documentation:');
console.log('==================');
console.log('- Deployment Guide: DEPLOYMENT_GUIDE.md');
console.log('- Troubleshooting: TROUBLESHOOTING.md');
console.log('- Project README: README_AI.md');

console.log('\n🎯 Ready to deploy your AI-accelerated MLB Discord bot!'); 