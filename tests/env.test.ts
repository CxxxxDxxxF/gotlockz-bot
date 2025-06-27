import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { getEnv } from '../src/utils/env';

describe('Environment Configuration', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset environment before each test
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    // Restore original environment after each test
    process.env = originalEnv;
  });

  it('should load required environment variables', () => {
    // Set required environment variables
    process.env['DISCORD_BOT_TOKEN'] = 'dummy';
    process.env['OPENAI_API_KEY'] = 'dummy';

    const env = getEnv();

    expect(env.DISCORD_BOT_TOKEN).toBe('dummy');
    expect(env.OPENAI_API_KEY).toBe('dummy');
  });

  it('should throw error for missing DISCORD_BOT_TOKEN', () => {
    process.env['OPENAI_API_KEY'] = 'dummy';
    delete process.env['DISCORD_BOT_TOKEN'];
    expect(() => getEnv()).toThrow('Missing DISCORD_BOT_TOKEN');
  });

  it('should throw error for missing OPENAI_API_KEY', () => {
    process.env['DISCORD_BOT_TOKEN'] = 'dummy';
    delete process.env['OPENAI_API_KEY'];
    expect(() => getEnv()).toThrow('Missing OPENAI_API_KEY');
  });
}); 