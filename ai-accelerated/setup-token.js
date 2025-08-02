import fs from 'fs';
import readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔧 Discord Bot Token Setup\n');

console.log('Please provide the following information:');
console.log('(You can find these in your Discord Developer Portal)\n');

rl.question('1. Discord Bot Token: ', (token) => {
  rl.question('2. Discord Client ID: ', (clientId) => {
    rl.question('3. Discord Guild ID (Server ID): ', (guildId) => {
      
      const envContent = `# Discord Bot Configuration
DISCORD_TOKEN=${token}
DISCORD_CLIENT_ID=${clientId}
DISCORD_GUILD_ID=${guildId}

# Optional Configuration
NODE_ENV=development
LOG_LEVEL=debug
RATE_LIMIT_WINDOW=60000
RATE_LIMIT_MAX_REQUESTS=5
`;

      try {
        fs.writeFileSync('.env', envContent);
        console.log('\n✅ .env file created successfully!');
        console.log('\n🚀 Next steps:');
        console.log('1. Start the bot: npm start');
        console.log('2. Deploy commands: node deploy-commands.js');
        console.log('3. Test in Discord!');
        console.log('\n🎯 Commands to test:');
        console.log('- /pick (VIP Play with units)');
        console.log('- /test-ocr (Upload bet slip image)');
        console.log('- /admin status (Check bot status)');
      } catch (error) {
        console.error('❌ Error creating .env file:', error.message);
      }
      
      rl.close();
    });
  });
}); 