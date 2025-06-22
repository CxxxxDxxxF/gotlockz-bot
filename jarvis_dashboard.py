#!/usr/bin/env python3
"""
JARVIS Dashboard - Web interface for system monitoring
"""

from flask import Flask, render_template, jsonify, request
import psutil
import subprocess
import json
from datetime import datetime
import threading
import time
import os

app = Flask(__name__)

class JarvisDashboard:
    def __init__(self):
        self.system_stats = {}
        self.update_stats()
    
    def get_temperature(self):
        """Get CPU temperature"""
        try:
            result = subprocess.run(
                ['sudo', 'powermetrics', '--samplers', 'smc', '-n', '1', '-i', '1000'],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split('\n'):
                if 'CPU die temperature' in line:
                    return float(line.split(':')[1].strip().replace(' C', ''))
        except:
            pass
        return None
    
    def get_battery_percent(self):
        """Get battery percentage"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return int(battery.percent)
        except:
            pass
        return None
    
    def update_stats(self):
        """Update system statistics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network connections with error handling
        try:
            network_connections = len(psutil.net_connections())
        except (psutil.AccessDenied, PermissionError):
            network_connections = 0  # Default if access denied
        
        self.system_stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'disk_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2),
            'temperature_c': self.get_temperature(),
            'battery_percent': self.get_battery_percent(),
            'network_connections': network_connections,
            'process_count': len(psutil.pids())
        }
    
    def get_top_processes(self, limit=10):
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
        
        return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    
    def optimize_system(self):
        """Perform system optimization"""
        results = []
        
        # Clear system caches
        try:
            subprocess.run(['sudo', 'purge'], capture_output=True)
            results.append("Cleared system caches")
        except:
            results.append("Failed to clear system caches")
        
        # Enable low power mode
        try:
            subprocess.run(['sudo', 'pmset', '-a', 'lowpowermode', '1'], capture_output=True)
            results.append("Enabled low power mode")
        except:
            results.append("Failed to enable low power mode")
        
        return results

dashboard = JarvisDashboard()

@app.route('/')
def index():
    return render_template('jarvis_dashboard.html')

@app.route('/api/stats')
def get_stats():
    dashboard.update_stats()
    return jsonify(dashboard.system_stats)

@app.route('/api/processes')
def get_processes():
    processes = dashboard.get_top_processes(15)
    return jsonify(processes)

@app.route('/api/optimize', methods=['POST'])
def optimize():
    results = dashboard.optimize_system()
    return jsonify({'results': results})

@app.route('/api/kill_process', methods=['POST'])
def kill_process():
    data = request.get_json()
    pid = data.get('pid')
    
    try:
        os.kill(int(pid), 15)  # SIGTERM
        return jsonify({'success': True, 'message': f'Process {pid} terminated'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 