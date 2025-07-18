#!/usr/bin/env node

import { REST, Routes } from 'discord.js';
import { config } from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
config();

class CommandDeployer {
  constructor() {
    this.commands = [];
    this.rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
  }

  async loadCommands() {
    try {
      const commandsPath = path.join(__dirname, '..', 'commands');
      const commandFiles = await fs.readdir(commandsPath);
      
      for (const file of commandFiles) {
        if (file.endsWith('.js') && !file.startsWith('.')) {
          const filePath = path.join(commandsPath, file);
          const command = await import(filePath);
          
          if (command.data && command.execute) {
            this.commands.push(command.data.toJSON());
            logger.info(`Loaded command: ${command.data.name}`);
          } else {
            logger.warn(`Invalid command file: ${file}`);
          }
        }
      }
      
      logger.info(`Loaded ${this.commands.length} commands`);
      
    } catch (error) {
      logger.error('Error loading commands:', error);
      throw error;
    }
  }

  async deployCommands() {
    try {
      logger.info('🚀 Starting command deployment...');
      
      // Load commands
      await this.loadCommands();
      
      if (this.commands.length === 0) {
        logger.warn('No commands found to deploy');
        return;
      }
      
      const clientId = process.env.DISCORD_CLIENT_ID;
      const guildId = process.env.DISCORD_GUILD_ID;
      
      if (!clientId) {
        throw new Error('DISCORD_CLIENT_ID is required');
      }
      
      // Deploy to guild (faster for development)
      if (guildId) {
        logger.info(`Deploying ${this.commands.length} commands to guild ${guildId}...`);
        
        await this.rest.put(
          Routes.applicationGuildCommands(clientId, guildId),
          { body: this.commands }
        );
        
        logger.info('✅ Commands deployed to guild successfully');
      }
      
      // Deploy globally (slower, but works across all guilds)
      if (process.env.NODE_ENV === 'production' || process.env.DEPLOY_GLOBAL === 'true') {
        logger.info(`Deploying ${this.commands.length} commands globally...`);
        
        await this.rest.put(
          Routes.applicationCommands(clientId),
          { body: this.commands }
        );
        
        logger.info('✅ Commands deployed globally successfully');
      }
      
      logger.info('🎉 Command deployment complete!');
      
    } catch (error) {
      logger.error('❌ Command deployment failed:', error);
      throw error;
    }
  }

  async listCommands() {
    try {
      const clientId = process.env.DISCORD_CLIENT_ID;
      const guildId = process.env.DISCORD_GUILD_ID;
      
      if (!clientId) {
        throw new Error('DISCORD_CLIENT_ID is required');
      }
      
      let commands;
      
      if (guildId) {
        commands = await this.rest.get(
          Routes.applicationGuildCommands(clientId, guildId)
        );
      } else {
        commands = await this.rest.get(
          Routes.applicationCommands(clientId)
        );
      }
      
      logger.info(`Found ${commands.length} deployed commands:`);
      
      for (const command of commands) {
        logger.info(`  - ${command.name}: ${command.description}`);
      }
      
      return commands;
      
    } catch (error) {
      logger.error('Error listing commands:', error);
      throw error;
    }
  }

  async deleteCommand(commandId) {
    try {
      const clientId = process.env.DISCORD_CLIENT_ID;
      const guildId = process.env.DISCORD_GUILD_ID;
      
      if (!clientId) {
        throw new Error('DISCORD_CLIENT_ID is required');
      }
      
      if (guildId) {
        await this.rest.delete(
          Routes.applicationGuildCommand(clientId, guildId, commandId)
        );
      } else {
        await this.rest.delete(
          Routes.applicationCommand(clientId, commandId)
        );
      }
      
      logger.info(`Deleted command: ${commandId}`);
      
    } catch (error) {
      logger.error('Error deleting command:', error);
      throw error;
    }
  }

  async deleteAllCommands() {
    try {
      const clientId = process.env.DISCORD_CLIENT_ID;
      const guildId = process.env.DISCORD_GUILD_ID;
      
      if (!clientId) {
        throw new Error('DISCORD_CLIENT_ID is required');
      }
      
      let commands;
      
      if (guildId) {
        commands = await this.rest.get(
          Routes.applicationGuildCommands(clientId, guildId)
        );
        
        for (const command of commands) {
          await this.rest.delete(
            Routes.applicationGuildCommand(clientId, guildId, command.id)
          );
        }
      } else {
        commands = await this.rest.get(
          Routes.applicationCommands(clientId)
        );
        
        for (const command of commands) {
          await this.rest.delete(
            Routes.applicationCommand(clientId, command.id)
          );
        }
      }
      
      logger.info(`Deleted ${commands.length} commands`);
      
    } catch (error) {
      logger.error('Error deleting all commands:', error);
      throw error;
    }
  }
}

// Main execution
async function main() {
  const deployer = new CommandDeployer();
  
  const command = process.argv[2];
  
  try {
    switch (command) {
      case 'deploy':
        await deployer.deployCommands();
        break;
      case 'list':
        await deployer.listCommands();
        break;
      case 'delete':
        const commandId = process.argv[3];
        if (!commandId) {
          logger.error('Command ID required for delete operation');
          process.exit(1);
        }
        await deployer.deleteCommand(commandId);
        break;
      case 'delete-all':
        await deployer.deleteAllCommands();
        break;
      default:
        logger.info('Usage: node deploy-commands.js [deploy|list|delete <id>|delete-all]');
        process.exit(1);
    }
  } catch (error) {
    logger.error('Deployment failed:', error);
    process.exit(1);
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { CommandDeployer }; 