# Deployment Guide

Complete guide for deploying JanMitra AI Frontend to production.

## Pre-Deployment Checklist

- [ ] Backend API is deployed and accessible
- [ ] Environment variables are configured
- [ ] Build completes without errors
- [ ] All features tested in production build
- [ ] Dark mode works correctly
- [ ] Mobile responsive design verified
- [ ] API endpoints return expected data

## Environment Configuration

### Production Environment Variables

Create `.env.production`:

```env
VITE_API_BASE_URL=https://api.janmitra.example.com
```

**Important:** Never commit `.env` files to version control!

## Build for Production

```bash
# Install dependencies
npm install

# Create production build
npm run build

# Test production build locally
npm run preview
```

Build output will be in `dist/` directory.

## Deployment Options

### Option 1: Netlify (Recommended)

**Via Netlify CLI:**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy
netlify deploy --prod
```

**Via Netlify UI:**

1. Push code to GitHub/GitLab
2. Connect repository to Netlify
3. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
4. Add environment variables in Netlify dashboard
5. Deploy

**Netlify Configuration (`netlify.toml`):**

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

### Option 2: Vercel

**Via Vercel CLI:**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

**Via Vercel UI:**

1. Import project from GitHub
2. Configure:
   - Framework: Vite
   - Build command: `npm run build`
   - Output directory: `dist`
3. Add environment variables
4. Deploy

**Vercel Configuration (`vercel.json`):**

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Option 3: AWS S3 + CloudFront

**1. Build the project:**
```bash
npm run build
```

**2. Create S3 bucket:**
```bash
aws s3 mb s3://janmitra-frontend
```

**3. Configure bucket for static hosting:**
```bash
aws s3 website s3://janmitra-frontend \
  --index-document index.html \
  --error-document index.html
```

**4. Upload build files:**
```bash
aws s3 sync dist/ s3://janmitra-frontend --delete
```

**5. Create CloudFront distribution:**
- Origin: S3 bucket
- Default root object: `index.html`
- Error pages: 404 → `/index.html` (for SPA routing)
- SSL certificate: Use ACM certificate

**6. Update DNS:**
- Point domain to CloudFront distribution

### Option 4: Docker + Any Cloud

**Dockerfile:**

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf:**

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

**Build and run:**

```bash
# Build image
docker build -t janmitra-frontend .

# Run container
docker run -p 80:80 janmitra-frontend

# Or with docker-compose
docker-compose up -d
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  frontend:
    build: .
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
```

### Option 5: GitHub Pages

**1. Install gh-pages:**
```bash
npm install --save-dev gh-pages
```

**2. Add to package.json:**
```json
{
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  },
  "homepage": "https://yourusername.github.io/janmitra-frontend"
}
```

**3. Update vite.config.ts:**
```typescript
export default defineConfig({
  base: '/janmitra-frontend/',
  // ... rest of config
})
```

**4. Deploy:**
```bash
npm run deploy
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Check if site is accessible
curl -I https://your-domain.com

# Check API connectivity
curl https://your-domain.com/api/health
```

### 2. Test All Features

- [ ] Landing page loads
- [ ] Navigation works
- [ ] Form submission works
- [ ] Results display correctly
- [ ] Chat assistant works
- [ ] Voice input works (requires HTTPS)
- [ ] Document upload works
- [ ] Dark mode toggle works
- [ ] Mobile responsive

### 3. Performance Optimization

**Enable Gzip/Brotli compression:**
- Most hosting platforms enable this by default
- For custom servers, configure in nginx/apache

**CDN Configuration:**
- Use CloudFront, Cloudflare, or similar
- Cache static assets aggressively
- Set appropriate cache headers

**Monitoring:**
- Set up error tracking (Sentry, LogRocket)
- Monitor API response times
- Track user analytics (Google Analytics, Plausible)

## SSL/HTTPS Configuration

**Important:** Voice input requires HTTPS!

### Let's Encrypt (Free SSL)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Cloudflare (Free SSL)

1. Add domain to Cloudflare
2. Update nameservers
3. Enable "Full (strict)" SSL mode
4. Enable "Always Use HTTPS"

## Environment-Specific Builds

### Staging Environment

```bash
# .env.staging
VITE_API_BASE_URL=https://staging-api.janmitra.com

# Build for staging
npm run build -- --mode staging
```

### Production Environment

```bash
# .env.production
VITE_API_BASE_URL=https://api.janmitra.com

# Build for production
npm run build -- --mode production
```

## Rollback Strategy

### Quick Rollback

**Netlify/Vercel:**
- Use dashboard to rollback to previous deployment
- One-click rollback available

**S3 + CloudFront:**
```bash
# Keep previous builds
aws s3 sync dist/ s3://janmitra-frontend/v1.0.1/

# Rollback by syncing old version
aws s3 sync s3://janmitra-frontend/v1.0.0/ s3://janmitra-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Docker:**
```bash
# Tag images with versions
docker tag janmitra-frontend janmitra-frontend:v1.0.1

# Rollback to previous version
docker run -p 80:80 janmitra-frontend:v1.0.0
```

## Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf node_modules dist .vite
npm install
npm run build
```

### API Not Connecting

1. Check CORS configuration on backend
2. Verify `VITE_API_BASE_URL` is correct
3. Check network tab in browser DevTools
4. Verify SSL certificates are valid

### 404 on Page Refresh

- Configure server to serve `index.html` for all routes
- See nginx.conf example above
- For Netlify/Vercel, add redirects configuration

### Dark Mode Not Working

- Check localStorage is enabled
- Verify Tailwind dark mode is configured
- Check browser console for errors

## Security Checklist

- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] No sensitive data in client code
- [ ] API keys not exposed
- [ ] CORS properly configured
- [ ] Content Security Policy set
- [ ] XSS protection enabled

## Performance Checklist

- [ ] Bundle size optimized (<500KB)
- [ ] Images optimized
- [ ] Lazy loading implemented
- [ ] Code splitting enabled
- [ ] Gzip/Brotli compression
- [ ] CDN configured
- [ ] Cache headers set

## Monitoring & Analytics

### Error Tracking (Sentry)

```bash
npm install @sentry/react
```

```typescript
// src/main.tsx
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  environment: import.meta.env.MODE,
})
```

### Analytics (Google Analytics)

```typescript
// Add to index.html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
```

## Maintenance

### Regular Updates

```bash
# Check for outdated packages
npm outdated

# Update dependencies
npm update

# Update major versions carefully
npm install package@latest
```

### Backup Strategy

- Keep git history clean
- Tag releases: `git tag v1.0.0`
- Backup environment variables
- Document configuration changes

## Support

For deployment issues:
1. Check build logs
2. Verify environment variables
3. Test locally with production build
4. Check hosting platform documentation
5. Review browser console errors
