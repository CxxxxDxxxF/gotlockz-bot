import { rateLimiter } from './rateLimiter.js';

describe('RateLimiter', () => {
  beforeEach(() => {
    rateLimiter.clearAll();
  });

  test('should allow first request', () => {
    const userId = '123456789';
    expect(rateLimiter.allow(userId)).toBe(true);
  });

  test('should block subsequent requests within cooldown period', () => {
    const userId = '123456789';
    
    // First request should be allowed
    expect(rateLimiter.allow(userId)).toBe(true);
    
    // Second request should be blocked
    expect(rateLimiter.allow(userId)).toBe(false);
  });

  test('should allow request after cooldown period', () => {
    const userId = '123456789';
    
    // First request
    rateLimiter.allow(userId);
    
    // Mock time to be after cooldown
    const originalNow = Date.now;
    Date.now = jest.fn(() => originalNow() + 13000); // 13 seconds later
    
    // Should be allowed again
    expect(rateLimiter.allow(userId)).toBe(true);
    
    // Restore original Date.now
    Date.now = originalNow;
  });

  test('should return correct time remaining', () => {
    const userId = '123456789';
    
    // First request
    rateLimiter.allow(userId);
    
    // Check time remaining
    const timeRemaining = rateLimiter.getTimeRemaining(userId);
    expect(timeRemaining).toBeGreaterThan(0);
    expect(timeRemaining).toBeLessThanOrEqual(12000); // 12 seconds
  });

  test('should clear specific user', () => {
    const userId = '123456789';
    
    // Make a request
    rateLimiter.allow(userId);
    
    // Clear the user
    rateLimiter.clear(userId);
    
    // Should be allowed again
    expect(rateLimiter.allow(userId)).toBe(true);
  });

  test('should clear all users', () => {
    const user1 = '123456789';
    const user2 = '987654321';
    
    // Make requests for both users
    rateLimiter.allow(user1);
    rateLimiter.allow(user2);
    
    // Clear all
    rateLimiter.clearAll();
    
    // Both should be allowed again
    expect(rateLimiter.allow(user1)).toBe(true);
    expect(rateLimiter.allow(user2)).toBe(true);
  });
}); 