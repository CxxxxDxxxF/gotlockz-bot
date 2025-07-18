export class RateLimiter {
  private static lastCall = new Map<string, number>();
  private static readonly COOLDOWN_MS = 12 * 1000; // 12 seconds

  static allow(userId: string): boolean {
    const now = Date.now();
    const prev = this.lastCall.get(userId) || 0;
    
    if (now - prev < this.COOLDOWN_MS) {
      return false;
    }
    
    this.lastCall.set(userId, now);
    return true;
  }

  static getTimeRemaining(userId: string): number {
    const now = Date.now();
    const prev = this.lastCall.get(userId) || 0;
    const timeElapsed = now - prev;
    
    return Math.max(0, this.COOLDOWN_MS - timeElapsed);
  }

  static clear(userId: string): void {
    this.lastCall.delete(userId);
  }

  static clearAll(): void {
    this.lastCall.clear();
  }
} 