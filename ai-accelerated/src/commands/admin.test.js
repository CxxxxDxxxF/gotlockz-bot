import { execute, data } from './admin.js';
import { getSystemStats } from '../utils/systemStats.js';

// Mock dependencies
jest.mock('../utils/systemStats.js');
jest.mock('../utils/logger.js');

describe('Admin Command', () => {
  let mockInteraction;

  beforeEach(() => {
    mockInteraction = {
      options: {
        getSubcommand: jest.fn()
      },
      user: {
        id: '123456789'
      },
      reply: jest.fn().mockResolvedValue(),
      editReply: jest.fn().mockResolvedValue(),
      deferReply: jest.fn().mockResolvedValue()
    };

    // Mock environment variable
    process.env.OWNER_ID = '123456789';
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('ping subcommand', () => {
    test('should respond with ping information', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('ping');
      mockInteraction.client = {
        ws: {
          ping: 50
        }
      };

      await execute(mockInteraction);

      expect(mockInteraction.reply).toHaveBeenCalledWith('🏓 Pinging...');
      expect(mockInteraction.editReply).toHaveBeenCalledWith(
        expect.stringContaining('🏓 Pong! Latency:')
      );
    });
  });

  describe('status subcommand', () => {
    test('should return system status', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('status');
      
      const mockStats = {
        uptime: '1h 30m',
        memory: '50MB',
        cpu: '2500ms',
        commands: '2',
        servers: '1'
      };

      getSystemStats.mockReturnValue(mockStats);

      await execute(mockInteraction);

      expect(mockInteraction.deferReply).toHaveBeenCalled();
      expect(mockInteraction.editReply).toHaveBeenCalledWith({
        embeds: [{
          color: 0x00ff00,
          title: '🤖 Bot Status',
          fields: [
            { name: '🟢 Status', value: 'Online', inline: true },
            { name: '⏱️ Uptime', value: '1h 30m', inline: true },
            { name: '💾 Memory', value: '50MB', inline: true },
            { name: '🖥️ CPU', value: '2500ms', inline: true },
            { name: '📊 Commands', value: '2', inline: true },
            { name: '👥 Servers', value: '1', inline: true }
          ],
          timestamp: expect.any(String)
        }]
      });
    });
  });

  describe('stats subcommand', () => {
    test('should return usage statistics', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('stats');

      await execute(mockInteraction);

      expect(mockInteraction.deferReply).toHaveBeenCalled();
      expect(mockInteraction.editReply).toHaveBeenCalledWith({
        embeds: [{
          color: 0x0099ff,
          title: '📊 Bot Usage Statistics',
          fields: [
            { name: '🎯 Total Picks', value: '1,234', inline: true },
            { name: '💰 VIP Plays', value: '567', inline: true },
            { name: '🎁 Free Plays', value: '789', inline: true },
            { name: '🎰 Lotto Tickets', value: '123', inline: true },
            { name: '📈 Success Rate', value: '87.5%', inline: true },
            { name: '⚡ Avg Response', value: '2.3s', inline: true }
          ],
          timestamp: expect.any(String)
        }]
      });
    });
  });

  describe('restart subcommand', () => {
    test('should allow restart for owner', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('restart');
      mockInteraction.user.id = '123456789'; // Owner ID

      // Mock process.exit
      const originalExit = process.exit;
      process.exit = jest.fn();

      await execute(mockInteraction);

      expect(mockInteraction.reply).toHaveBeenCalledWith('🔄 Restarting bot...');
      expect(process.exit).toHaveBeenCalledWith(0);

      // Restore process.exit
      process.exit = originalExit;
    });

    test('should deny restart for non-owner', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('restart');
      mockInteraction.user.id = '987654321'; // Non-owner ID

      await execute(mockInteraction);

      expect(mockInteraction.reply).toHaveBeenCalledWith({
        content: '❌ You do not have permission to restart the bot.',
        ephemeral: true
      });
    });
  });

  describe('error handling', () => {
    test('should handle unknown subcommand', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('unknown');

      await execute(mockInteraction);

      expect(mockInteraction.reply).toHaveBeenCalledWith('❌ Unknown subcommand.');
    });

    test('should handle errors gracefully', async () => {
      mockInteraction.options.getSubcommand.mockReturnValue('status');
      mockInteraction.deferReply.mockRejectedValue(new Error('Test error'));

      await execute(mockInteraction);

      expect(mockInteraction.reply).toHaveBeenCalledWith({
        content: '❌ An error occurred while executing this command.',
        ephemeral: true
      });
    });
  });

  describe('command data', () => {
    test('should have correct command structure', () => {
      expect(data.name).toBe('admin');
      expect(data.description).toBe('Admin commands for bot management');
      expect(data.options).toHaveLength(4);
      
      const subcommandNames = data.options.map(option => option.name);
      expect(subcommandNames).toContain('ping');
      expect(subcommandNames).toContain('status');
      expect(subcommandNames).toContain('stats');
      expect(subcommandNames).toContain('restart');
    });
  });
}); 