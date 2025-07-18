#!/usr/bin/env node

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 GotLockz Bot - Deployment Status Check\n');

let allChecksPassed = true;

// Check 1: Required files
console.log('1. Required Files:');
const requiredFiles = [
  'package.json',
  'package-lock.json',
  'src/index.js',
  'src/commands/pick.js',
  'src/commands/admin.js',
  'src/services/ocrService.js',
  'src/services/mlbService.js',
  'src/services/aiService.js',
  'src/services/bettingService.js',
  'src/utils/logger.js',
  'src/utils/rateLimiter.js',
  'src/utils/systemStats.js',
  'deploy-commands.js',
  'deploy.sh',
  'Dockerfile',
  'render.yaml',
  'env.example'
];

for (const file of requiredFiles) {
  const exists = fs.existsSync(join(__dirname, file));
  console.log(`   ${file}: ${exists ? '✅' : '❌'}`);
  if (!exists) allChecksPassed = false;
}

// Check 2: Environment variables
console.log('\n2. Environment Variables:');
const requiredEnvVars = ['DISCORD_TOKEN', 'CLIENT_ID', 'OWNER_ID'];
const optionalEnvVars = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY', 'GUILD_ID'];

console.log('   Required:');
for (const envVar of requiredEnvVars) {
  const value = process.env[envVar];
  console.log(`     ${envVar}: ${value ? '✅ SET' : '❌ MISSING'}`);
  if (!value) allChecksPassed = false;
}

console.log('   Optional:');
for (const envVar of optionalEnvVars) {
  const value = process.env[envVar];
  console.log(`     ${envVar}: ${value ? '✅ SET' : '⚠️  NOT SET'}`);
}

// Check 3: Dependencies
console.log('\n3. Dependencies:');
try {
  const packageJson = JSON.parse(fs.readFileSync(join(__dirname, 'package.json'), 'utf8'));
  const requiredDeps = ['discord.js', 'tesseract.js', 'sharp', 'openai', '@huggingface/inference'];
  
  for (const dep of requiredDeps) {
    const version = packageJson.dependencies[dep];
    console.log(`   ${dep}: ${version ? '✅' : '❌'} ${version || 'NOT FOUND'}`);
    if (!version) allChecksPassed = false;
  }
} catch (error) {
  console.log(`   ❌ Error reading package.json: ${error.message}`);
  allChecksPassed = false;
}

// Check 4: Node.js version
console.log('\n4. Node.js Version:');
const nodeVersion = process.version;
const requiredVersion = '18.0.0';
console.log(`   Current: ${nodeVersion}`);
console.log(`   Required: >=${requiredVersion}`);
console.log(`   ${nodeVersion >= requiredVersion ? '✅ PASS' : '❌ FAIL'}`);
if (nodeVersion < requiredVersion) allChecksPassed = false;

// Check 5: Docker setup
console.log('\n5. Docker Setup:');
const dockerfileExists = fs.existsSync(join(__dirname, 'Dockerfile'));
const dockerignoreExists = fs.existsSync(join(__dirname, '../.dockerignore'));
console.log(`   Dockerfile: ${dockerfileExists ? '✅' : '❌'}`);
console.log(`   .dockerignore: ${dockerignoreExists ? '✅' : '❌'}`);
if (!dockerfileExists) allChecksPassed = false;

// Check 6: Render configuration
console.log('\n6. Render Configuration:');
const renderYamlExists = fs.existsSync(join(__dirname, 'render.yaml'));
const rootRenderYamlExists = fs.existsSync(join(__dirname, '../render.yaml'));
console.log(`   ai-accelerated/render.yaml: ${renderYamlExists ? '✅' : '❌'}`);
console.log(`   root/render.yaml: ${rootRenderYamlExists ? '✅' : '❌'}`);
if (!renderYamlExists || !rootRenderYamlExists) allChecksPassed = false;

// Summary
console.log('\n📊 Deployment Status Summary:');
if (allChecksPassed) {
  console.log('✅ ALL CHECKS PASSED - Ready for deployment!');
  console.log('\n🚀 Next steps:');
  console.log('   1. Push to GitHub');
  console.log('   2. Deploy on Render');
  console.log('   3. Set environment variables in Render dashboard');
  console.log('   4. Test with /admin ping');
} else {
  console.log('❌ SOME CHECKS FAILED - Please fix issues before deploying');
  console.log('\n🔧 Common fixes:');
  console.log('   - Set missing environment variables');
  console.log('   - Install missing dependencies');
  console.log('   - Create missing files');
}

console.log('\n🎯 Ready for AI-powered betting analysis!'); 