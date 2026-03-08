# Fixing Network Errors - Quick Guide

## Problem: 404 Errors in Network Tab

Based on your screenshot, you're seeing failed requests (red in Network tab). Here's how to fix it:

## Root Cause

The frontend is trying to load resources but either:
1. **Backend server is not running** (most likely)
2. **Frontend dev server is not running properly**
3. **Wrong URL being accessed**

## Quick Fix (3 Steps)

### Step 1: Start Backend

```bash
# Open Terminal 1
cd /path/to/janmitra-backend

# If using virtual environment:
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start backend
python main.py
```

**Wait for this message**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Start Frontend

```bash
# Open Terminal 2 (new terminal window)
cd /path/to/janmitra-backend/frontend

# First time only:
npm install

# Start dev server
npm run dev
```

**Wait for this message**:
```
➜  Local:   http://localhost:3000/
```

### Step 3: Access Correct URL

Open browser and go to: **`http://localhost:3000`**

NOT `http://localhost:3000/eligibility` directly!

## Automated Fix (Recommended)

### Linux/Mac:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Windows:
```powershell
.\start-dev.ps1
```

## Verify It's Working

### 1. Check Backend
Open: `http://localhost:8000/health`

Should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T..."
}
```

### 2. Check Frontend
Open: `http://localhost:3000`

Should see: JanMitra AI landing page

### 3. Check Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Refresh page
4. Should see **green/black** requests (200 status)
5. No red (failed) requests

## Still Seeing Errors?

### Error: "Failed to fetch"

**Cause**: Backend not running

**Fix**:
```bash
# Terminal 1
python main.py
```

### Error: "This site can't be reached"

**Cause**: Frontend dev server not running

**Fix**:
```bash
# Terminal 2
cd frontend
npm run dev
```

### Error: Port already in use

**Fix**:
```bash
# Kill port 8000 (backend)
# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
# Note the PID, then:
taskkill /PID <PID> /F

# Kill port 3000 (frontend)
npx kill-port 3000
```

### Error: Module not found

**Fix**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## What You Should See in Network Tab

### ✅ Successful Requests (Status 200)
- `main.tsx` - React app entry
- `index.css` - Styles
- `Layout.tsx` - Layout component
- `LandingPage.tsx` - Home page
- Various `.js` files - Compiled code

### ❌ Failed Requests (Status 404)
If you see these, backend is not running:
- `/health`
- `/evaluate`
- `/upload-audio`

## Development Workflow

### Every Time You Start Development:

1. **Terminal 1**: Start backend
   ```bash
   python main.py
   ```

2. **Terminal 2**: Start frontend
   ```bash
   cd frontend
   npm run dev
   ```

3. **Browser**: Open `http://localhost:3000`

### Keep Both Terminals Open

Don't close them while developing!

## Production vs Development

### Development (Current)
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Two separate servers
- Hot reload enabled

### Production (Later)
- Backend: `https://your-domain.com`
- Frontend: Built and served from CDN or same domain
- Single deployment

## Quick Checklist

Before reporting issues, verify:

- [ ] Backend terminal shows "Uvicorn running on http://0.0.0.0:8000"
- [ ] Frontend terminal shows "Local: http://localhost:3000/"
- [ ] Can access http://localhost:8000/health in browser
- [ ] Can access http://localhost:3000 in browser
- [ ] No firewall blocking ports 3000 or 8000
- [ ] No antivirus blocking Node.js or Python

## Common Mistakes

### ❌ Wrong: Accessing backend directly
`http://localhost:8000` - Shows FastAPI docs, not the app

### ✅ Correct: Accessing frontend
`http://localhost:3000` - Shows JanMitra AI app

### ❌ Wrong: Starting only one server
Need BOTH backend AND frontend running

### ✅ Correct: Both servers running
Terminal 1: Backend, Terminal 2: Frontend

## Need More Help?

1. **Check backend logs**: Look at Terminal 1 for errors
2. **Check frontend console**: F12 → Console tab in browser
3. **Check this file**: `DEVELOPMENT_SETUP.md` for detailed guide
4. **Restart everything**: Close both terminals, start fresh

## Summary

**The fix is simple**: Make sure both servers are running!

1. Terminal 1: `python main.py` (backend)
2. Terminal 2: `npm run dev` (frontend)
3. Browser: `http://localhost:3000`

That's it! 🚀
