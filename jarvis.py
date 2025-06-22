#!/usr/bin/env python3
"""
JARVIS - Just A Rather Very Intelligent System
A comprehensive computer management and monitoring assistant
"""

import os
import sys
import time
import json
import psutil
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Optional
import argparse

class Jarvis:
    def __init__(self):
        self.running = False
        self.monitoring = False
        self.alerts = []
        self.system_stats = {}
        
    def speak(self, message: str):
        """Text-to-speech output"""
        print(f"🤖 JARVIS: {message}")
        try:
            subprocess.run(['say', message], capture_output=True)
        except FileNotFoundError:
            pass  # say command not available
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get temperature (macOS specific)
        temp = self.get_temperature()
        
        # Get network connections with error handling
        try:
            network_connections = len(psutil.net_connections())
        except (psutil.AccessDenied, PermissionError):
            network_connections = 0  # Default if access denied
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'disk_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'temperature_c': temp,
            'battery_percent': self.get_battery_percent(),
            'network_connections': network_connections,
            'process_count': len(psutil.pids())
        }
    
    def get_temperature(self) -> Optional[float]:
        """Get CPU temperature"""
        try:
            result = subprocess.run(
                ['sudo', 'powermetrics', '--samplers', 'smc', '-n', '1', '-i', '1000'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'CPU die temperature' in line:
                    return float(line.split(':')[1].strip().replace(' C', ''))
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            pass
        return None
    
    def get_battery_percent(self) -> Optional[int]:
        """Get battery percentage"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent)
        except:
            pass
        return None
    
    def get_top_processes(self, limit: int = 10) -> List[Dict]:
        """Get top CPU-consuming processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        # Filter out processes with None cpu_percent
        processes = [p for p in processes if p['cpu_percent'] is not None]
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    
    def check_alerts(self, stats: Dict) -> List[str]:
        """Check for system alerts"""
        alerts = []
        
        # CPU temperature alerts
        if stats.get('temperature_c'):
            temp = stats['temperature_c']
            if temp > 85:
                alerts.append(f"🚨 CRITICAL: CPU temperature is {temp}°C - System overheating!")
            elif temp > 75:
                alerts.append(f"⚠️  WARNING: CPU temperature is {temp}°C - Monitor closely")
        
        # CPU usage alerts
        if stats['cpu_percent'] > 90:
            alerts.append(f"🚨 CRITICAL: CPU usage is {stats['cpu_percent']}%")
        elif stats['cpu_percent'] > 80:
            alerts.append(f"⚠️  WARNING: CPU usage is {stats['cpu_percent']}%")
        
        # Memory alerts
        if stats['memory_percent'] > 90:
            alerts.append(f"🚨 CRITICAL: Memory usage is {stats['memory_percent']}%")
        elif stats['memory_percent'] > 80:
            alerts.append(f"⚠️  WARNING: Memory usage is {stats['memory_percent']}%")
        
        # Disk alerts
        if stats['disk_percent'] > 90:
            alerts.append(f"🚨 CRITICAL: Disk usage is {stats['disk_percent']}%")
        elif stats['disk_percent'] > 80:
            alerts.append(f"⚠️  WARNING: Disk usage is {stats['disk_percent']}%")
        
        # Battery alerts
        if stats.get('battery_percent') is not None:
            battery = stats['battery_percent']
            if battery < 10:
                alerts.append(f"🔋 CRITICAL: Battery at {battery}% - Connect charger immediately!")
            elif battery < 20:
                alerts.append(f"🔋 WARNING: Battery at {battery}% - Consider charging")
        
        return alerts
    
    def optimize_system(self):
        """Perform system optimization tasks"""
        self.speak("Initiating system optimization protocols")
        
        optimizations = []
        
        # Clear system caches
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True)
            optimizations.append("✅ Cleared system caches")
        except:
            optimizations.append("❌ Failed to clear system caches")
        
        # Kill high-CPU processes (except system processes)
        high_cpu_processes = self.get_top_processes(5)
        for proc in high_cpu_processes:
            if proc['cpu_percent'] > 50 and proc['name'] not in ['kernel_task', 'WindowServer']:
                try:
                    os.kill(proc['pid'], 15)  # SIGTERM
                    optimizations.append(f"✅ Terminated high-CPU process: {proc['name']}")
                except:
                    pass
        
        # Enable low power mode
        try:
            subprocess.run(['sudo', 'pmset', '-a', 'lowpowermode', '1'], capture_output=True)
            optimizations.append("✅ Enabled low power mode")
        except:
            pass
        
        return optimizations
    
    def monitor_system(self, interval: int = 30):
        """Continuous system monitoring"""
        self.monitoring = True
        self.speak("System monitoring activated")
        
        while self.monitoring:
            try:
                stats = self.get_system_info()
                alerts = self.check_alerts(stats)
                
                # Display current status
                print(f"\n{'='*60}")
                print(f"📊 SYSTEM STATUS - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*60}")
                print(f"CPU: {stats['cpu_percent']}% | Memory: {stats['memory_percent']}% | Disk: {stats['disk_percent']}%")
                if stats.get('temperature_c'):
                    print(f"Temperature: {stats['temperature_c']}°C")
                if stats.get('battery_percent') is not None:
                    print(f"Battery: {stats['battery_percent']}%")
                
                # Show alerts
                if alerts:
                    print(f"\n🚨 ALERTS:")
                    for alert in alerts:
                        print(f"  {alert}")
                        self.speak(alert.split(':')[1] if ':' in alert else alert)
                
                # Show top processes
                print(f"\n🔥 TOP PROCESSES:")
                top_procs = self.get_top_processes(5)
                for i, proc in enumerate(top_procs, 1):
                    print(f"  {i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.monitoring = False
                break
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(interval)
    
    def run_command(self, command: str):
        """Execute system commands"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e)
            }
    
    def start(self):
        """Start Jarvis"""
        self.running = True
        self.speak("Jarvis online and ready for duty")
        
        print("🤖 JARVIS - Just A Rather Very Intelligent System")
        print("=" * 60)
        print("Available commands:")
        print("  status    - Show current system status")
        print("  monitor   - Start continuous monitoring")
        print("  optimize  - Perform system optimization")
        print("  processes - Show top processes")
        print("  temp      - Show temperature")
        print("  quit      - Exit Jarvis")
        print("=" * 60)
        
        while self.running:
            try:
                command = input("\n🤖 JARVIS> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    self.running = False
                    self.monitoring = False
                    self.speak("Jarvis shutting down")
                    break
                
                elif command == 'status':
                    stats = self.get_system_info()
                    print(f"\n📊 SYSTEM STATUS:")
                    print(f"CPU: {stats['cpu_percent']}%")
                    print(f"Memory: {stats['memory_percent']}% ({stats['memory_used_gb']}GB / {stats['memory_total_gb']}GB)")
                    print(f"Disk: {stats['disk_percent']}%")
                    if stats.get('temperature_c'):
                        print(f"Temperature: {stats['temperature_c']}°C")
                    if stats.get('battery_percent') is not None:
                        print(f"Battery: {stats['battery_percent']}%")
                
                elif command == 'monitor':
                    if not self.monitoring:
                        monitor_thread = threading.Thread(target=self.monitor_system)
                        monitor_thread.daemon = True
                        monitor_thread.start()
                    else:
                        print("Monitoring already active")
                
                elif command == 'optimize':
                    optimizations = self.optimize_system()
                    print("\n🔧 OPTIMIZATION RESULTS:")
                    for opt in optimizations:
                        print(f"  {opt}")
                
                elif command == 'processes':
                    print(f"\n🔥 TOP PROCESSES:")
                    top_procs = self.get_top_processes(10)
                    for i, proc in enumerate(top_procs, 1):
                        print(f"  {i}. {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}% | Memory: {proc['memory_percent']}%")
                
                elif command == 'temp':
                    temp = self.get_temperature()
                    if temp:
                        print(f"🌡️  CPU Temperature: {temp}°C")
                        if temp > 85:
                            print("🚨 CRITICAL: System is overheating!")
                        elif temp > 75:
                            print("⚠️  WARNING: Temperature is high")
                        else:
                            print("✅ Temperature is normal")
                    else:
                        print("❌ Could not read temperature")
                
                elif command.startswith('run '):
                    cmd = command[4:]
                    result = self.run_command(cmd)
                    if result['success']:
                        print(f"✅ Command executed successfully")
                        if result['output']:
                            print(f"Output: {result['output']}")
                    else:
                        print(f"❌ Command failed: {result['error']}")
                
                else:
                    print("Unknown command. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                self.running = False
                self.monitoring = False
                self.speak("Jarvis shutting down")
                break

def main():
    parser = argparse.ArgumentParser(description='JARVIS - System Management Assistant')
    parser.add_argument('--monitor', action='store_true', help='Start monitoring mode')
    parser.add_argument('--optimize', action='store_true', help='Run system optimization')
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    jarvis = Jarvis()
    
    if args.status:
        stats = jarvis.get_system_info()
        print(json.dumps(stats, indent=2))
    elif args.optimize:
        optimizations = jarvis.optimize_system()
        for opt in optimizations:
            print(opt)
    elif args.monitor:
        jarvis.monitor_system()
    else:
        jarvis.start()

if __name__ == "__main__":
    main() 