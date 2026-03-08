# Development Setup Guide

## Issue: Network Errors in Browser

If you see 404 errors in the browser's Network tab, follow these steps:

## Solution

### 1. Start Backend Server

```bash
# Navigate to backend directory
cd /path/to/janmitra-backend

# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Start backend
python main.py

# Backend should be running on http://localhost:8000
```

Verify backend is running:
```bash
curl http://localhost:8000/health
```

### 2. Start Frontend Dev Server

```bash
# Open new terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Frontend should be running on http://localhost:3000
```

### 3. Access Application

Open browser and go to: `http://localhost:3000`

## Common Issues & Fixes

### Issue 1: Backend Not Running

**Symptoms**: 
- Network tab shows failed requests to `/health`, `/evaluate`, etc.
- Console shows "Failed to fetch" or "Network Error"

**Fix**:
```bash
# Start backend
cd /path/to/backend
python main.py
```

### Issue 2: Frontend Dev Server Not Running

**Symptoms**:
- Page doesn't load at all
- 404 for all resources
- "This site can't be reached"

**Fix**:
```bash
# Start frontend
cd frontend
npm run dev
```

### Issue 3: Port Already in Use

**Symptoms**:
- Error: "Port 3000 is already in use"
- Error: "Port 8000 is already in use"

**Fix**:
```bash
# Kill process on port 3000 (frontend)
npx kill-port 3000

# Kill process on port 8000 (backend)
# Linux/Mac:
lsof -ti:8000 | xargs kill -9
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue 4: CORS Errors

**Symptoms**:
- Console shows "CORS policy" errors
- Network tab shows requests blocked

**Fix**:
Backend CORS is already configured to allow all origins in development.
If still seeing issues, verify backend is running on port 8000.

### Issue 5: Module Not Found

**Symptoms**:
- Frontend shows "Module not found" errors
- Import errors in console

**Fix**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Correct Development Workflow

### Terminal 1: Backend
```bash
cd /path/to/janmitra-backend
source venv/bin/activate  # if using venv
python main.py
```

**Expected output**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

**Expected output**:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Browser
Open: `http://localhost:3000`

## Verification Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can access http://localhost:8000/health
- [ ] Can access http://localhost:3000
- [ ] No errors in browser console
- [ ] No failed requests in Network tab

## Network Tab - What Should You See?

### Successful Requests (Status 200)
- `main.tsx` - Main React app
- `index.css` - Styles
- `Layout.tsx`, `LandingPage.tsx`, etc. - Components
- `/health` - Backend health check (when form loads)

### Expected Behavior
1. Initial page load: Loads React app and assets
2. Navigate to form: May call `/health` to check backend
3. Submit form: Calls `/evaluate` with user data
4. Voice input: Calls `/upload-audio` with audio file

## Debugging Network Errors

### Check Request Details
1. Open DevTools (F12)
2. Go to Network tab
3. Click on failed request
4. Check:
   - **Request URL**: Should match backend URL
   - **Status Code**: 404 = not found, 500 = server error
   - **Response**: Error message details

### Common Status Codes

- **200 OK**: Success
- **400 Bad Request**: Invalid data sent
- **404 Not Found**: Endpoint doesn't exist or backend not running
- **500 Internal Server Error**: Backend error (check backend logs)
- **CORS Error**: CORS not configured (already fixed in our setup)

## Production Deployment

For production, you need to:

1. **Build frontend**:
```bash
cd frontend
npm run build
```

2. **Serve frontend** (choose one):
   - Use nginx to serve `frontend/dist/`
   - Use a static hosting service (Netlify, Vercel)
   - Serve from FastAPI (add static file serving)

3. **Update API URL**:
   - Create `frontend/.env.production`
   - Set `VITE_API_BASE_URL=https://your-backend-domain.com`

## Quick Fix Script

Create `start-dev.sh`:
```bash
#!/bin/bash

# Start backend in background
cd /path/to/backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
cd /path/to/frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Make executable and run:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

## Still Having Issues?

1. **Check backend logs**: Look for errors in terminal running `python main.py`
2. **Check frontend console**: Look for errors in browser DevTools Console tab
3. **Verify ports**: Make sure 3000 and 8000 are not blocked by firewall
4. **Clear cache**: Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
5. **Restart everything**: Stop both servers, restart backend first, then frontend

## Contact

If issues persist:
1. Check backend logs for errors
2. Check browser console for errors
3. Verify both servers are running
4. Check firewall/antivirus settings
