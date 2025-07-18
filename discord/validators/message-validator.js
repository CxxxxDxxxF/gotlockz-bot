import { logger } from '../utils/logger.js';

class MessageValidator {
  constructor() {
    this.initialized = false;
    this.spamPatterns = [
      /(.)\1{4,}/, // Repeated characters
      /[A-Z]{10,}/, // ALL CAPS
      /(https?:\/\/[^\s]+){3,}/, // Multiple URLs
      /(.){100,}/, // Very long messages
    ];
    
    this.forbiddenWords = [
      'spam', 'scam', 'free money', 'get rich quick',
      'click here', 'limited time', 'act now'
    ];
  }

  async initialize() {
    if (this.initialized) return;
    this.initialized = true;
    logger.info('✅ Message validator initialized');
  }

  async validate(message) {
    try {
      await this.initialize();
      
      const validationResult = {
        isValid: true,
        reason: null,
        warnings: []
      };

      // Check if message is from a bot
      if (message.author.bot) {
        validationResult.isValid = false;
        validationResult.reason = 'Bot message';
        return validationResult;
      }

      // Check message length
      if (message.content.length > 2000) {
        validationResult.isValid = false;
        validationResult.reason = 'Message too long';
        return validationResult;
      }

      // Check for spam patterns
      const spamCheck = this.checkSpamPatterns(message.content);
      if (!spamCheck.isValid) {
        validationResult.isValid = false;
        validationResult.reason = spamCheck.reason;
        return validationResult;
      }

      // Check for forbidden words
      const forbiddenCheck = this.checkForbiddenWords(message.content);
      if (!forbiddenCheck.isValid) {
        validationResult.isValid = false;
        validationResult.reason = forbiddenCheck.reason;
        return validationResult;
      }

      // Check for excessive mentions
      const mentionCheck = this.checkMentions(message);
      if (!mentionCheck.isValid) {
        validationResult.isValid = false;
        validationResult.reason = mentionCheck.reason;
        return validationResult;
      }

      // Check for excessive emojis
      const emojiCheck = this.checkEmojis(message.content);
      if (!emojiCheck.isValid) {
        validationResult.warnings.push(emojiCheck.reason);
      }

      // Check for JSON data validity (if present)
      if (this.isJsonData(message.content)) {
        const jsonCheck = this.validateJsonData(message.content);
        if (!jsonCheck.isValid) {
          validationResult.isValid = false;
          validationResult.reason = jsonCheck.reason;
          return validationResult;
        }
      }

      // Log validation result
      if (!validationResult.isValid) {
        logger.warn(`Message validation failed for ${message.author.tag}:`, {
          reason: validationResult.reason,
          content: message.content.substring(0, 100)
        });
      }

      return validationResult;

    } catch (error) {
      logger.error('Error validating message:', error);
      return {
        isValid: false,
        reason: 'Validation error',
        warnings: []
      };
    }
  }

  checkSpamPatterns(content) {
    for (const pattern of this.spamPatterns) {
      if (pattern.test(content)) {
        return {
          isValid: false,
          reason: 'Spam pattern detected'
        };
      }
    }

    return { isValid: true };
  }

  checkForbiddenWords(content) {
    const lowerContent = content.toLowerCase();
    
    for (const word of this.forbiddenWords) {
      if (lowerContent.includes(word)) {
        return {
          isValid: false,
          reason: 'Forbidden word detected'
        };
      }
    }

    return { isValid: true };
  }

  checkMentions(message) {
    const mentionCount = message.mentions.users.size + message.mentions.roles.size;
    
    if (mentionCount > 5) {
      return {
        isValid: false,
        reason: 'Too many mentions'
      };
    }

    return { isValid: true };
  }

  checkEmojis(content) {
    const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/gu;
    const emojis = content.match(emojiRegex) || [];
    
    if (emojis.length > 10) {
      return {
        isValid: false,
        reason: 'Too many emojis'
      };
    }

    return { isValid: true };
  }

  isJsonData(content) {
    try {
      const trimmed = content.trim();
      return trimmed.startsWith('{') && trimmed.endsWith('}') && JSON.parse(trimmed);
    } catch {
      return false;
    }
  }

  validateJsonData(content) {
    try {
      const data = JSON.parse(content);
      
      // Check if it's betting data
      if (this.isBettingData(data)) {
        return this.validateBettingData(data);
      }
      
      // Generic JSON validation
      if (typeof data !== 'object' || data === null) {
        return {
          isValid: false,
          reason: 'Invalid JSON structure'
        };
      }
      
      return { isValid: true };
      
    } catch (error) {
      return {
        isValid: false,
        reason: 'Invalid JSON format'
      };
    }
  }

  isBettingData(data) {
    // Check for betting-related fields
    const bettingFields = ['teams', 'pick', 'odds', 'analysis', 'recommendation'];
    return bettingFields.some(field => data.hasOwnProperty(field));
  }

  validateBettingData(data) {
    const requiredFields = ['teams', 'pick', 'analysis'];
    const missingFields = requiredFields.filter(field => !data[field]);
    
    if (missingFields.length > 0) {
      return {
        isValid: false,
        reason: `Missing required betting fields: ${missingFields.join(', ')}`
      };
    }
    
    // Validate teams structure
    if (data.teams) {
      if (!data.teams.away || !data.teams.home) {
        return {
          isValid: false,
          reason: 'Invalid teams structure'
        };
      }
    }
    
    // Validate pick format
    if (data.pick && typeof data.pick !== 'string') {
      return {
        isValid: false,
        reason: 'Invalid pick format'
      };
    }
    
    // Validate analysis format
    if (data.analysis && typeof data.analysis !== 'string') {
      return {
        isValid: false,
        reason: 'Invalid analysis format'
      };
    }
    
    return { isValid: true };
  }

  // Method to validate specific betting data from OCR
  async validateOcrData(jsonData) {
    try {
      const validationResult = await this.validateBettingData(jsonData);
      
      if (!validationResult.isValid) {
        logger.warn('OCR data validation failed:', validationResult.reason);
      }
      
      return validationResult;
      
    } catch (error) {
      logger.error('Error validating OCR data:', error);
      return {
        isValid: false,
        reason: 'Validation error'
      };
    }
  }
}

export const messageValidator = new MessageValidator(); 