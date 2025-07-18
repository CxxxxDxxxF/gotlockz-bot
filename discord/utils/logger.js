import winston from 'winston';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Custom format for console output
const consoleFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.colorize(),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let log = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(meta).length > 0) {
      log += ` ${JSON.stringify(meta)}`;
    }
    return log;
  })
);

// Custom format for file output
const fileFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '..', '..', 'logs');
import fs from 'fs';
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Create logger instance
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: fileFormat,
  defaultMeta: { 
    service: 'gotlockz-discord-bot',
    platform: 'darwin',
    architecture: 'arm64'
  },
  transports: [
    // Error log file
    new winston.transports.File({
      filename: path.join(logsDir, 'error.log'),
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    
    // Combined log file
    new winston.transports.File({
      filename: path.join(logsDir, 'combined.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    }),
    
    // Discord-specific log file
    new winston.transports.File({
      filename: path.join(logsDir, 'discord.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Add console transport for development
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: consoleFormat
  }));
}

// Custom logging methods for Discord bot
logger.discord = (message, meta = {}) => {
  logger.info(message, { ...meta, context: 'discord' });
};

logger.command = (commandName, userId, meta = {}) => {
  logger.info(`Command executed: ${commandName}`, { 
    ...meta, 
    context: 'command',
    commandName,
    userId 
  });
};

logger.interaction = (interactionType, userId, meta = {}) => {
  logger.info(`Interaction: ${interactionType}`, { 
    ...meta, 
    context: 'interaction',
    interactionType,
    userId 
  });
};

logger.error = (message, error = null, meta = {}) => {
  if (error) {
    logger.error(message, { 
      ...meta, 
      error: error.message,
      stack: error.stack 
    });
  } else {
    logger.error(message, meta);
  }
};

// Performance logging
logger.performance = (operation, duration, meta = {}) => {
  logger.info(`Performance: ${operation} took ${duration}ms`, {
    ...meta,
    context: 'performance',
    operation,
    duration
  });
};

// Memory usage logging
logger.memory = (usage, meta = {}) => {
  logger.info('Memory usage', {
    ...meta,
    context: 'memory',
    ...usage
  });
};

export { logger }; 