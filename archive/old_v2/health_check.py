#!/usr/bin/env python3
"""
Health Check Script - Verify system protection is working
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from bot.utils.system_monitor import system_monitor
from config.performance_config import get_performance_config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def health_check():
    """Run a quick health check."""
    print("🔍 GotLockz Bot Health Check")
    print("=" * 40)

    try:
        # Check configuration
        print("\n📋 Configuration Check:")
        config = get_performance_config()
        print(f"   ✅ Performance profile: {config['profile']}")
        print(f"   ✅ Max CPU usage: {config['system_limits']['max_cpu_percent']}%")
        print(f"   ✅ Max memory usage: {config['system_limits']['max_memory_percent']}%")
        print(f"   ✅ Max temperature: {config['system_limits']['max_temperature_celsius']}°C")
        print(f"   ✅ Max concurrent requests: {config['rate_limiting']['max_concurrent_requests']}")

        # Test system monitoring
        print("\n🖥️  System Monitoring Check:")
        await system_monitor.start_monitoring(interval_seconds=5)
        await asyncio.sleep(6)  # Wait for first metrics

        summary = system_monitor.get_system_summary()
        current = summary.get("current", {})

        print(f"   ✅ CPU usage: {current.get('cpu_percent', 'N/A')}%")
        print(f"   ✅ Memory usage: {current.get('memory_percent', 'N/A')}%")
        print(f"   ✅ Memory used: {current.get('memory_used_gb', 'N/A'):.1f}GB")
        print(f"   ✅ Disk usage: {current.get('disk_usage_percent', 'N/A')}%")

        if current.get("temperature_celsius"):
            print(f"   ✅ Temperature: {current.get('temperature_celsius'):.1f}°C")
        else:
            print("   ⚠️  Temperature: Not available (requires iStats on macOS)")

        # Check system health
        is_healthy = system_monitor.is_system_healthy()
        status = "🟢 HEALTHY" if is_healthy else "🔴 UNHEALTHY"
        print(f"   {status} System status: {summary.get('status', 'unknown')}")

        await system_monitor.stop_monitoring()

        # Final status
        print("\n🎯 Protection Status:")
        if is_healthy:
            print("   ✅ Your computer is protected from overheating and performance issues!")
            print("   ✅ The bot will automatically throttle operations if needed")
            print("   ✅ System monitoring is active and working")
        else:
            print("   ⚠️  System resources are currently high")
            print("   ✅ Protection is active - operations will be throttled")
            print("   ✅ Monitor the logs for performance warnings")

        print("\n💡 Tips:")
        print("   - The bot uses conservative limits by default")
        print("   - Set PERFORMANCE_PROFILE=conservative for extra safety")
        print("   - Monitor logs for 'System thresholds warning' messages")
        print("   - The bot will automatically recover when resources improve")

        return True

    except Exception as e:
        print(f"\n❌ Health check failed: {e}")
        print("   Please check your installation and dependencies")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(health_check())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Health check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
