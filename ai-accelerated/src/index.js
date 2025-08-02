import { Client, Events, GatewayIntentBits, Collection, Routes } from 'discord.js';
import { REST } from '@discordjs/rest';
import { logger, logError } from './utils/logger.js';
import { setupInteractionHandler } from './handlers/interactionHandler.js';
import express from 'express';
import { getSystemStats } from './utils/systemStats.js';

// Create Express app for health checks and logging
const app = express();
const PORT = process.env.PORT || 3000;

// Health check endpoint for Render
app.get('/health', (req, res) => {
  try {
    const stats = getSystemStats();
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      stats
    });
  } catch (error) {
    logError(error, { endpoint: '/health' });
    res.status(500).json({
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Logs endpoint for debugging (only in development)
if (process.env.NODE_ENV === 'development') {
  app.get('/logs', (req, res) => {
    try {
      const fs = require('fs');
      const path = require('path');
      
      const logFiles = ['logs/error.log', 'logs/combined.log'];
      const logs = {};
      
      logFiles.forEach(file => {
        if (fs.existsSync(file)) {
          logs[file] = fs.readFileSync(file, 'utf8').split('\n').slice(-50).join('\n');
        }
      });
      
      res.json(logs);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
}

// Start Express server
app.listen(PORT, () => {
  console.log(`🚀 Health check server running on port ${PORT}`);
  logger.info('Health check server started', { port: PORT });
});

// Create Discord client
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Global error handling
process.on('uncaughtException', (error) => {
  logError(error, { type: 'uncaughtException' });
  console.error('💥 Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  logError(new Error(`Unhandled Rejection: ${reason}`), { 
    type: 'unhandledRejection',
    promise: promise.toString()
  });
  console.error('💥 Unhandled Rejection:', reason);
});

// Client error handling
client.on('error', (error) => {
  logError(error, { type: 'client_error' });
  console.error('💥 Discord client error:', error);
});

client.on('warn', (warning) => {
  logger.warn('Discord client warning:', warning);
  console.warn('⚠️ Discord client warning:', warning);
});

// Command collection
client.commands = new Collection();

// Load commands
const loadCommands = async () => {
  try {
    console.log('📦 Loading commands...');
    
    const commandFiles = [
      './src/commands/pick.js',
      './src/commands/admin.js',
      './src/commands/economy.js',
      './src/commands/leveling.js',
      './src/commands/automod.js',
      './src/commands/test-ocr.js'
    ];

    for (const file of commandFiles) {
      try {
        const { data, execute } = await import(file);
        client.commands.set(data.name, { data, execute });
        console.log(`✅ Loaded command: ${data.name}`);
        logger.info('Command loaded', { command: data.name });
      } catch (error) {
        logError(error, { commandFile: file });
        console.error(`❌ Failed to load command from ${file}:`, error.message);
      }
    }

    console.log(`✅ Loaded ${client.commands.size} commands`);
  } catch (error) {
    logError(error, { operation: 'loadCommands' });
    throw error;
  }
};

// Setup interaction handler
const setupBot = async () => {
  try {
    console.log('🔧 Setting up interaction handler...');
    setupInteractionHandler(client);
    console.log('✅ Interaction handler setup complete');
  } catch (error) {
    logError(error, { operation: 'setupInteractionHandler' });
    throw error;
  }
};

// Bot ready event
client.once(Events.ClientReady, async () => {
  try {
    console.log(`🤖 Bot logged in as ${client.user.tag}`);
    logger.info('Bot ready', { 
      botId: client.user.id,
      botTag: client.user.tag,
      guildCount: client.guilds.cache.size
    });

    // Load commands after bot is ready
    await loadCommands();
    await setupBot();

    // Deploy commands to Discord (only in production)
    if (process.env.NODE_ENV === 'production') {
      try {
        console.log('📝 Deploying commands to Discord...');
        const { execSync } = await import('child_process');
        execSync('node render-deploy-commands.js', { stdio: 'inherit' });
        console.log('✅ Commands deployed successfully');
      } catch (deployError) {
        console.warn('⚠️ Command deployment failed (this is okay for development):', deployError.message);
      }
    }

    console.log('🎉 Bot setup complete!');
  } catch (error) {
    logError(error, { operation: 'botReady' });
    console.error('💥 Bot setup failed:', error);
    process.exit(1);
  }
});

// Login with error handling
const startBot = async () => {
  try {
    console.log('🔑 Logging in to Discord...');
    
    if (!process.env.DISCORD_TOKEN) {
      throw new Error('DISCORD_TOKEN environment variable is required');
    }

    await client.login(process.env.DISCORD_TOKEN);
    console.log('✅ Discord login successful');
  } catch (error) {
    logError(error, { operation: 'botLogin' });
    console.error('💥 Failed to login to Discord:', error.message);
    process.exit(1);
  }
};

// Start the bot
startBot();
