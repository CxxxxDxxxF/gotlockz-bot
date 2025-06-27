"""
Performance Limiter - Automatically throttles operations to prevent system overload
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional
from functools import wraps

from .system_monitor import system_monitor

logger = logging.getLogger(__name__)


class PerformanceLimiter:
    """Limits performance based on system resources."""

    def __init__(self):
        self.max_concurrent_requests = 10
        self.request_semaphore = asyncio.Semaphore(10)
        self.min_request_interval = 0.1  # 100ms between requests
        self.last_request_time = 0
        self.adaptive_limits = True
        self.emergency_mode = False

    async def check_system_health(self) -> bool:
        """Check if system is healthy for operations."""
        return system_monitor.is_system_healthy()

    async def adaptive_throttle(self):
        """Adaptively throttle based on system health."""
        if not self.adaptive_limits:
            return

        summary = system_monitor.get_system_summary()
        
        # Adjust limits based on system load
        if summary["status"] == "warning":
            self.max_concurrent_requests = max(3, self.max_concurrent_requests - 2)
            self.min_request_interval = min(1.0, self.min_request_interval * 1.5)
            logger.warning(f"System under load - reducing limits: max_requests={self.max_concurrent_requests}, interval={self.min_request_interval}s")
        
        elif summary["status"] == "healthy":
            # Gradually restore limits
            self.max_concurrent_requests = min(10, self.max_concurrent_requests + 1)
            self.min_request_interval = max(0.1, self.min_request_interval * 0.9)

    async def wait_for_system_health(self, timeout: float = 30.0) -> bool:
        """Wait for system to become healthy."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.check_system_health():
                return True
            await asyncio.sleep(1)
        
        return False

    async def rate_limited_request(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function with rate limiting."""
        # Check system health first
        if not await self.check_system_health():
            logger.warning("System unhealthy - waiting for recovery")
            if not await self.wait_for_system_health():
                raise RuntimeError("System did not recover within timeout")

        # Apply rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            await asyncio.sleep(wait_time)

        # Use semaphore for concurrent request limiting
        async with self.request_semaphore:
            self.last_request_time = time.time()
            result = await func(*args, **kwargs)
            
            # Update adaptive limits
            await self.adaptive_throttle()
            
            return result

    def limit_concurrent_requests(self, max_requests: int):
        """Decorator to limit concurrent requests."""
        def decorator(func: Callable) -> Callable:
            semaphore = asyncio.Semaphore(max_requests)
            
            @wraps(func)
            async def wrapper(*args, **kwargs):
                async with semaphore:
                    return await self.rate_limited_request(func, *args, **kwargs)
            
            return wrapper
        return decorator

    def emergency_throttle(self):
        """Enable emergency throttling mode."""
        self.emergency_mode = True
        self.max_concurrent_requests = 1
        self.min_request_interval = 2.0
        logger.critical("EMERGENCY THROTTLING ENABLED - System under extreme load")

    def disable_emergency_throttle(self):
        """Disable emergency throttling mode."""
        self.emergency_mode = False
        self.max_concurrent_requests = 10
        self.min_request_interval = 0.1
        logger.info("Emergency throttling disabled")


# Global performance limiter instance
performance_limiter = PerformanceLimiter()


def rate_limit(max_requests: int = 5):
    """Decorator to rate limit functions."""
    return performance_limiter.limit_concurrent_requests(max_requests)


async def safe_operation(func: Callable, *args, **kwargs) -> Any:
    """Safely execute an operation with performance monitoring."""
    try:
        return await performance_limiter.rate_limited_request(func, *args, **kwargs)
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise 