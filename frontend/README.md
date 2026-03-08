# JanMitra AI - Frontend

Professional production-ready frontend for JanMitra AI Government Scheme Eligibility Assistant.

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and optimized builds
- **TailwindCSS** for styling with dark mode support
- **React Router** for navigation
- **Axios** for API communication
- **Context API** for state management
- **Lucide React** for icons
- **React Hot Toast** for notifications

## Features

✅ Modern, minimal, government-grade professional UI
✅ Full Dark Mode + Light Mode with system preference detection
✅ Theme persistence using localStorage
✅ Responsive design (mobile + desktop)
✅ Voice input for form filling
✅ Document upload with data extraction
✅ Real-time chat assistant (side drawer)
✅ Eligibility evaluation with ranked results
✅ Clean component architecture
✅ Type-safe with TypeScript
✅ Smooth animations and transitions

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Layout.tsx       # Main layout with header/footer
│   │   ├── ChatPanel.tsx    # Chat assistant drawer
│   │   ├── VoiceInput.tsx   # Voice recording component
│   │   └── DocumentUpload.tsx # Document upload component
│   ├── pages/               # Page components
│   │   ├── LandingPage.tsx  # Home page
│   │   ├── EligibilityFormPage.tsx # Form page
│   │   └── ResultsPage.tsx  # Results display
│   ├── context/             # React Context providers
│   │   ├── ThemeContext.tsx # Theme management
│   │   └── AppContext.tsx   # Global app state
│   ├── services/            # API service layer
│   │   └── api.ts           # Axios instance & API calls
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts         # All interfaces
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── vite.config.ts           # Vite config
├── tailwind.config.js       # Tailwind config
└── postcss.config.js        # PostCSS config
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Configure environment variables:**
   Edit `.env` file:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Development

**Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

**Features in dev mode:**
- Hot Module Replacement (HMR)
- Fast refresh
- API proxy to backend (no CORS issues)

### Build for Production

**Create optimized production build:**
```bash
npm run build
```

**Preview production build:**
```bash
npm run preview
```

**Build output:**
- Optimized bundle in `dist/` directory
- Minified CSS and JavaScript
- Tree-shaken dependencies
- Ready for deployment

## Color Scheme

### Light Mode
- **Primary Blue:** `#2563eb` (primary-600)
- **Saffron Accent:** `#f97316` (saffron-500)
- **Background:** `#f9fafb` (gray-50)
- **Cards:** `#ffffff` (white)

### Dark Mode
- **Primary Blue:** `#3b82f6` (primary-500)
- **Saffron Accent:** `#fb923c` (saffron-400)
- **Background:** `#111827` (gray-900)
- **Cards:** `#1f2937` (gray-800)

## API Integration

### Endpoints Used

1. **GET /health**
   - Health check
   - Response: `{ status: "healthy", timestamp: "..." }`

2. **POST /evaluate**
   - Evaluate eligibility
   - Body: `UserProfile` object
   - Response: Array of `EvaluationResult`

3. **POST /chat**
   - Chat with assistant
   - Body: `{ message: string, history: ChatMessage[] }`
   - Response: `{ response: string }`

4. **POST /upload-audio**
   - Upload voice recording
   - Body: FormData with audio file
   - Response: `{ success: boolean, transcript: string, extracted_data?: Partial<UserProfile> }`

5. **POST /upload-document**
   - Upload document for parsing
   - Body: FormData with document file
   - Response: `{ success: boolean, message: string, extracted_data?: Partial<UserProfile> }`

### API Service Layer

Centralized API client in `src/services/api.ts`:
- Axios instance with base URL from environment
- Request/response interceptors for logging
- Error handling
- Type-safe API methods

## State Management

### ThemeContext
- Manages light/dark theme
- Persists preference in localStorage
- Detects system preference on first load

### AppContext
- User profile data
- Evaluation results
- Chat history
- Global state methods

## Component Guide

### Layout
- Header with logo and theme toggle
- Chat panel toggle button
- Responsive navigation
- Footer

### ChatPanel
- Side drawer with chat interface
- Message history
- Real-time responses
- Auto-scroll to latest message

### VoiceInput
- Microphone recording
- Visual feedback (pulse animation)
- Audio processing
- Auto-fill form fields

### DocumentUpload
- Drag-and-drop file upload
- File type validation
- Processing indicator
- Success confirmation

### Pages

**LandingPage:**
- Hero section
- Feature highlights
- How it works
- CTA button

**EligibilityFormPage:**
- User profile form
- Voice input integration
- Document upload
- Form validation
- Submit to backend

**ResultsPage:**
- Summary statistics
- Eligible schemes (green)
- Partially eligible (yellow)
- Not eligible (red)
- Missing fields/failed conditions
- Application buttons

## Dark Mode Implementation

Uses Tailwind's class-based dark mode:

1. **Toggle:** Button in header switches theme
2. **Persistence:** Saved to localStorage
3. **System Preference:** Detected on first load
4. **Classes:** `dark:` prefix for dark mode styles
5. **Transitions:** Smooth color transitions

## Responsive Design

- Mobile-first approach
- Breakpoints: `sm:`, `md:`, `lg:`, `xl:`
- Flexible grid layouts
- Touch-friendly buttons
- Collapsible sections

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Modern mobile browsers

## Deployment

### Static Hosting (Netlify, Vercel, etc.)

1. Build the project:
   ```bash
   npm run build
   ```

2. Deploy `dist/` directory

3. Configure environment variables in hosting platform

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### API Connection Issues
- Verify backend is running on correct port
- Check `VITE_API_BASE_URL` in `.env`
- Check browser console for CORS errors

### Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `rm -rf .vite`
- Check Node.js version: `node --version` (should be 18+)

### Theme Not Persisting
- Check browser localStorage is enabled
- Clear localStorage: `localStorage.clear()`

## Performance

- Lazy loading for routes
- Optimized bundle size
- Tree-shaking unused code
- Minified assets
- Gzip compression ready

## Security

- No sensitive data in localStorage
- API calls over HTTPS in production
- Input validation on forms
- XSS protection via React
- CSRF tokens (if backend implements)

## Contributing

1. Follow existing code structure
2. Use TypeScript for type safety
3. Follow Tailwind utility-first approach
4. Test on both light and dark modes
5. Ensure responsive on mobile

## License

Built for AI for Bharat Hackathon 2026
