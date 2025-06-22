#!/bin/bash

# JARVIS Startup Script
# Just A Rather Very Intelligent System

echo "🤖 Initializing JARVIS..."
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import psutil" 2>/dev/null || {
    echo "📦 Installing psutil..."
    pip3 install psutil
}

python3 -c "import flask" 2>/dev/null || {
    echo "📦 Installing Flask..."
    pip3 install flask
}

echo "✅ Dependencies checked"

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes:"
    echo "  terminal    - Start JARVIS in terminal mode (default)"
    echo "  dashboard   - Start JARVIS web dashboard"
    echo "  monitor     - Start continuous monitoring"
    echo "  optimize    - Run system optimization"
    echo "  status      - Show current system status"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start terminal mode"
    echo "  $0 dashboard          # Start web dashboard"
    echo "  $0 monitor            # Start monitoring"
    echo "  $0 optimize           # Optimize system"
    echo ""
}

# Function to start terminal mode
start_terminal() {
    echo "🚀 Starting JARVIS in terminal mode..."
    echo "Press Ctrl+C to exit"
    echo ""
    python3 jarvis.py
}

# Function to start dashboard
start_dashboard() {
    echo "🌐 Starting JARVIS web dashboard..."
    echo "Dashboard will be available at: http://localhost:5001"
    echo "Press Ctrl+C to stop the dashboard"
    echo ""
    python3 jarvis_dashboard.py
}

# Function to start monitoring
start_monitor() {
    echo "📊 Starting JARVIS monitoring mode..."
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    python3 jarvis.py --monitor
}

# Function to optimize system
optimize_system() {
    echo "🔧 Running JARVIS system optimization..."
    python3 jarvis.py --optimize
}

# Function to show status
show_status() {
    echo "📈 Showing JARVIS system status..."
    python3 jarvis.py --status
}

# Main script logic
case "${1:-terminal}" in
    "terminal")
        start_terminal
        ;;
    "dashboard")
        start_dashboard
        ;;
    "monitor")
        start_monitor
        ;;
    "optimize")
        optimize_system
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown mode: $1"
        show_usage
        exit 1
        ;;
esac 