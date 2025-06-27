import { Client, GatewayIntentBits, REST, Routes, Collection, Interaction } from 'discord.js';
import { getEnv } from './utils/env';
import { data as pickData, execute as pickExecute } from './commands/pick';
import { data as adminData, execute as adminExecute } from './commands/admin';
import express from 'express';

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

app.listen(PORT, () => {
  console.log(`Health endpoint listening on port ${PORT}`);
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