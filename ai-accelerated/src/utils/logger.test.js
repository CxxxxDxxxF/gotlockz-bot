import { logger } from './logger.js';

describe('Logger', () => {
  let consoleSpy;

  beforeEach(() => {
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  test('should log info messages', () => {
    const message = 'Test info message';
    const data = { key: 'value' };

    logger.info(message, data);

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[INFO]'),
      expect.stringContaining(message),
      data
    );
  });

  test('should log error messages', () => {
    const message = 'Test error message';
    const error = new Error('Test error');

    logger.error(message, error);

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR]'),
      expect.stringContaining(message),
      error
    );
  });

  test('should log warning messages', () => {
    const message = 'Test warning message';

    logger.warn(message);

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[WARN]'),
      expect.stringContaining(message)
    );
  });

  test('should log debug messages in development', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    const message = 'Test debug message';
    logger.debug(message);

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[DEBUG]'),
      expect.stringContaining(message)
    );

    process.env.NODE_ENV = originalEnv;
  });

  test('should not log debug messages in production', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    const message = 'Test debug message';
    logger.debug(message);

    expect(consoleSpy).not.toHaveBeenCalledWith(
      expect.stringContaining('[DEBUG]'),
      expect.stringContaining(message)
    );

    process.env.NODE_ENV = originalEnv;
  });
}); 