/**
 * Command Registration Tests
 * Ensures all commands in config are registered and match their definitions.
 */
import { readdirSync } from 'fs';
import { join } from 'path';
import commandsConfig from '../src/config/commands.json';

// Mock environment variables
process.env['DISCORD_BOT_TOKEN'] = 'test-token';
process.env['OPENAI_API_KEY'] = 'test-openai-key';

const commandsDir = join(__dirname, '../src/commands');

describe('Command Registration', () => {
  const commandFiles = readdirSync(commandsDir).filter(f => f.endsWith('.ts'));
  const commandModules: Record<string, any> = {};

  for (const file of commandFiles) {
    const mod = require(join(commandsDir, file));
    // Grab the plain object via toJSON()
    commandModules[file.replace('.ts', '')] = mod.data.toJSON();
  }

  it('should have a command module for every config entry', () => {
    for (const cfg of commandsConfig.commands) {
      expect(commandModules).toHaveProperty(cfg.name);
    }
  });

  it('should match command names and descriptions', () => {
    for (const cfg of commandsConfig.commands) {
      const json = commandModules[cfg.name];
      expect(json.name).toBe(cfg.name);
      expect(json.description).toBe(cfg.description);
    }
  });

  it('should have correct option definitions for pick command', () => {
    const pickCfg = commandsConfig.commands.find(c => c.name === 'pick');
    const json = commandModules['pick'];
    expect(Array.isArray(json.options)).toBe(true);
    expect(json.options).toHaveLength(pickCfg?.options.length ?? 0);

    // compare each option
    for (let i = 0; i < (pickCfg?.options.length ?? 0); i++) {
      const optCfg = pickCfg?.options[i];
      const optJson = json.options[i];
      if (!optCfg || !optJson) continue;
      expect(optJson.name).toBe(optCfg.name);
      if ('required' in optCfg) {
        expect(optJson.required).toBe(optCfg.required);
      }
      expect(optJson.type).toBeDefined();
    }
  });
}); 