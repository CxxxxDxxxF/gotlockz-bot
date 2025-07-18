import winston from 'winston';

// Enhanced logger configuration for Render deployment
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp({
      format: 'YYYY-MM-DD HH:mm:ss'
    }),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'gotlockz-bot' },
  transports: [
    // Console transport for local development and Render logs
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple(),
        winston.format.printf(({ timestamp, level, message, service, ...meta }) => {
          let logMessage = `${timestamp} [${level.toUpperCase()}] ${service}: ${message}`;
          
          // Add stack trace for errors
          if (meta.stack) {
            logMessage += `\n${meta.stack}`;
          }
          
          // Add additional metadata
          if (Object.keys(meta).length > 0) {
            const metaStr = JSON.stringify(meta, null, 2);
            logMessage += `\nMetadata: ${metaStr}`;
          }
          
          return logMessage;
        })
      )
    }),
    
    // File transport for persistent logs (useful for debugging)
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      )
    }),
    
    // Combined log file
    new winston.transports.File({
      filename: 'logs/combined.log',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
      )
    })
  ]
});

// Add error handling for the logger itself
logger.on('error', (error) => {
  console.error('Logger error:', error);
});

// Enhanced error logging function
export const logError = (error, context = {}) => {
  const errorInfo = {
    message: error.message,
    stack: error.stack,
    name: error.name,
    code: error.code,
    context,
    timestamp: new Date().toISOString(),
    service: 'gotlockz-bot'
  };

  logger.error('Application Error', errorInfo);
  
  // Also log to console for immediate visibility in Render
  console.error('🚨 CRITICAL ERROR:', {
    message: error.message,
    stack: error.stack,
    context,
    timestamp: new Date().toISOString()
  });
};

// Enhanced command logging
export const logCommand = (commandName, userId, options = {}, result = null) => {
  logger.info('Command Executed', {
    command: commandName,
    userId,
    options,
    result: result ? 'success' : 'failure',
    timestamp: new Date().toISOString()
  });
};

// Enhanced service logging
export const logService = (serviceName, operation, data = {}, error = null) => {
  const logData = {
    service: serviceName,
    operation,
    data,
    timestamp: new Date().toISOString()
  };

  if (error) {
    logData.error = {
      message: error.message,
      stack: error.stack
    };
    logger.error('Service Error', logData);
  } else {
    logger.info('Service Operation', logData);
  }
};

export { logger };
