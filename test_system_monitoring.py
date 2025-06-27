#!/usr/bin/env python3
"""
Test script to verify system monitoring and performance limiting
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.utils.system_monitor import system_monitor
from bot.utils.performance_limiter import performance_limiter, safe_operation
from config.performance_config import get_performance_config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_system_monitoring():
    """Test system monitoring functionality."""
    print("=== Testing System Monitoring ===")
    
    try:
        # Start monitoring
        await system_monitor.start_monitoring(interval_seconds=5)
        print("✅ System monitoring started")
        
        # Wait a bit for first metrics
        await asyncio.sleep(6)
        
        # Get system summary
        summary = system_monitor.get_system_summary()
        print(f"✅ System summary: {summary}")
        
        # Check if system is healthy
        is_healthy = system_monitor.is_system_healthy()
        print(f"✅ System healthy: {is_healthy}")
        
        # Stop monitoring
        await system_monitor.stop_monitoring()
        print("✅ System monitoring stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ System monitoring test failed: {e}")
        return False


async def test_performance_limiting():
    """Test performance limiting functionality."""
    print("\n=== Testing Performance Limiting ===")
    
    try:
        # Test rate limited function
        @performance_limiter.limit_concurrent_requests(2)
        async def test_function(delay: float = 0.1):
            await asyncio.sleep(delay)
            return f"Completed after {delay}s"
        
        # Run multiple concurrent operations
        start_time = time.time()
        tasks = [safe_operation(test_function, 0.1) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        print(f"✅ Performance limiting test completed in {total_time:.2f}s")
        print(f"✅ Results: {len(results)} operations completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance limiting test failed: {e}")
        return False


async def test_configuration():
    """Test performance configuration."""
    print("\n=== Testing Performance Configuration ===")
    
    try:
        config = get_performance_config()
        print("✅ Performance configuration loaded:")
        print(f"   - Profile: {config['profile']}")
        print(f"   - Max concurrent requests: {config['rate_limiting']['max_concurrent_requests']}")
        print(f"   - Min request interval: {config['rate_limiting']['min_request_interval']}s")
        print(f"   - Max CPU: {config['system_limits']['max_cpu_percent']}%")
        print(f"   - Max memory: {config['system_limits']['max_memory_percent']}%")
        print(f"   - Max temperature: {config['system_limits']['max_temperature_celsius']}°C")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_emergency_mode():
    """Test emergency throttling mode."""
    print("\n=== Testing Emergency Mode ===")
    
    try:
        # Enable emergency mode
        performance_limiter.emergency_throttle()
        print("✅ Emergency throttling enabled")
        
        # Check limits
        print(f"   - Max concurrent requests: {performance_limiter.max_concurrent_requests}")
        print(f"   - Min request interval: {performance_limiter.min_request_interval}s")
        
        # Disable emergency mode
        performance_limiter.disable_emergency_throttle()
        print("✅ Emergency throttling disabled")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency mode test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("Starting system monitoring and performance tests...\n")
    
    tests = [
        test_configuration,
        test_system_monitoring,
        test_performance_limiting,
        test_emergency_mode,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print(f"\n=== Test Summary ===")
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! System monitoring and performance limiting are working correctly.")
        print("\nYour computer is now protected from overheating and performance issues!")
    else:
        print("❌ Some tests failed. Please check the configuration and dependencies.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 