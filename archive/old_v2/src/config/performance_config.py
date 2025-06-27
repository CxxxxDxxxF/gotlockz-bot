"""
Performance Configuration - Safe limits to prevent system overload
"""

import os
from typing import Any, Dict

# System Resource Limits
MAX_CPU_PERCENT = float(os.getenv("MAX_CPU_PERCENT", "80.0"))
MAX_MEMORY_PERCENT = float(os.getenv("MAX_MEMORY_PERCENT", "85.0"))
MAX_DISK_USAGE_PERCENT = float(os.getenv("MAX_DISK_USAGE_PERCENT", "90.0"))
MAX_TEMPERATURE_CELSIUS = float(os.getenv("MAX_TEMPERATURE_CELSIUS", "85.0"))

# Request Rate Limiting
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
MIN_REQUEST_INTERVAL = float(os.getenv("MIN_REQUEST_INTERVAL", "0.2"))  # 200ms between requests
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))

# Cache Settings
CACHE_TIMEOUT_STATS = int(os.getenv("CACHE_TIMEOUT_STATS", "300"))  # 5 minutes
CACHE_TIMEOUT_WEATHER = int(os.getenv("CACHE_TIMEOUT_WEATHER", "300"))  # 5 minutes
CACHE_TIMEOUT_LIVE = int(os.getenv("CACHE_TIMEOUT_LIVE", "60"))  # 1 minute

# Timeout Settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))  # 10 seconds
CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", "5"))  # 5 seconds

# Monitoring Settings
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))  # 60 seconds
MAX_METRICS_HISTORY = int(os.getenv("MAX_METRICS_HISTORY", "100"))

# Emergency Settings
EMERGENCY_CPU_THRESHOLD = float(os.getenv("EMERGENCY_CPU_THRESHOLD", "95.0"))
EMERGENCY_MEMORY_THRESHOLD = float(os.getenv("EMERGENCY_MEMORY_THRESHOLD", "95.0"))
EMERGENCY_TEMP_THRESHOLD = float(os.getenv("EMERGENCY_TEMP_THRESHOLD", "95.0"))

# Feature Throttling
ENABLE_ADAPTIVE_THROTTLING = os.getenv("ENABLE_ADAPTIVE_THROTTLING", "true").lower() == "true"
ENABLE_EMERGENCY_MODE = os.getenv("ENABLE_EMERGENCY_MODE", "true").lower() == "true"

# Performance Profiles
PERFORMANCE_PROFILES = {
    "conservative": {
        "max_concurrent_requests": 3,
        "min_request_interval": 0.5,
        "max_requests_per_minute": 30,
        "monitoring_interval": 30,
    },
    "balanced": {
        "max_concurrent_requests": 5,
        "min_request_interval": 0.2,
        "max_requests_per_minute": 60,
        "monitoring_interval": 60,
    },
    "performance": {
        "max_concurrent_requests": 10,
        "min_request_interval": 0.1,
        "max_requests_per_minute": 120,
        "monitoring_interval": 120,
    },
}

# Get performance profile from environment
PERFORMANCE_PROFILE = os.getenv("PERFORMANCE_PROFILE", "balanced").lower()
if PERFORMANCE_PROFILE not in PERFORMANCE_PROFILES:
    PERFORMANCE_PROFILE = "balanced"

# Apply profile settings
PROFILE_SETTINGS = PERFORMANCE_PROFILES[PERFORMANCE_PROFILE]
MAX_CONCURRENT_REQUESTS = PROFILE_SETTINGS["max_concurrent_requests"]
MIN_REQUEST_INTERVAL = PROFILE_SETTINGS["min_request_interval"]
MAX_REQUESTS_PER_MINUTE = PROFILE_SETTINGS["max_requests_per_minute"]
MONITORING_INTERVAL = PROFILE_SETTINGS["monitoring_interval"]

# Warning Messages
WARNING_MESSAGES = {
    "cpu_high": "CPU usage is high - consider reducing load",
    "memory_high": "Memory usage is high - consider reducing load",
    "disk_full": "Disk usage is high - consider cleanup",
    "temp_high": "System temperature is high - consider cooling",
    "emergency": "EMERGENCY: System under extreme load - throttling operations",
}

# Logging Configuration
PERFORMANCE_LOG_LEVEL = os.getenv("PERFORMANCE_LOG_LEVEL", "INFO").upper()


def get_performance_config() -> Dict[str, Any]:
    """Get complete performance configuration."""
    return {
        "system_limits": {
            "max_cpu_percent": MAX_CPU_PERCENT,
            "max_memory_percent": MAX_MEMORY_PERCENT,
            "max_disk_usage_percent": MAX_DISK_USAGE_PERCENT,
            "max_temperature_celsius": MAX_TEMPERATURE_CELSIUS,
        },
        "rate_limiting": {
            "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
            "min_request_interval": MIN_REQUEST_INTERVAL,
            "max_requests_per_minute": MAX_REQUESTS_PER_MINUTE,
        },
        "caching": {
            "stats_timeout": CACHE_TIMEOUT_STATS,
            "weather_timeout": CACHE_TIMEOUT_WEATHER,
            "live_timeout": CACHE_TIMEOUT_LIVE,
        },
        "timeouts": {
            "request_timeout": REQUEST_TIMEOUT,
            "connection_timeout": CONNECTION_TIMEOUT,
        },
        "monitoring": {
            "interval": MONITORING_INTERVAL,
            "max_history": MAX_METRICS_HISTORY,
        },
        "emergency": {
            "cpu_threshold": EMERGENCY_CPU_THRESHOLD,
            "memory_threshold": EMERGENCY_MEMORY_THRESHOLD,
            "temp_threshold": EMERGENCY_TEMP_THRESHOLD,
        },
        "features": {
            "adaptive_throttling": ENABLE_ADAPTIVE_THROTTLING,
            "emergency_mode": ENABLE_EMERGENCY_MODE,
        },
        "profile": PERFORMANCE_PROFILE,
    }
