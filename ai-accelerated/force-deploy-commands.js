#!/usr/bin/env node

import { REST } from '@discordjs/rest';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

console.log('🚀 FORCE DEPLOYING DISCORD COMMANDS\n');

// Check if we're running in Render
const isRender = process.env.RENDER || process.env.NODE_ENV === 'production';
console.log(`Environment: ${isRender ? 'Render (Production)' : 'Local (Development)'}`);

// Validate required environment variables
const requiredEnvVars = ['DISCORD_TOKEN', 'DISCORD_CLIENT_ID'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('❌ Missing required environment variables:', missingVars.join(', '));
  console.error('Please ensure these are set in your environment.');
  process.exit(1);
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const commands = [];
const commandsPath = join(__dirname, 'src', 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

console.log(`📁 Found ${commandFiles.length} command files:`);

for (const file of commandFiles) {
  const filePath = join(commandsPath, file);
  const command = await import(filePath);
  
  if ('data' in command && 'execute' in command) {
    commands.push(command.data.toJSON());
    console.log(`   ✅ ${file} - ${command.data.name}`);
    
    // Show the options for the pick command
    if (command.data.name === 'pick') {
      console.log(`      Options:`);
      command.data.options.forEach(opt => {
        console.log(`        - ${opt.name}: ${opt.description}`);
      });
    }
  } else {
    console.log(`   ❌ ${file} - Missing required properties`);
  }
}

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

(async () => {
  try {
    console.log(`\n📝 Deploying ${commands.length} commands to Discord...`);
    console.log(`Client ID: ${process.env.DISCORD_CLIENT_ID}`);
    console.log(`Guild ID: ${process.env.DISCORD_GUILD_ID || 'Global deployment'}`);

    if (process.env.DISCORD_GUILD_ID) {
      // Deploy to specific guild (faster for development)
      await rest.put(
        `/applications/${process.env.DISCORD_CLIENT_ID}/guilds/${process.env.DISCORD_GUILD_ID}/commands`,
        { body: commands }
      );
      console.log(`✅ Successfully deployed ${commands.length} commands to guild ${process.env.DISCORD_GUILD_ID}`);
    } else {
      // Deploy globally
      await rest.put(
        `/applications/${process.env.DISCORD_CLIENT_ID}/commands`,
        { body: commands }
      );
      console.log(`✅ Successfully deployed ${commands.length} commands globally`);
    }

    console.log('\n🎯 Commands deployed:');
    commands.forEach(cmd => {
      console.log(`   - /${cmd.name}: ${cmd.description}`);
      if (cmd.options) {
        cmd.options.forEach(opt => {
          console.log(`     └─ ${opt.name}: ${opt.description}`);
        });
      }
    });

    console.log('\n🚀 Your bot is now ready! Test these commands:');
    console.log('   - /pick (VIP Play with units)');
    console.log('   - /test-ocr (Upload bet slip image)');
    console.log('   - /admin status (Check bot status)');

    console.log('\n⏰ Note: Discord may take a few minutes to update the command cache.');
    console.log('   If you still see the old "notes" option, wait 2-3 minutes and try again.');

  } catch (error) {
    console.error('❌ Error deploying commands:', error);
    console.error('Error details:', error.message);
    process.exit(1);
  }
})(); 