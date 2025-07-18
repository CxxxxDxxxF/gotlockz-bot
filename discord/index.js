#!/usr/bin/env node

import { Client, GatewayIntentBits, Collection } from 'discord.js';
import { config } from 'dotenv';
import { logger } from './utils/logger.js';
import { commandRouter } from './handlers/command-router.js';
import { messageHandler } from './handlers/message-handler.js';
import { botSetup } from './config/bot-setup.js';
import { healthCheck } from './utils/health-check.js';

// Load environment variables
config();

class GotLockzDiscordBot {
  constructor() {
    this.client = new Client({
      intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers
      ]
    });
    
    this.commands = new Collection();
    this.isReady = false;
  }

  async initialize() {
    try {
      logger.info('🚀 Initializing GotLockz Discord Bot (M4 Mac)...');
      
      // Setup bot configuration
      await botSetup(this.client);
      
      // Register event handlers
      this.registerEventHandlers();
      
      // Initialize command router
      await commandRouter.initialize(this.client);
      
      // Initialize message handler
      await messageHandler.initialize(this.client);
      
      // Start health check
      healthCheck.start();
      
      logger.info('✅ Bot initialization complete');
      
    } catch (error) {
      logger.error('❌ Bot initialization failed:', error);
      process.exit(1);
    }
  }

  registerEventHandlers() {
    this.client.once('ready', () => {
      this.isReady = true;
      logger.info(`🤖 ${this.client.user.tag} is ready! (M4 Mac)`);
      logger.info(`📊 Serving ${this.client.guilds.cache.size} guilds`);
    });

    this.client.on('interactionCreate', async (interaction) => {
      try {
        await commandRouter.handleInteraction(interaction);
      } catch (error) {
        logger.error('Interaction handling error:', error);
        await interaction.reply({ 
          content: 'Sorry, something went wrong processing your command.', 
          ephemeral: true 
        });
      }
    });

    this.client.on('messageCreate', async (message) => {
      try {
        await messageHandler.handleMessage(message);
      } catch (error) {
        logger.error('Message handling error:', error);
      }
    });

    this.client.on('error', (error) => {
      logger.error('Discord client error:', error);
    });

    process.on('SIGINT', () => {
      logger.info('🛑 Shutting down bot...');
      this.client.destroy();
      process.exit(0);
    });

    process.on('SIGTERM', () => {
      logger.info('🛑 Shutting down bot...');
      this.client.destroy();
      process.exit(0);
    });
  }

  async start() {
    try {
      await this.initialize();
      await this.client.login(process.env.DISCORD_TOKEN);
    } catch (error) {
      logger.error('❌ Failed to start bot:', error);
      process.exit(1);
    }
  }
}

// Start the bot
const bot = new GotLockzDiscordBot();
bot.start().catch((error) => {
  logger.error('❌ Bot startup failed:', error);
  process.exit(1);
}); 