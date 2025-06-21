#!/bin/bash

echo "🚀 Starting GotLockz Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip3 install Flask Flask-CORS
fi

# Change to dashboard directory
cd dashboard

# Initialize database and start dashboard
echo "🌐 Starting dashboard at http://localhost:5000"
echo "📊 Press Ctrl+C to stop the dashboard"
echo ""

python3 app.py 