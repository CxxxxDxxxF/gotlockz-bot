#!/usr/bin/env node

import { execSync } from 'child_process';
import fs from 'fs';

console.log('🚀 GotLockz Bot Quick Start\n');

// Check if .env exists
if (!fs.existsSync('.env')) {
  console.log('❌ .env file not found!');
  console.log('Please run: node setup-token.js');
  console.log('This will help you set up your Discord credentials.\n');
  process.exit(1);
}

console.log('✅ .env file found');
console.log('🔧 Starting bot setup...\n');

try {
  // Step 1: Deploy commands
  console.log('📝 Step 1: Deploying Discord commands...');
  execSync('node deploy-commands.js', { stdio: 'inherit' });
  console.log('✅ Commands deployed successfully!\n');
  
  // Step 2: Start the bot
  console.log('🤖 Step 2: Starting the bot...');
  console.log('Press Ctrl+C to stop the bot\n');
  
  execSync('npm start', { stdio: 'inherit' });
  
} catch (error) {
  console.error('❌ Error during setup:', error.message);
  console.log('\n🔧 Troubleshooting:');
  console.log('1. Make sure your Discord token is correct');
  console.log('2. Check that your bot has proper permissions');
  console.log('3. Verify your server ID is correct');
  console.log('4. Try running: node setup-token.js again');
} 