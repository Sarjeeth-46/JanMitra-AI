#!/bin/bash

# JanMitra AI Frontend Setup Script
# Run this script to set up the frontend

echo "========================================"
echo "JanMitra AI Frontend Setup"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Check Node.js installation
echo -e "${YELLOW}Checking Node.js installation...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
    
    # Check if version is 18 or higher
    VERSION_NUMBER=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
    if [ "$VERSION_NUMBER" -lt 18 ]; then
        echo -e "${YELLOW}⚠ Warning: Node.js 18+ is recommended. Current: $NODE_VERSION${NC}"
    fi
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+ from https://nodejs.org${NC}"
    exit 1
fi

# Check npm installation
echo -e "${YELLOW}Checking npm installation...${NC}"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm found: v$NPM_VERSION${NC}"
else
    echo -e "${RED}✗ npm not found. Please install npm${NC}"
    exit 1
fi

echo ""

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
echo -e "${GRAY}This may take 2-3 minutes...${NC}"
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${GRAY}  You can edit .env to change the API URL${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

echo ""

# Check if backend is running
echo -e "${YELLOW}Checking backend connection...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "${GREEN}✓ Backend is running and accessible${NC}"
else
    echo -e "${YELLOW}⚠ Backend not accessible at http://localhost:8000${NC}"
    echo -e "${GRAY}  Make sure to start the backend before using the frontend${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "${NC}1. Start the development server:${NC}"
echo -e "${CYAN}   npm run dev${NC}"
echo ""
echo -e "${NC}2. Open your browser:${NC}"
echo -e "${CYAN}   http://localhost:3000${NC}"
echo ""
echo -e "${NC}3. Make sure backend is running:${NC}"
echo -e "${CYAN}   http://localhost:8000${NC}"
echo ""
echo -e "${YELLOW}For more information, see:${NC}"
echo -e "${GRAY}- README.md (full documentation)${NC}"
echo -e "${GRAY}- QUICKSTART.md (quick start guide)${NC}"
echo -e "${GRAY}- DEPLOYMENT.md (deployment guide)${NC}"
echo ""
