#!/usr/bin/env python3
"""
run_dashboard.py

Simple script to run the GotLockz dashboard.
"""
import os
import sys
from pathlib import Path

# Add the dashboard directory to the Python path
dashboard_path = Path(__file__).parent / 'dashboard'
sys.path.insert(0, str(dashboard_path))

# Change to dashboard directory
os.chdir(dashboard_path)

# Import and run the dashboard
from app import app, init_db

if __name__ == '__main__':
    print("🚀 Starting GotLockz Dashboard...")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Initialize database
    init_db()
    print("✅ Database initialized")
    
    # Run the dashboard
    print("🌐 Dashboard will be available at: http://localhost:8080")
    print("📊 Press Ctrl+C to stop the dashboard")
    
    app.run(debug=True, host='0.0.0.0', port=8080) 