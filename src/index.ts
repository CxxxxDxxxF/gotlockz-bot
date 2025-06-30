import { Client, GatewayIntentBits, REST, Routes, Collection, Interaction } from 'discord.js';
import { getEnv } from './utils/env';
import { data as pickData, execute as pickExecute } from './commands/pick';
import { data as adminData, execute as adminExecute } from './commands/admin';
import { getForecast } from './services/weatherService';
import express from 'express';

// Deployment test - verifying environment variables and health endpoint
const { DISCORD_BOT_TOKEN } = getEnv();
const CLIENT_ID = process.env['DISCORD_CLIENT_ID'] || '';
const GUILD_ID = process.env['DISCORD_GUILD_ID'] || '';

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent],
});

const commands = [pickData, adminData];
const commandHandlers = new Collection<string, any>();
commandHandlers.set('pick', pickExecute);
commandHandlers.set('admin', adminExecute);

const app = express();
const PORT = process.env['PORT'] ? Number(process.env['PORT']) : 3000;

app.get('/health', (_req: express.Request, res: express.Response) => {
  res.json({ status: 'ok', uptime: process.uptime() });
});

// Weather endpoint to test OpenWeatherMap integration
app.get('/weather', async (req: express.Request, res: express.Response) => {
  try {
    const location = req.query.location as string || 'New York';
    console.log(`🔍 Fetching weather for ${location}`);
    
    const weather = await getForecast(location);
    
    if (weather) {
      console.log(`✅ Weather fetched successfully for ${location}`);
      res.json({
        location,
        temperature: weather.temp,
        wind_speed: weather.wind,
        units: 'imperial',
        timestamp: new Date().toISOString()
      });
    } else {
      console.log(`❌ Failed to fetch weather for ${location}`);
      res.status(500).json({
        error: 'Failed to fetch weather data',
        location,
        message: 'Check if OPENWEATHERMAP_KEY is set correctly'
      });
    }
  } catch (error) {
    console.error('Weather endpoint error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

app.listen(PORT, () => {
  console.log(`Health endpoint listening on port ${PORT}`);
  console.log(`Weather endpoint available at /weather?location=CityName`);
});

async function registerCommands() {
  const rest = new REST({ version: '10' }).setToken(DISCORD_BOT_TOKEN);
  const body = commands.map(cmd => cmd.toJSON());
  if (GUILD_ID) {
    await rest.put(Routes.applicationGuildCommands(CLIENT_ID, GUILD_ID), { body });
    console.log('Registered guild commands');
  } else {
    await rest.put(Routes.applicationCommands(CLIENT_ID), { body });
    console.log('Registered global commands');
  }
}

client.once('ready', () => {
  console.log(`Logged in as ${client.user?.tag}`);
  console.log('Bot is ready and analysis service is up!');
});

client.on('interactionCreate', async (interaction: Interaction) => {
  if (!interaction.isChatInputCommand()) return;
  const handler = commandHandlers.get(interaction.commandName);
  if (!handler) return;
  if (interaction.commandName === 'admin') {
    await handler(interaction, client);
  } else {
    await handler(interaction);
  }
});

registerCommands()
  .then(() => client.login(DISCORD_BOT_TOKEN))
  .catch(console.error); 