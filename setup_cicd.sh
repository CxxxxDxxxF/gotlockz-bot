#!/bin/bash

# GotLockz Bot CI/CD Setup Script
# This script helps set up the CI/CD pipeline for the GotLockz Bot

set -e

echo "🚀 GotLockz Bot CI/CD Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This script must be run from the root of the git repository"
    exit 1
fi

# Check if GitHub Actions directory exists
if [ ! -d ".github/workflows" ]; then
    print_error "GitHub Actions workflows not found. Please ensure you have the CI/CD files."
    exit 1
fi

print_info "Setting up CI/CD pipeline..."

# 1. Check required files
print_info "Checking required files..."

required_files=(
    "requirements.txt"
    "main.py"
    "bot.py"
    "commands.py"
    "config.py"
    ".github/workflows/deploy.yml"
    ".github/workflows/development.yml"
    ".github/workflows/monitor.yml"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "Found $file"
    else
        print_error "Missing required file: $file"
        exit 1
    fi
done

# 2. Check Python environment
print_info "Checking Python environment..."

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# 3. Install development dependencies
print_info "Installing development dependencies..."

pip install --upgrade pip
pip install flake8 black isort mypy pytest pytest-cov pytest-asyncio bandit safety pip-review

print_status "Development dependencies installed"

# 4. Run initial code quality checks
print_info "Running initial code quality checks..."

# Format code
print_info "Formatting code with black..."
black . || print_warning "Black formatting failed"

print_info "Sorting imports with isort..."
isort . || print_warning "Import sorting failed"

# Lint code
print_info "Running flake8 linting..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || print_warning "Flake8 found issues"

# Type checking
print_info "Running mypy type checking..."
mypy . --ignore-missing-imports --no-strict-optional || print_warning "Type checking found issues"

# Security check
print_info "Running security check..."
bandit -r . -f txt -o bandit-report.txt || print_warning "Security check found issues"

# 5. Run tests
print_info "Running tests..."

if [ -d "tests" ]; then
    pytest tests/ -v || print_warning "Some tests failed"
else
    print_warning "No tests directory found"
fi

# 6. Check environment variables
print_info "Checking environment variables..."

env_file=".env"
if [ -f "$env_file" ]; then
    print_status "Found .env file"
    
    # Check for required variables
    required_vars=("DISCORD_TOKEN" "OPENAI_API_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" "$env_file"; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_status "All required environment variables found"
    else
        print_warning "Missing environment variables: ${missing_vars[*]}"
        print_info "Please add these to your .env file"
    fi
else
    print_warning "No .env file found"
    print_info "Please create a .env file with your configuration"
fi

# 7. Setup instructions
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo ""
echo "1. Set up GitHub Secrets:"
echo "   - Go to your repository → Settings → Secrets and variables → Actions"
echo "   - Add the following secrets:"
echo "     * DISCORD_TOKEN"
echo "     * OPENAI_API_KEY"
echo "     * RENDER_SERVICE_ID"
echo "     * RENDER_API_KEY"
echo "     * HF_USERNAME"
echo "     * HF_TOKEN"
echo "     * DISCORD_WEBHOOK_URL (optional)"
echo ""
echo "2. Deploy to Render:"
echo "   - Go to https://dashboard.render.com"
echo "   - Create a new Web Service"
echo "   - Connect your GitHub repository"
echo "   - Set build command: pip install -r requirements.txt"
echo "   - Set start command: python main.py"
echo "   - Add all environment variables"
echo ""
echo "3. Deploy Dashboard to Hugging Face:"
echo "   - Go to https://huggingface.co/spaces"
echo "   - Create a new Space with Gradio SDK"
echo "   - Name it: your-username-gotlockz-dashboard"
echo ""
echo "4. Set up logging channel:"
echo "   - Create a Discord channel for bot logs"
echo "   - Use /setup_logging #channel in your server"
echo ""
echo "5. Test the deployment:"
echo "   - Push to main branch to trigger auto-deploy"
echo "   - Check GitHub Actions for deployment status"
echo "   - Test bot commands in Discord"
echo ""

print_status "CI/CD setup complete!"
print_info "Check DEPLOYMENT.md for detailed instructions"

# 8. Create a summary report
cat > setup_report.txt << EOF
GotLockz Bot CI/CD Setup Report
==============================

Setup completed: $(date)
Python version: $PYTHON_VERSION

Files checked:
$(for file in "${required_files[@]}"; do echo "- $file"; done)

Development dependencies installed:
- flake8 (linting)
- black (code formatting)
- isort (import sorting)
- mypy (type checking)
- pytest (testing)
- bandit (security)
- safety (dependency security)

Next steps:
1. Set up GitHub Secrets
2. Deploy to Render
3. Deploy Dashboard to Hugging Face
4. Set up logging channel
5. Test deployment

For detailed instructions, see DEPLOYMENT.md
EOF

print_status "Setup report saved to setup_report.txt" 