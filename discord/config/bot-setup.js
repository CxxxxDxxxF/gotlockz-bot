import { logger } from '../utils/logger.js';

class BotSetup {
  constructor() {
    this.initialized = false;
  }

  async setup(client) {
    if (this.initialized) return;
    
    try {
      logger.info('🔧 Setting up Discord bot configuration...');
      
      // Validate environment variables
      this.validateEnvironment();
      
      // Set up bot presence
      this.setupPresence(client);
      
      // Set up error handling
      this.setupErrorHandling(client);
      
      this.initialized = true;
      logger.info('✅ Bot setup complete');
      
    } catch (error) {
      logger.error('❌ Bot setup failed:', error);
      throw error;
    }
  }

  validateEnvironment() {
    const requiredEnvVars = [
      'DISCORD_TOKEN',
      'DISCORD_CLIENT_ID',
      'DISCORD_GUILD_ID'
    ];

    const missing = requiredEnvVars.filter(varName => !process.env[varName]);
    
    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }

    logger.info('✅ Environment variables validated');
  }

  setupPresence(client) {
    const activities = [
      { name: 'MLB Betting Analysis', type: 2 }, // Watching
      { name: 'GotLockz Family', type: 0 }, // Playing
      { name: 'Free Plays Daily', type: 3 }, // Listening
      { name: '21+ Only', type: 0 } // Playing
    ];

    let currentIndex = 0;

    // Set initial presence
    client.user.setPresence({
      activities: [activities[currentIndex]],
      status: 'online'
    });

    // Rotate presence every 30 seconds
    setInterval(() => {
      currentIndex = (currentIndex + 1) % activities.length;
      client.user.setPresence({
        activities: [activities[currentIndex]],
        status: 'online'
      });
    }, 30000);

    logger.info('✅ Bot presence configured');
  }

  setupErrorHandling(client) {
    client.on('warn', (warning) => {
      logger.warn('Discord client warning:', warning);
    });

    client.on('debug', (info) => {
      logger.debug('Discord client debug:', info);
    });

    client.on('disconnect', () => {
      logger.warn('Discord client disconnected');
    });

    client.on('reconnecting', () => {
      logger.info('Discord client reconnecting...');
    });

    client.on('resume', (replayed) => {
      logger.info(`Discord client resumed, replayed ${replayed} events`);
    });

    logger.info('✅ Error handling configured');
  }

  getBotConfig() {
    return {
      token: process.env.DISCORD_TOKEN,
      clientId: process.env.DISCORD_CLIENT_ID,
      guildId: process.env.DISCORD_GUILD_ID,
      intents: [
        'Guilds',
        'GuildMessages',
        'MessageContent',
        'GuildMembers'
      ],
      partials: [
        'Message',
        'Channel',
        'Reaction'
      ]
    };
  }

  getDeploymentConfig() {
    return {
      token: process.env.DISCORD_TOKEN,
      clientId: process.env.DISCORD_CLIENT_ID,
      guildId: process.env.DISCORD_GUILD_ID,
      commandsPath: './commands',
      global: process.env.NODE_ENV === 'production'
    };
  }
}

export const botSetup = new BotSetup(); 