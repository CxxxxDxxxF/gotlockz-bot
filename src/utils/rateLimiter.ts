const lastCall = new Map<string, number>();

export function allow(userId: string): boolean {
  const now = Date.now();
  const prev = lastCall.get(userId) || 0;
  if (now - prev < 1000 * 12) { // max 5 calls/min
    return false;
  }
  lastCall.set(userId, now);
  return true;
} 