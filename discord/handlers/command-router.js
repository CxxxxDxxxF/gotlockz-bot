import { Collection } from 'discord.js';
import { logger } from '../utils/logger.js';
import { loadCommands } from '../utils/command-loader.js';
import { rateLimiter } from '../utils/rate-limiter.js';

class CommandRouter {
  constructor() {
    this.commands = new Collection();
    this.client = null;
    this.initialized = false;
  }

  async initialize(client) {
    if (this.initialized) return;
    
    this.client = client;
    
    try {
      // Load all commands from the commands directory
      await this.loadCommands();
      logger.info(`📋 Loaded ${this.commands.size} commands`);
      this.initialized = true;
    } catch (error) {
      logger.error('Failed to initialize command router:', error);
      throw error;
    }
  }

  async loadCommands() {
    try {
      const commandFiles = await loadCommands();
      
      for (const file of commandFiles) {
        const command = await import(file);
        
        if (command.data && command.execute) {
          this.commands.set(command.data.name, command);
          logger.debug(`Loaded command: ${command.data.name}`);
        } else {
          logger.warn(`Invalid command file: ${file}`);
        }
      }
    } catch (error) {
      logger.error('Error loading commands:', error);
      throw error;
    }
  }

  async handleInteraction(interaction) {
    if (!interaction.isChatInputCommand()) return;

    const command = this.commands.get(interaction.commandName);

    if (!command) {
      logger.warn(`Unknown command: ${interaction.commandName}`);
      await interaction.reply({ 
        content: 'This command is not available.', 
        ephemeral: true 
      });
      return;
    }

    // Check rate limiting
    const rateLimitResult = await rateLimiter.checkLimit(interaction.user.id, interaction.commandName);
    if (!rateLimitResult.allowed) {
      await interaction.reply({ 
        content: `Rate limit exceeded. Please wait ${rateLimitResult.retryAfter} seconds.`, 
        ephemeral: true 
      });
      return;
    }

    try {
      // Defer reply for commands that might take time
      if (command.deferReply !== false) {
        await interaction.deferReply({ ephemeral: command.ephemeral || false });
      }

      // Execute the command
      await command.execute(interaction);

      // Log successful command execution
      logger.info(`Command executed: ${interaction.commandName} by ${interaction.user.tag}`);

    } catch (error) {
      logger.error(`Error executing command ${interaction.commandName}:`, error);
      
      const errorMessage = 'An error occurred while executing this command.';
      
      if (interaction.deferred) {
        await interaction.editReply({ content: errorMessage });
      } else {
        await interaction.reply({ 
          content: errorMessage, 
          ephemeral: true 
        });
      }
    }
  }

  getCommands() {
    return this.commands;
  }

  getCommand(name) {
    return this.commands.get(name);
  }
}

export const commandRouter = new CommandRouter(); 