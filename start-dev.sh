#!/bin/bash

echo "=========================================="
echo "JanMitra AI - Development Server Startup"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if backend directory exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: main.py not found. Please run this script from the backend directory.${NC}"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found.${NC}"
    exit 1
fi

# Start backend
echo -e "${YELLOW}Starting backend server...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python main.py &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "  Backend URL: http://localhost:8000"
echo ""

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 3

# Test backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${YELLOW}⚠ Backend may not be ready yet${NC}"
fi
echo ""

# Start frontend
echo -e "${YELLOW}Starting frontend dev server...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "  Frontend URL: http://localhost:3000"
echo ""

echo "=========================================="
echo -e "${GREEN}Both servers are running!${NC}"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for processes
wait
