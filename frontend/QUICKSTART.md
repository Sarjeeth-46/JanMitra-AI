# Quick Start Guide

Get JanMitra AI Frontend running in 3 minutes.

## Prerequisites Check

```bash
# Check Node.js version (need 18+)
node --version

# Check npm version
npm --version
```

## Installation & Run

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies (takes ~2 minutes)
npm install

# 3. Create environment file
cp .env.example .env

# 4. Start development server
npm run dev
```

**That's it!** Open `http://localhost:3000` in your browser.

## Verify Backend Connection

The frontend expects the backend API at `http://localhost:8000`.

**Test backend is running:**
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-26T..."
}
```

## Common Commands

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run lint
```

## Testing the App

### 1. Landing Page
- Visit `http://localhost:3000`
- Click "Start Eligibility Check"

### 2. Fill Form
- Enter your details manually, OR
- Click microphone icon to use voice input, OR
- Upload a document

### 3. View Results
- Click "Check Eligibility"
- See eligible schemes ranked first
- Green = Eligible
- Yellow = Partially Eligible (missing info)
- Red = Not Eligible

### 4. Chat Assistant
- Click chat icon in header (top-right)
- Ask questions about schemes
- Get instant responses

### 5. Dark Mode
- Click moon/sun icon in header
- Theme persists across sessions

## Troubleshooting

### Port 3000 already in use?
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- --port 3001
```

### Backend not connecting?
1. Check backend is running: `curl http://localhost:8000/health`
2. Check `.env` file has correct `VITE_API_BASE_URL`
3. Restart dev server: `Ctrl+C` then `npm run dev`

### Dependencies not installing?
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Next Steps

- Read full [README.md](./README.md) for detailed documentation
- Customize colors in `tailwind.config.js`
- Add new pages in `src/pages/`
- Extend API in `src/services/api.ts`

## Production Deployment

```bash
# Build optimized bundle
npm run build

# Output in dist/ directory
# Deploy dist/ to any static hosting:
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - GitHub Pages
```

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend logs
3. Verify all environment variables are set
4. Review [README.md](./README.md) troubleshooting section
