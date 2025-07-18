class RateLimiter {
  constructor () {
    this.requests = new Map();
    this.cooldownMs = 12 * 1000; // 12 seconds
  }

  allow (userId) {
    const now = Date.now();
    const userRequests = this.requests.get(userId);

    if (!userRequests) {
      this.requests.set(userId, now);
      return true;
    }

    if (now - userRequests < this.cooldownMs) {
      return false;
    }

    this.requests.set(userId, now);
    return true;
  }

  getTimeRemaining (userId) {
    const now = Date.now();
    const lastRequest = this.requests.get(userId);

    if (!lastRequest) {
      return 0;
    }

    const timeElapsed = now - lastRequest;
    return Math.max(0, this.cooldownMs - timeElapsed);
  }

  clear (userId) {
    this.requests.delete(userId);
  }

  clearAll () {
    this.requests.clear();
  }

  // Clean up old entries periodically
  cleanup () {
    const now = Date.now();
    for (const [userId, timestamp] of this.requests.entries()) {
      if (now - timestamp > this.cooldownMs * 2) {
        this.requests.delete(userId);
      }
    }
  }
}

export const rateLimiter = new RateLimiter();

// Clean up old entries every 5 minutes
setInterval(() => {
  rateLimiter.cleanup();
}, 5 * 60 * 1000);
