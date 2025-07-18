// Test setup file for Jest
const dotenv = require('dotenv');

// Load test environment variables
dotenv.config({ path: '.env.test' });

// Mock Discord.js
jest.mock('discord.js', () => ({
  SlashCommandBuilder: jest.fn().mockImplementation(() => ({
    setName: jest.fn().mockReturnThis(),
    setDescription: jest.fn().mockReturnThis(),
    addSubcommand: jest.fn().mockReturnThis(),
    addStringOption: jest.fn().mockReturnThis(),
    addAttachmentOption: jest.fn().mockReturnThis(),
    addBooleanOption: jest.fn().mockReturnThis(),
    toJSON: jest.fn().mockReturnValue({ name: 'test', description: 'test' })
  })),
  EmbedBuilder: jest.fn().mockImplementation(() => ({
    setColor: jest.fn().mockReturnThis(),
    setTitle: jest.fn().mockReturnThis(),
    setDescription: jest.fn().mockReturnThis(),
    setThumbnail: jest.fn().mockReturnThis(),
    setTimestamp: jest.fn().mockReturnThis(),
    addFields: jest.fn().mockReturnThis(),
    setFooter: jest.fn().mockReturnThis()
  })),
  Events: {
    ClientReady: 'ready',
    InteractionCreate: 'interactionCreate'
  },
  GatewayIntentBits: {
    Guilds: 1,
    GuildMessages: 2,
    MessageContent: 4
  },
  Routes: {
    applicationCommands: jest.fn(),
    applicationGuildCommands: jest.fn()
  }
}));

// Mock external APIs
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn()
}));

// Mock image processing
jest.mock('sharp', () => jest.fn().mockReturnValue({
  resize: jest.fn().mockReturnThis(),
  grayscale: jest.fn().mockReturnThis(),
  normalize: jest.fn().mockReturnThis(),
  sharpen: jest.fn().mockReturnThis(),
  png: jest.fn().mockReturnThis(),
  toBuffer: jest.fn().mockResolvedValue(Buffer.from('test')),
  toFile: jest.fn().mockResolvedValue()
}));

// Mock OCR
jest.mock('tesseract.js', () => ({
  createWorker: jest.fn().mockResolvedValue({
    loadLanguage: jest.fn().mockResolvedValue(),
    initialize: jest.fn().mockResolvedValue(),
    setParameters: jest.fn().mockResolvedValue(),
    recognize: jest.fn().mockResolvedValue({
      data: {
        text: 'Test OCR text',
        confidence: 85
      }
    }),
    terminate: jest.fn().mockResolvedValue()
  })
}));

// Global test utilities
global.testUtils = {
  createMockInteraction: (options = {}) => ({
    isChatInputCommand: jest.fn().mockReturnValue(true),
    commandName: options.commandName || 'test',
    options: {
      getSubcommand: jest.fn().mockReturnValue(options.subcommand),
      getString: jest.fn().mockReturnValue(options.stringValue),
      getAttachment: jest.fn().mockReturnValue(options.attachment),
      getBoolean: jest.fn().mockReturnValue(options.booleanValue)
    },
    user: {
      id: options.userId || '123456789'
    },
    reply: jest.fn().mockResolvedValue(),
    editReply: jest.fn().mockResolvedValue(),
    deferReply: jest.fn().mockResolvedValue(),
    followUp: jest.fn().mockResolvedValue(),
    ...options
  }),

  createMockClient: () => ({
    ws: {
      ping: 50
    },
    guilds: {
      cache: {
        size: 1
      }
    }
  })
}; 