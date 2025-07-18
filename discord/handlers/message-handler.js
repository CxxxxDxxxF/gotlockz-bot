import { logger } from '../utils/logger.js';
import { postGenerator } from '../services/post-generator.js';
import { messageValidator } from '../validators/message-validator.js';
import { rateLimiter } from '../utils/rate-limiter.js';

class MessageHandler {
  constructor() {
    this.client = null;
    this.initialized = false;
  }

  async initialize(client) {
    if (this.initialized) return;
    
    this.client = client;
    this.initialized = true;
    logger.info('📨 Message handler initialized');
  }

  async handleMessage(message) {
    // Ignore bot messages
    if (message.author.bot) return;

    try {
      // Check rate limiting for message processing
      const rateLimitResult = await rateLimiter.checkLimit(message.author.id, 'message');
      if (!rateLimitResult.allowed) {
        logger.debug(`Rate limit exceeded for user ${message.author.tag}`);
        return;
      }

      // Validate message content
      const validationResult = await messageValidator.validate(message);
      if (!validationResult.isValid) {
        logger.debug(`Invalid message from ${message.author.tag}: ${validationResult.reason}`);
        return;
      }

      // Check if message contains JSON data (from OCR processing)
      if (this.isJsonData(message.content)) {
        await this.handleJsonData(message);
        return;
      }

      // Check for specific keywords or patterns
      if (this.isBettingAnalysisRequest(message.content)) {
        await this.handleBettingAnalysisRequest(message);
        return;
      }

      // Log message for debugging
      logger.debug(`Message from ${message.author.tag}: ${message.content.substring(0, 100)}...`);

    } catch (error) {
      logger.error('Error handling message:', error);
    }
  }

  isJsonData(content) {
    try {
      const trimmed = content.trim();
      return trimmed.startsWith('{') && trimmed.endsWith('}') && JSON.parse(trimmed);
    } catch {
      return false;
    }
  }

  isBettingAnalysisRequest(content) {
    const keywords = [
      'gotlockz family',
      'free play is here',
      'betting analysis',
      'mlb pick',
      'lock of the day'
    ];
    
    return keywords.some(keyword => 
      content.toLowerCase().includes(keyword.toLowerCase())
    );
  }

  async handleJsonData(message) {
    try {
      const jsonData = JSON.parse(message.content);
      
      // Validate JSON structure
      if (!this.isValidBettingData(jsonData)) {
        logger.warn(`Invalid betting data structure from ${message.author.tag}`);
        return;
      }

      // Generate formatted betting post
      const formattedPost = await postGenerator.generateBettingPost(jsonData);
      
      // Send the formatted post
      await message.channel.send(formattedPost);
      
      logger.info(`Generated betting post from JSON data for ${message.author.tag}`);

    } catch (error) {
      logger.error('Error processing JSON data:', error);
    }
  }

  async handleBettingAnalysisRequest(message) {
    try {
      // This could trigger a request to the OCR processing module
      // For now, we'll just acknowledge the request
      await message.reply('Betting analysis request received. Processing...');
      
      logger.info(`Betting analysis requested by ${message.author.tag}`);

    } catch (error) {
      logger.error('Error handling betting analysis request:', error);
    }
  }

  isValidBettingData(data) {
    // Basic validation for betting data structure
    const requiredFields = ['teams', 'analysis', 'recommendation'];
    return requiredFields.every(field => data.hasOwnProperty(field));
  }

  // Method to handle direct JSON data from OCR processing
  async processOcrData(jsonData, channel) {
    try {
      const formattedPost = await postGenerator.generateBettingPost(jsonData);
      await channel.send(formattedPost);
      
      logger.info('OCR data processed and posted successfully');
      return { success: true };
      
    } catch (error) {
      logger.error('Error processing OCR data:', error);
      return { success: false, error: error.message };
    }
  }
}

export const messageHandler = new MessageHandler(); 