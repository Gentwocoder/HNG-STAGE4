#!/bin/bash

# User Service Setup Script
# This script sets up the development environment for the User Service

set -e  # Exit on error

echo "=================================="
echo "User Service Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
    echo -e "${YELLOW}!${NC} Please update .env with your configuration"
else
    echo -e "${YELLOW}!${NC} .env file already exists"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir logs
    echo -e "${GREEN}✓${NC} Logs directory created"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Migrations completed"

# Create superuser prompt
echo ""
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To access admin panel:"
echo "  http://localhost:8000/admin/"
echo ""
echo "API Base URL:"
echo "  http://localhost:8000/api/v1/users/"
echo ""
echo "Health check:"
echo "  http://localhost:8000/api/v1/users/health/"
echo ""
