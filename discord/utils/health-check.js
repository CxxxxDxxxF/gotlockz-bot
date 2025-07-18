import { logger } from './logger.js';
import os from 'os';

class HealthCheck {
  constructor() {
    this.startTime = Date.now();
    this.checks = new Map();
    this.isRunning = false;
    this.interval = null;
  }

  start(intervalMs = 300000) { // Default: 5 minutes
    if (this.isRunning) {
      logger.warn('Health check is already running');
      return;
    }

    this.isRunning = true;
    this.interval = setInterval(() => {
      this.performHealthCheck();
    }, intervalMs);

    logger.info(`Health check started (interval: ${intervalMs}ms)`);
  }

  stop() {
    if (this.interval) {
      clearInterval(this.interval);
      this.interval = null;
    }
    this.isRunning = false;
    logger.info('Health check stopped');
  }

  async performHealthCheck() {
    const startTime = Date.now();
    
    try {
      const healthData = {
        timestamp: new Date().toISOString(),
        uptime: this.getUptime(),
        system: this.getSystemInfo(),
        memory: this.getMemoryInfo(),
        process: this.getProcessInfo(),
        checks: await this.runCustomChecks()
      };

      // Log health status
      const status = this.evaluateHealth(healthData);
      healthData.status = status;

      if (status === 'healthy') {
        logger.debug('Health check passed', healthData);
      } else {
        logger.warn('Health check issues detected', healthData);
      }

      // Store latest health data
      this.latestHealth = healthData;

    } catch (error) {
      logger.error('Health check failed:', error);
    }

    const duration = Date.now() - startTime;
    logger.performance('health_check', duration);
  }

  getUptime() {
    const uptime = Date.now() - this.startTime;
    return {
      milliseconds: uptime,
      seconds: Math.floor(uptime / 1000),
      minutes: Math.floor(uptime / 60000),
      hours: Math.floor(uptime / 3600000),
      days: Math.floor(uptime / 86400000)
    };
  }

  getSystemInfo() {
    return {
      platform: os.platform(),
      arch: os.arch(),
      cpus: os.cpus().length,
      hostname: os.hostname(),
      loadAverage: os.loadavg(),
      uptime: os.uptime()
    };
  }

  getMemoryInfo() {
    const total = os.totalmem();
    const free = os.freemem();
    const used = total - free;
    
    return {
      total: this.formatBytes(total),
      free: this.formatBytes(free),
      used: this.formatBytes(used),
      percentage: Math.round((used / total) * 100),
      raw: {
        total,
        free,
        used
      }
    };
  }

  getProcessInfo() {
    const usage = process.memoryUsage();
    
    return {
      pid: process.pid,
      version: process.version,
      memory: {
        rss: this.formatBytes(usage.rss),
        heapTotal: this.formatBytes(usage.heapTotal),
        heapUsed: this.formatBytes(usage.heapUsed),
        external: this.formatBytes(usage.external),
        arrayBuffers: this.formatBytes(usage.arrayBuffers || 0)
      },
      cpu: process.cpuUsage()
    };
  }

  async runCustomChecks() {
    const checks = {};
    
    // Run all registered custom checks
    for (const [name, checkFn] of this.checks) {
      try {
        const startTime = Date.now();
        const result = await checkFn();
        const duration = Date.now() - startTime;
        
        checks[name] = {
          status: result.status || 'unknown',
          message: result.message || '',
          duration,
          data: result.data || {}
        };
      } catch (error) {
        checks[name] = {
          status: 'error',
          message: error.message,
          duration: 0,
          error: true
        };
      }
    }
    
    return checks;
  }

  evaluateHealth(healthData) {
    const issues = [];
    
    // Check memory usage
    if (healthData.memory.percentage > 90) {
      issues.push('High memory usage');
    }
    
    // Check custom checks
    for (const [name, check] of Object.entries(healthData.checks)) {
      if (check.status === 'error' || check.status === 'failed') {
        issues.push(`Check failed: ${name}`);
      }
    }
    
    // Check uptime
    if (healthData.uptime.hours > 24) {
      issues.push('Long uptime - consider restart');
    }
    
    return issues.length === 0 ? 'healthy' : 'degraded';
  }

  addCheck(name, checkFunction) {
    this.checks.set(name, checkFunction);
    logger.info(`Added health check: ${name}`);
  }

  removeCheck(name) {
    this.checks.delete(name);
    logger.info(`Removed health check: ${name}`);
  }

  getLatestHealth() {
    return this.latestHealth;
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Convenience method for quick health status
  async getStatus() {
    if (!this.latestHealth) {
      await this.performHealthCheck();
    }
    return this.latestHealth;
  }
}

export const healthCheck = new HealthCheck(); 