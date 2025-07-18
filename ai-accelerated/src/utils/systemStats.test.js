import { getSystemStats } from './systemStats.js';

describe('SystemStats', () => {
  let originalUptime;
  let originalMemoryUsage;
  let originalCpuUsage;

  beforeEach(() => {
    // Mock process methods
    originalUptime = process.uptime;
    originalMemoryUsage = process.memoryUsage;
    originalCpuUsage = process.cpuUsage;

    process.uptime = jest.fn(() => 3661); // 1 hour 1 minute 1 second
    process.memoryUsage = jest.fn(() => ({
      heapUsed: 52428800, // 50MB
      heapTotal: 104857600 // 100MB
    }));
    process.cpuUsage = jest.fn(() => ({
      user: 5000000, // 5 seconds
      system: 2000000 // 2 seconds
    }));
  });

  afterEach(() => {
    // Restore original methods
    process.uptime = originalUptime;
    process.memoryUsage = originalMemoryUsage;
    process.cpuUsage = originalCpuUsage;
  });

  test('should return formatted uptime', () => {
    const stats = getSystemStats();

    expect(stats.uptime).toBe('1h 1m');
  });

  test('should return formatted memory usage', () => {
    const stats = getSystemStats();

    expect(stats.memory).toBe('50MB');
  });

  test('should return formatted CPU usage', () => {
    const stats = getSystemStats();

    expect(stats.cpu).toBe('5000ms');
  });

  test('should return command count', () => {
    const stats = getSystemStats();

    expect(stats.commands).toBe('2');
  });

  test('should return server count', () => {
    const stats = getSystemStats();

    expect(stats.servers).toBe('1');
  });

  test('should return all stats in correct format', () => {
    const stats = getSystemStats();

    expect(stats).toEqual({
      uptime: '1h 1m',
      memory: '50MB',
      cpu: '5000ms',
      commands: '2',
      servers: '1'
    });
  });

  test('should handle zero uptime', () => {
    process.uptime = jest.fn(() => 0);
    
    const stats = getSystemStats();

    expect(stats.uptime).toBe('0h 0m');
  });

  test('should handle large memory usage', () => {
    process.memoryUsage = jest.fn(() => ({
      heapUsed: 1073741824, // 1GB
      heapTotal: 2147483648 // 2GB
    }));

    const stats = getSystemStats();

    expect(stats.memory).toBe('1024MB');
  });
}); 