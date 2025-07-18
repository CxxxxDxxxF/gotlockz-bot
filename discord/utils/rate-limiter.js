import { logger } from './logger.js';

class RateLimiter {
  constructor() {
    this.limits = new Map();
    this.windows = new Map();
    
    // Default rate limits (requests per window)
    this.defaultLimits = {
      message: { requests: 5, window: 60000 }, // 5 messages per minute
      command: { requests: 10, window: 60000 }, // 10 commands per minute
      interaction: { requests: 20, window: 60000 }, // 20 interactions per minute
      bet: { requests: 3, window: 300000 }, // 3 bets per 5 minutes
      stats: { requests: 15, window: 60000 }, // 15 stats requests per minute
      weather: { requests: 10, window: 300000 } // 10 weather requests per 5 minutes
    };
    
    // Clean up old entries every 5 minutes
    setInterval(() => this.cleanup(), 300000);
  }

  async checkLimit(userId, action, customLimit = null) {
    const key = `${userId}:${action}`;
    const now = Date.now();
    
    // Get limit configuration
    const limit = customLimit || this.defaultLimits[action] || this.defaultLimits.command;
    
    // Initialize user's rate limit data if not exists
    if (!this.limits.has(key)) {
      this.limits.set(key, []);
      this.windows.set(key, now);
    }
    
    const requests = this.limits.get(key);
    const windowStart = this.windows.get(key);
    
    // Remove requests outside the current window
    const validRequests = requests.filter(timestamp => 
      now - timestamp < limit.window
    );
    
    // Update the requests array
    this.limits.set(key, validRequests);
    
    // Check if user has exceeded the limit
    if (validRequests.length >= limit.requests) {
      const oldestRequest = validRequests[0];
      const retryAfter = Math.ceil((oldestRequest + limit.window - now) / 1000);
      
      logger.warn(`Rate limit exceeded for user ${userId}, action: ${action}`, {
        userId,
        action,
        requests: validRequests.length,
        limit: limit.requests,
        retryAfter
      });
      
      return {
        allowed: false,
        retryAfter,
        remaining: 0,
        resetTime: oldestRequest + limit.window
      };
    }
    
    // Add current request
    validRequests.push(now);
    this.limits.set(key, validRequests);
    
    const remaining = limit.requests - validRequests.length;
    
    logger.debug(`Rate limit check for user ${userId}, action: ${action}`, {
      userId,
      action,
      remaining,
      total: validRequests.length
    });
    
    return {
      allowed: true,
      remaining,
      resetTime: now + limit.window
    };
  }

  async checkUserLimit(userId, actions = []) {
    const results = {};
    
    for (const action of actions) {
      results[action] = await this.checkLimit(userId, action);
    }
    
    return results;
  }

  resetLimit(userId, action) {
    const key = `${userId}:${action}`;
    this.limits.delete(key);
    this.windows.delete(key);
    
    logger.info(`Rate limit reset for user ${userId}, action: ${action}`);
  }

  resetUserLimits(userId) {
    const keysToDelete = [];
    
    for (const key of this.limits.keys()) {
      if (key.startsWith(`${userId}:`)) {
        keysToDelete.push(key);
      }
    }
    
    for (const key of keysToDelete) {
      this.limits.delete(key);
      this.windows.delete(key);
    }
    
    logger.info(`All rate limits reset for user ${userId}`);
  }

  getLimitInfo(userId, action) {
    const key = `${userId}:${action}`;
    const requests = this.limits.get(key) || [];
    const limit = this.defaultLimits[action] || this.defaultLimits.command;
    const now = Date.now();
    
    const validRequests = requests.filter(timestamp => 
      now - timestamp < limit.window
    );
    
    return {
      current: validRequests.length,
      limit: limit.requests,
      remaining: Math.max(0, limit.requests - validRequests.length),
      resetTime: validRequests.length > 0 ? validRequests[0] + limit.window : now
    };
  }

  cleanup() {
    const now = Date.now();
    const keysToDelete = [];
    
    // Clean up expired rate limit entries
    for (const [key, requests] of this.limits.entries()) {
      const action = key.split(':')[1];
      const limit = this.defaultLimits[action] || this.defaultLimits.command;
      
      const validRequests = requests.filter(timestamp => 
        now - timestamp < limit.window
      );
      
      if (validRequests.length === 0) {
        keysToDelete.push(key);
      } else {
        this.limits.set(key, validRequests);
      }
    }
    
    // Delete expired entries
    for (const key of keysToDelete) {
      this.limits.delete(key);
      this.windows.delete(key);
    }
    
    if (keysToDelete.length > 0) {
      logger.debug(`Cleaned up ${keysToDelete.length} expired rate limit entries`);
    }
  }

  getStats() {
    const stats = {
      totalUsers: new Set(),
      totalRequests: 0,
      actions: {}
    };
    
    for (const [key, requests] of this.limits.entries()) {
      const [userId, action] = key.split(':');
      stats.totalUsers.add(userId);
      stats.totalRequests += requests.length;
      
      if (!stats.actions[action]) {
        stats.actions[action] = 0;
      }
      stats.actions[action] += requests.length;
    }
    
    return {
      ...stats,
      totalUsers: stats.totalUsers.size,
      memoryUsage: {
        limits: this.limits.size,
        windows: this.windows.size
      }
    };
  }
}

export const rateLimiter = new RateLimiter(); 