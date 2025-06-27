"""
System Monitor - Prevents computer overheating and performance issues
"""

import asyncio
import logging
import os
import platform
import psutil
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_total_gb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    temperature_celsius: Optional[float] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SystemMonitor:
    """Monitors system resources to prevent overheating and performance issues."""

    def __init__(self):
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 100
        self.warning_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_usage_percent": 90.0,
            "temperature_celsius": 85.0,  # Conservative threshold
        }
        self.critical_thresholds = {
            "cpu_percent": 95.0,
            "memory_percent": 95.0,
            "disk_usage_percent": 98.0,
            "temperature_celsius": 95.0,
        }
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.last_metrics: Optional[SystemMetrics] = None

    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous system monitoring."""
        if self.is_monitoring:
            logger.warning("System monitoring already running")
            return

        self.is_monitoring = True
        logger.info(f"Starting system monitoring (interval: {interval_seconds}s)")
        
        self.monitor_task = asyncio.create_task(self._monitor_loop(interval_seconds))

    async def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("System monitoring stopped")

    async def _monitor_loop(self, interval_seconds: int):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = await self.get_current_metrics()
                self._store_metrics(metrics)
                await self._check_thresholds(metrics)
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)

    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Network usage
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024**2)
            network_recv_mb = network.bytes_recv / (1024**2)
            
            # Temperature (platform specific)
            temperature = await self._get_temperature()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_gb=memory_used_gb,
                memory_total_gb=memory_total_gb,
                disk_usage_percent=disk_usage_percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                temperature_celsius=temperature
            )
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            # Return safe defaults
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_gb=0.0,
                memory_total_gb=0.0,
                disk_usage_percent=0.0,
                network_sent_mb=0.0,
                network_recv_mb=0.0
            )

    async def _get_temperature(self) -> Optional[float]:
        """Get CPU temperature (platform specific)."""
        try:
            if platform.system() == "Darwin":  # macOS
                return await self._get_macos_temperature()
            elif platform.system() == "Linux":
                return await self._get_linux_temperature()
            elif platform.system() == "Windows":
                return await self._get_windows_temperature()
            else:
                return None
        except Exception as e:
            logger.debug(f"Could not get temperature: {e}")
            return None

    async def _get_macos_temperature(self) -> Optional[float]:
        """Get temperature on macOS."""
        try:
            # Use iStats if available, otherwise return None
            result = await asyncio.create_subprocess_exec(
                "istats", "cpu", "temp",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                output = stdout.decode().strip()
                # Parse temperature from output like "CPU temp: 45.0°C"
                if "°C" in output:
                    temp_str = output.split("°C")[0].split(":")[-1].strip()
                    return float(temp_str)
            return None
        except Exception:
            return None

    async def _get_linux_temperature(self) -> Optional[float]:
        """Get temperature on Linux."""
        try:
            # Try common temperature file locations
            temp_files = [
                "/sys/class/thermal/thermal_zone0/temp",
                "/sys/class/hwmon/hwmon0/temp1_input",
                "/proc/acpi/thermal_zone/THM0/temperature"
            ]
            
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    with open(temp_file, 'r') as f:
                        temp_raw = f.read().strip()
                        # Convert from millidegrees to degrees
                        return float(temp_raw) / 1000.0
            return None
        except Exception:
            return None

    async def _get_windows_temperature(self) -> Optional[float]:
        """Get temperature on Windows."""
        try:
            # Windows doesn't have a simple way to get CPU temp without additional tools
            # Return None for now - could integrate with OpenHardwareMonitor or similar
            return None
        except Exception:
            return None

    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in history."""
        self.metrics_history.append(metrics)
        self.last_metrics = metrics
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)

    async def _check_thresholds(self, metrics: SystemMetrics):
        """Check if metrics exceed warning or critical thresholds."""
        warnings = []
        criticals = []
        
        # Check CPU
        if metrics.cpu_percent >= self.critical_thresholds["cpu_percent"]:
            criticals.append(f"CPU: {metrics.cpu_percent:.1f}%")
        elif metrics.cpu_percent >= self.warning_thresholds["cpu_percent"]:
            warnings.append(f"CPU: {metrics.cpu_percent:.1f}%")
        
        # Check memory
        if metrics.memory_percent >= self.critical_thresholds["memory_percent"]:
            criticals.append(f"Memory: {metrics.memory_percent:.1f}%")
        elif metrics.memory_percent >= self.warning_thresholds["memory_percent"]:
            warnings.append(f"Memory: {metrics.memory_percent:.1f}%")
        
        # Check disk
        if metrics.disk_usage_percent >= self.critical_thresholds["disk_usage_percent"]:
            criticals.append(f"Disk: {metrics.disk_usage_percent:.1f}%")
        elif metrics.disk_usage_percent >= self.warning_thresholds["disk_usage_percent"]:
            warnings.append(f"Disk: {metrics.disk_usage_percent:.1f}%")
        
        # Check temperature
        if metrics.temperature_celsius:
            if metrics.temperature_celsius >= self.critical_thresholds["temperature_celsius"]:
                criticals.append(f"Temperature: {metrics.temperature_celsius:.1f}°C")
            elif metrics.temperature_celsius >= self.warning_thresholds["temperature_celsius"]:
                warnings.append(f"Temperature: {metrics.temperature_celsius:.1f}°C")
        
        # Log warnings and criticals
        if criticals:
            logger.critical(f"CRITICAL system thresholds exceeded: {', '.join(criticals)}")
            await self._handle_critical_thresholds()
        elif warnings:
            logger.warning(f"System thresholds warning: {', '.join(warnings)}")

    async def _handle_critical_thresholds(self):
        """Handle critical threshold breaches."""
        logger.critical("CRITICAL: System resources critically low - consider stopping intensive operations")
        
        # Could implement automatic throttling here
        # For now, just log the warning

    def get_system_summary(self) -> Dict[str, any]:
        """Get a summary of current system status."""
        if not self.last_metrics:
            return {"status": "No metrics available"}
        
        metrics = self.last_metrics
        
        # Calculate averages over last 10 measurements
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            "current": {
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "memory_used_gb": metrics.memory_used_gb,
                "memory_total_gb": metrics.memory_total_gb,
                "disk_usage_percent": metrics.disk_usage_percent,
                "temperature_celsius": metrics.temperature_celsius,
                "timestamp": metrics.timestamp.isoformat()
            },
            "averages": {
                "cpu_percent": avg_cpu,
                "memory_percent": avg_memory
            },
            "status": "healthy" if metrics.cpu_percent < 80 and metrics.memory_percent < 85 else "warning"
        }

    def is_system_healthy(self) -> bool:
        """Check if system is healthy for intensive operations."""
        if not self.last_metrics:
            return True  # Assume healthy if no metrics
        
        metrics = self.last_metrics
        
        # Check if any critical thresholds are exceeded
        if (metrics.cpu_percent >= self.critical_thresholds["cpu_percent"] or
            metrics.memory_percent >= self.critical_thresholds["memory_percent"] or
            metrics.disk_usage_percent >= self.critical_thresholds["disk_usage_percent"] or
            (metrics.temperature_celsius and 
             metrics.temperature_celsius >= self.critical_thresholds["temperature_celsius"])):
            return False
        
        return True


# Global system monitor instance
system_monitor = SystemMonitor() 