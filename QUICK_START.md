# Quick Start - Fix Network Errors

## 🚨 Seeing 404 Errors? Follow These Steps:

### Step 1: Open Two Terminals

```
Terminal 1 (Backend)          Terminal 2 (Frontend)
┌─────────────────────┐      ┌─────────────────────┐
│ $ python main.py    │      │ $ cd frontend       │
│                     │      │ $ npm run dev       │
│ Backend running on  │      │                     │
│ http://0.0.0.0:8000 │      │ Frontend running on │
│                     │      │ http://localhost:3000│
└─────────────────────┘      └─────────────────────┘
```

### Step 2: Run Commands

**Terminal 1 (Backend)**:
```bash
cd /path/to/janmitra-backend
python main.py
```

**Terminal 2 (Frontend)**:
```bash
cd /path/to/janmitra-backend/frontend
npm install  # First time only
npm run dev
```

### Step 3: Open Browser

Go to: **http://localhost:3000**

## ✅ Success Indicators

### Backend Terminal Should Show:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend Terminal Should Show:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Browser Network Tab Should Show:
- ✅ Green/Black requests (Status 200)
- ✅ No red requests
- ✅ All resources loading

## 🎯 One-Command Start (Easier!)

### Linux/Mac:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Windows:
```powershell
.\start-dev.ps1
```

This starts both servers automatically!

## 🔍 Troubleshooting

### Problem: Backend won't start

**Error**: "Address already in use"

**Fix**:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Problem: Frontend won't start

**Error**: "Port 3000 is already in use"

**Fix**:
```bash
npx kill-port 3000
```

### Problem: "Module not found"

**Fix**:
```bash
cd frontend
npm install
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────┐
│                   Browser                        │
│            http://localhost:3000                 │
└────────────────────┬────────────────────────────┘
                     │
                     │ Loads React App
                     ▼
┌─────────────────────────────────────────────────┐
│              Frontend Dev Server                 │
│            (Vite on port 3000)                   │
│                                                  │
│  - Serves React app                              │
│  - Hot reload                                    │
│  - Proxies API calls to backend                  │
└────────────────────┬────────────────────────────┘
                     │
                     │ API Calls (/evaluate, /upload-audio)
                     ▼
┌─────────────────────────────────────────────────┐
│              Backend API Server                  │
│            (FastAPI on port 8000)                │
│                                                  │
│  - Handles eligibility evaluation                │
│  - Processes voice transcription                 │
│  - Connects to DynamoDB                          │
└─────────────────────────────────────────────────┘
```

## 🎓 Understanding the Setup

### Why Two Servers?

1. **Frontend (Port 3000)**: 
   - Serves the React app
   - Provides hot reload for development
   - Handles UI/UX

2. **Backend (Port 8000)**:
   - Provides API endpoints
   - Handles business logic
   - Connects to AWS services

### In Production

You'll build the frontend and serve it differently:
```bash
cd frontend
npm run build
# Deploy dist/ folder to hosting
```

## 📝 Daily Development Workflow

### Morning (Start Development)
```bash
# Terminal 1
python main.py

# Terminal 2
cd frontend && npm run dev

# Browser
Open http://localhost:3000
```

### Evening (Stop Development)
```bash
# Press Ctrl+C in both terminals
```

## 🆘 Still Having Issues?

1. **Read**: `NETWORK_ERRORS_FIX.md` - Detailed troubleshooting
2. **Read**: `DEVELOPMENT_SETUP.md` - Complete setup guide
3. **Check**: Both terminals for error messages
4. **Verify**: Ports 3000 and 8000 are not blocked

## ✨ Quick Commands Reference

```bash
# Start backend
python main.py

# Start frontend
cd frontend && npm run dev

# Check backend health
curl http://localhost:8000/health

# Kill port 3000
npx kill-port 3000

# Kill port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Reinstall frontend dependencies
cd frontend && rm -rf node_modules && npm install
```

## 🎉 You're Ready!

Once both servers are running and you can access `http://localhost:3000`, you're all set!

The network errors will be gone and you can start developing. 🚀
