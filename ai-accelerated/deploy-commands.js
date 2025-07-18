import { REST } from '@discordjs/rest';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

// Validate required environment variables
const requiredEnvVars = ['DISCORD_TOKEN', 'CLIENT_ID'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('❌ Missing required environment variables:', missingVars.join(', '));
  console.error('Please ensure these are set in your Render environment variables.');
  process.exit(1);
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const commands = [];
const commandsPath = join(__dirname, 'src', 'commands');
const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
  const filePath = join(commandsPath, file);
  const command = await import(filePath);
  
  if ('data' in command && 'execute' in command) {
    commands.push(command.data.toJSON());
  } else {
    console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
  }
}

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);

(async () => {
  try {
    console.log(`Started refreshing ${commands.length} application (/) commands.`);
    console.log(`Client ID: ${process.env.CLIENT_ID}`);
    console.log(`Guild ID: ${process.env.GUILD_ID || 'Global deployment'}`);

    if (process.env.GUILD_ID) {
      // Deploy to specific guild (faster for development)
      await rest.put(
        `/applications/${process.env.CLIENT_ID}/guilds/${process.env.GUILD_ID}/commands`,
        { body: commands }
      );
      console.log(`Successfully reloaded ${commands.length} application (/) commands for guild ${process.env.GUILD_ID}.`);
    } else {
      // Deploy globally
      await rest.put(
        `/applications/${process.env.CLIENT_ID}/commands`,
        { body: commands }
      );
      console.log(`Successfully reloaded ${commands.length} application (/) commands globally.`);
    }
  } catch (error) {
    console.error('Error deploying commands:', error);
    process.exit(1);
  }
})(); 