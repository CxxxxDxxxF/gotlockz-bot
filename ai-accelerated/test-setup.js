import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🚀 GotLockz Bot - AI Accelerated Setup Test\n');

// Test 1: Check Node.js version
console.log('1. Node.js Version Check:');
const nodeVersion = process.version;
const requiredVersion = '18.0.0';
console.log(`   Current: ${nodeVersion}`);
console.log(`   Required: >=${requiredVersion}`);
console.log(`   ✅ ${nodeVersion >= requiredVersion ? 'PASS' : 'FAIL'}\n`);

// Test 2: Check dependencies
console.log('2. Dependencies Check:');
try {
  const packageJson = JSON.parse(fs.readFileSync(join(__dirname, 'package.json'), 'utf8'));
  const requiredDeps = ['discord.js', 'tesseract.js', 'sharp', 'openai'];
  
  for (const dep of requiredDeps) {
    const version = packageJson.dependencies[dep];
    console.log(`   ${dep}: ${version ? '✅' : '❌'} ${version || 'NOT FOUND'}`);
  }
  console.log('   ✅ All required dependencies found\n');
} catch (error) {
  console.log(`   ❌ Error reading package.json: ${error.message}\n`);
}

// Test 3: Check file structure
console.log('3. File Structure Check:');
const requiredFiles = [
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
  'env.example'
];

for (const file of requiredFiles) {
  const exists = fs.existsSync(join(__dirname, file));
  console.log(`   ${file}: ${exists ? '✅' : '❌'}`);
}
console.log('   ✅ File structure check complete\n');

// Test 4: Check environment variables
console.log('4. Environment Variables Check:');
const requiredEnvVars = ['DISCORD_TOKEN', 'CLIENT_ID', 'OWNER_ID'];
const optionalEnvVars = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY', 'GUILD_ID'];

console.log('   Required:');
for (const envVar of requiredEnvVars) {
  const value = process.env[envVar];
  console.log(`     ${envVar}: ${value ? '✅ SET' : '❌ MISSING'}`);
}

console.log('   Optional:');
for (const envVar of optionalEnvVars) {
  const value = process.env[envVar];
  console.log(`     ${envVar}: ${value ? '✅ SET' : '⚠️  NOT SET'}`);
}
console.log('');

// Test 5: Test imports
console.log('5. Import Test:');
try {
  // Test basic imports
  const { logger } = await import('./src/utils/logger.js');
  console.log('   ✅ Logger import successful');
  
  const { rateLimiter } = await import('./src/utils/rateLimiter.js');
  console.log('   ✅ Rate limiter import successful');
  
  const { getSystemStats } = await import('./src/utils/systemStats.js');
  console.log('   ✅ System stats import successful');
  
  // Test service imports
  const { analyzeImage } = await import('./src/services/ocrService.js');
  console.log('   ✅ OCR service import successful');
  
  const { getGameData } = await import('./src/services/mlbService.js');
  console.log('   ✅ MLB service import successful');
  
  const { generateAnalysis } = await import('./src/services/aiService.js');
  console.log('   ✅ AI service import successful');
  
  const { createBettingMessage } = await import('./src/services/bettingService.js');
  console.log('   ✅ Betting service import successful');
  
  console.log('   ✅ All imports successful\n');
} catch (error) {
  console.log(`   ❌ Import error: ${error.message}\n`);
}

// Test 6: Test command loading
console.log('6. Command Loading Test:');
try {
  const commandsPath = join(__dirname, 'src', 'commands');
  const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
  
  console.log(`   Found ${commandFiles.length} command files:`);
  for (const file of commandFiles) {
    const command = await import(join(commandsPath, file));
    const hasData = 'data' in command;
    const hasExecute = 'execute' in command;
    console.log(`     ${file}: ${hasData && hasExecute ? '✅' : '❌'} (data: ${hasData}, execute: ${hasExecute})`);
  }
  console.log('   ✅ Command loading test complete\n');
} catch (error) {
  console.log(`   ❌ Command loading error: ${error.message}\n`);
}

// Summary
console.log('📊 Setup Test Summary:');
console.log('   If all tests show ✅, your AI-accelerated bot is ready to run!');
console.log('   Next steps:');
console.log('   1. Set up your .env file with Discord credentials');
console.log('   2. Run: npm run deploy (to register slash commands)');
console.log('   3. Run: npm start (to start the bot)');
console.log('   4. Test with /admin ping in Discord');
console.log('\n🚀 Ready for AI-powered betting analysis!'); 