import { Client, GatewayIntentBits, Collection, Interaction } from 'discord.js';
import { REST, Routes } from '@discordjs/rest';
import { getEnv } from './utils/env';
import { Logger } from './utils/logger';
import express from 'express';

// Import commands (will be updated when we refactor them)
import { data as pickData, execute as pickExecute } from './commands/pick';
import { data as adminData, execute as adminExecute } from './commands/admin';

const env = getEnv();
const logger = new Logger('main');

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent],
});

const commands = [pickData, adminData];
const commandHandlers = new Collection<string, any>();
commandHandlers.set('pick', pickExecute);
commandHandlers.set('admin', adminExecute);

// Express app for health checks
const app = express();
const PORT = env.PORT || 3000;

app.get('/health', (_req: express.Request, res: express.Response) => {
  res.json({ 
    status: 'ok', 
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    version: '4.0.0'
  });
});

app.listen(PORT, () => {
  logger.info(`Health endpoint listening on port ${PORT}`);
});

async function registerCommands() {
  const rest = new REST({ version: '10' }).setToken(env.DISCORD_BOT_TOKEN);
  const body = commands.map(cmd => cmd.toJSON());
  
  try {
    if (env.DISCORD_GUILD_ID) {
      await rest.put(Routes.applicationGuildCommands(env.DISCORD_CLIENT_ID, env.DISCORD_GUILD_ID), { body });
      logger.info('Registered guild commands');
    } else {
      await rest.put(Routes.applicationCommands(env.DISCORD_CLIENT_ID), { body });
      logger.info('Registered global commands');
    }
  } catch (error) {
    logger.error('Failed to register commands', { error });
    throw error;
  }
}

client.once('ready', () => {
  logger.info(`Logged in as ${client.user?.tag}`);
  logger.info('Bot is ready and analysis service is up!');
});

client.on('interactionCreate', async (interaction: Interaction) => {
  if (!interaction.isChatInputCommand()) return;
  
  const handler = commandHandlers.get(interaction.commandName);
  if (!handler) return;
  
  try {
    if (interaction.commandName === 'admin') {
      await handler(interaction, client);
    } else {
      await handler(interaction);
    }
  } catch (error) {
    logger.error('Command execution failed', { 
      command: interaction.commandName, 
      userId: interaction.user.id,
      error 
    });
    
    const reply = interaction.replied ? interaction.followUp : interaction.reply;
    await reply({ 
      content: '❌ An error occurred while executing this command.', 
      ephemeral: true 
    });
  }
});

// Handle process termination gracefully
process.on('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  client.destroy();
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  client.destroy();
  process.exit(0);
});

// Start the bot
registerCommands()
  .then(() => client.login(env.DISCORD_BOT_TOKEN))
  .catch((error) => {
    logger.error('Failed to start bot', { error });
    process.exit(1);
  }); 