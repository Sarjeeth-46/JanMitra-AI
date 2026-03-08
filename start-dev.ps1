# JanMitra AI - Development Server Startup (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "JanMitra AI - Development Server Startup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend directory exists
if (-not (Test-Path "main.py")) {
    Write-Host "Error: main.py not found. Please run this script from the backend directory." -ForegroundColor Red
    exit 1
}

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "Error: frontend directory not found." -ForegroundColor Red
    exit 1
}

# Start backend
Write-Host "Starting backend server..." -ForegroundColor Yellow

# Check if virtual environment exists
if (Test-Path "venv\Scripts\activate.ps1") {
    & "venv\Scripts\activate.ps1"
}

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python main.py" -WindowStyle Normal
Write-Host "✓ Backend started" -ForegroundColor Green
Write-Host "  Backend URL: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

# Wait for backend to be ready
Write-Host "Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✓ Backend is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠ Backend may not be ready yet" -ForegroundColor Yellow
}
Write-Host ""

# Start frontend
Write-Host "Starting frontend dev server..." -ForegroundColor Yellow
Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal
Write-Host "✓ Frontend started" -ForegroundColor Green
Write-Host "  Frontend URL: http://localhost:3000" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Both servers are running!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers" -ForegroundColor Gray
Write-Host ""
