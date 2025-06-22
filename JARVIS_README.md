# 🤖 JARVIS - Just A Rather Very Intelligent System

A comprehensive AI-powered computer management and monitoring assistant for macOS, inspired by Iron Man's JARVIS.

## 🚀 Features

### 📊 Real-time System Monitoring
- **CPU Usage**: Real-time CPU utilization tracking
- **Memory Usage**: RAM usage monitoring with detailed breakdown
- **Disk Usage**: Storage space monitoring
- **Temperature**: CPU temperature monitoring (macOS)
- **Battery**: Battery level tracking
- **Network**: Active connection monitoring
- **Processes**: Top resource-consuming processes

### 🔧 System Optimization
- **Cache Clearing**: Automatic system cache cleanup
- **Process Management**: Kill high-CPU processes
- **Power Management**: Enable low power mode
- **Performance Tuning**: Automatic system optimization

### 🚨 Intelligent Alerts
- **Temperature Alerts**: Warns when CPU gets too hot
- **Resource Alerts**: Notifies when CPU/memory usage is high
- **Battery Alerts**: Warns when battery is low
- **Critical Notifications**: Immediate alerts for dangerous conditions

### 🌐 Web Dashboard
- **Modern UI**: Beautiful, responsive web interface
- **Real-time Updates**: Live system statistics
- **Interactive Controls**: Process management and system optimization
- **Mobile Friendly**: Works on all devices

## 📦 Installation

### Prerequisites
- macOS (tested on macOS 13+)
- Python 3.7+
- Administrator privileges (for temperature monitoring)

### Quick Start
```bash
# Clone or download the files to your project directory
# Make the startup script executable
chmod +x start_jarvis.sh

# Install dependencies and start JARVIS
./start_jarvis.sh
```

### Manual Installation
```bash
# Install required Python packages
pip3 install psutil flask

# Make scripts executable
chmod +x jarvis.py jarvis_dashboard.py start_jarvis.sh
```

## 🎯 Usage

### Quick Commands
```bash
# Start JARVIS in terminal mode (interactive)
./start_jarvis.sh

# Start web dashboard
./start_jarvis.sh dashboard

# Start continuous monitoring
./start_jarvis.sh monitor

# Run system optimization
./start_jarvis.sh optimize

# Show current system status
./start_jarvis.sh status

# Show help
./start_jarvis.sh help
```

### Terminal Mode Commands
When running in terminal mode, you can use these commands:

- `status` - Show current system status
- `monitor` - Start continuous monitoring
- `optimize` - Perform system optimization
- `processes` - Show top processes
- `temp` - Show temperature
- `run <command>` - Execute system commands
- `quit` - Exit JARVIS

### Web Dashboard
1. Start the dashboard: `./start_jarvis.sh dashboard`
2. Open your browser to: `http://localhost:5001`
3. Monitor your system in real-time
4. Use the "Optimize System" button for quick fixes
5. Kill problematic processes directly from the interface

## 🔧 Configuration

### Temperature Monitoring
JARVIS uses `powermetrics` for temperature monitoring, which requires sudo privileges. You may be prompted for your password.

### Custom Alerts
You can modify the alert thresholds in `jarvis.py`:
```python
# CPU temperature alerts
if temp > 85:  # Critical threshold
if temp > 75:  # Warning threshold

# CPU usage alerts
if stats['cpu_percent'] > 90:  # Critical
if stats['cpu_percent'] > 80:  # Warning
```

## 🛠️ Troubleshooting

### Common Issues

**"Permission denied" for temperature monitoring**
- This is normal on macOS. Enter your password when prompted.
- Temperature monitoring requires sudo privileges.

**"Module not found" errors**
- Run: `pip3 install psutil flask`
- Or use: `./start_jarvis.sh` (auto-installs dependencies)

**Dashboard not loading**
- Check if port 5001 is available
- Try: `lsof -i :5001` to see what's using the port
- Restart the dashboard: `./start_jarvis.sh dashboard`

**High CPU usage from JARVIS itself**
- JARVIS is designed to be lightweight
- If it's using too much CPU, check for other processes
- Use the monitoring mode to identify the real culprits

### Performance Tips

1. **Use the web dashboard** for continuous monitoring (more efficient)
2. **Close unnecessary applications** when optimizing
3. **Restart your Mac** if temperatures remain high after optimization
4. **Check for background processes** using the process list

## 🔒 Security

- JARVIS requires administrator privileges for some features
- Temperature monitoring uses system-level commands
- Process termination requires careful consideration
- All operations are logged and visible

## 📈 System Requirements

- **OS**: macOS 10.15+ (Catalina and newer)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB free space
- **Python**: 3.7 or newer
- **Permissions**: Administrator access for full functionality

## 🤝 Contributing

Feel free to enhance JARVIS with additional features:

- Add more system metrics
- Create custom alert rules
- Improve the web interface
- Add support for other operating systems
- Create additional optimization strategies

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Inspired by Iron Man's JARVIS AI assistant
- Built with Python, Flask, and modern web technologies
- Uses system monitoring libraries for accurate data

---

**Remember**: JARVIS is here to help, but always be careful when terminating processes or making system changes. When in doubt, restart your computer!

🤖 *"Sometimes you gotta run before you can walk."* - Tony Stark 