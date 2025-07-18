import { REST, Routes } from '@discordjs/rest';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Validate required environment variables
const requiredEnvVars = ['DISCORD_TOKEN', 'DISCORD_CLIENT_ID'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('❌ Missing required environment variables:', missingVars.join(', '));
  console.error('Please ensure these are set in your environment.');
  process.exit(1);
}

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

async function cleanupCommands() {
  try {
    console.log('🧹 Starting command cleanup...');
    console.log(`Client ID: ${process.env.DISCORD_CLIENT_ID}`);
    console.log(`Guild ID: ${process.env.GUILD_ID || 'Global deployment'}`);

    if (process.env.GUILD_ID) {
      // Clean up guild-specific commands
      console.log('🗑️ Removing all guild commands...');
      await rest.put(
        Routes.applicationGuildCommands(process.env.DISCORD_CLIENT_ID, process.env.GUILD_ID),
        { body: [] }
      );
      console.log('✅ All guild commands removed.');
    } else {
      // Clean up global commands
      console.log('🗑️ Removing all global commands...');
      await rest.put(
        Routes.applicationCommands(process.env.DISCORD_CLIENT_ID),
        { body: [] }
      );
      console.log('✅ All global commands removed.');
    }

    console.log('🔄 Waiting 5 seconds for Discord to process...');
    await new Promise(resolve => setTimeout(resolve, 5000));

    console.log('📦 Now redeploying current commands...');
    
    // Import and deploy current commands
    const { data: adminData } = await import('./src/commands/admin.js');
    const { data: pickData } = await import('./src/commands/pick.js');
    
    const commands = [adminData.toJSON(), pickData.toJSON()];

    if (process.env.GUILD_ID) {
      // Deploy to specific guild
      await rest.put(
        Routes.applicationGuildCommands(process.env.DISCORD_CLIENT_ID, process.env.GUILD_ID),
        { body: commands }
      );
      console.log(`✅ Successfully deployed ${commands.length} commands to guild ${process.env.GUILD_ID}.`);
    } else {
      // Deploy globally
      await rest.put(
        Routes.applicationCommands(process.env.DISCORD_CLIENT_ID),
        { body: commands }
      );
      console.log(`✅ Successfully deployed ${commands.length} commands globally.`);
    }

    console.log('🎉 Command cleanup and redeployment completed!');
    console.log('📋 Current commands:');
    console.log('  - /admin');
    console.log('  - /pick');
    
  } catch (error) {
    console.error('❌ Error during cleanup:', error);
    process.exit(1);
  }
}

cleanupCommands(); 