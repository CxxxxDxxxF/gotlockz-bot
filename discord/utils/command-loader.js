import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { logger } from './logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class CommandLoader {
  constructor() {
    this.commandsPath = path.join(__dirname, '..', 'commands');
    this.loadedCommands = new Map();
  }

  async loadCommands() {
    try {
      const commandFiles = [];
      
      // Read all files in the commands directory
      const files = await fs.readdir(this.commandsPath);
      
      for (const file of files) {
        if (file.endsWith('.js') && !file.startsWith('.')) {
          const filePath = path.join(this.commandsPath, file);
          commandFiles.push(filePath);
        }
      }
      
      logger.info(`Found ${commandFiles.length} command files`);
      return commandFiles;
      
    } catch (error) {
      logger.error('Error loading commands:', error);
      throw error;
    }
  }

  async loadCommand(filePath) {
    try {
      const command = await import(filePath);
      
      // Validate command structure
      if (!command.data || !command.execute) {
        logger.warn(`Invalid command file: ${filePath}`);
        return null;
      }
      
      const commandName = command.data.name;
      this.loadedCommands.set(commandName, {
        ...command,
        filePath
      });
      
      logger.debug(`Loaded command: ${commandName}`);
      return command;
      
    } catch (error) {
      logger.error(`Error loading command from ${filePath}:`, error);
      return null;
    }
  }

  async reloadCommand(commandName) {
    const command = this.loadedCommands.get(commandName);
    if (!command) {
      logger.warn(`Command not found for reload: ${commandName}`);
      return false;
    }
    
    try {
      // Clear the module cache
      delete require.cache[require.resolve(command.filePath)];
      
      // Reload the command
      const reloadedCommand = await this.loadCommand(command.filePath);
      return reloadedCommand !== null;
      
    } catch (error) {
      logger.error(`Error reloading command ${commandName}:`, error);
      return false;
    }
  }

  getLoadedCommands() {
    return this.loadedCommands;
  }

  getCommand(commandName) {
    return this.loadedCommands.get(commandName);
  }

  async validateCommands() {
    const validationResults = [];
    
    for (const [name, command] of this.loadedCommands) {
      const result = {
        name,
        valid: true,
        errors: []
      };
      
      // Check required properties
      if (!command.data) {
        result.valid = false;
        result.errors.push('Missing data property');
      }
      
      if (!command.execute) {
        result.valid = false;
        result.errors.push('Missing execute function');
      }
      
      // Check data structure
      if (command.data) {
        if (!command.data.name) {
          result.valid = false;
          result.errors.push('Missing command name in data');
        }
        
        if (!command.data.description) {
          result.valid = false;
          result.errors.push('Missing command description in data');
        }
      }
      
      validationResults.push(result);
      
      if (!result.valid) {
        logger.warn(`Command validation failed for ${name}:`, result.errors);
      }
    }
    
    return validationResults;
  }
}

export const commandLoader = new CommandLoader();

// Export the loadCommands function for backward compatibility
export const loadCommands = () => commandLoader.loadCommands(); 