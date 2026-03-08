# JanMitra AI Frontend - Complete Structure

## 📁 Full Directory Tree

```
frontend/
├── public/                          # Static assets
│   └── (add favicon, images here)
│
├── src/
│   ├── components/                  # Reusable UI components
│   │   ├── Layout.tsx              # Main layout with header, footer, chat toggle
│   │   ├── ChatPanel.tsx           # Chat assistant side drawer
│   │   ├── VoiceInput.tsx          # Voice recording component
│   │   └── DocumentUpload.tsx      # Document upload with data extraction
│   │
│   ├── pages/                       # Page components (routes)
│   │   ├── LandingPage.tsx         # Home page with hero and features
│   │   ├── EligibilityFormPage.tsx # Form with voice/document input
│   │   └── ResultsPage.tsx         # Ranked eligibility results display
│   │
│   ├── context/                     # React Context providers
│   │   ├── ThemeContext.tsx        # Dark/light theme management
│   │   └── AppContext.tsx          # Global app state (profile, results, chat)
│   │
│   ├── services/                    # API service layer
│   │   └── api.ts                  # Axios instance + all API methods
│   │
│   ├── hooks/                       # Custom React hooks
│   │   └── useApi.ts               # Hook for API calls with loading/error states
│   │
│   ├── utils/                       # Utility functions
│   │   ├── formatters.ts           # Currency, date, text formatting
│   │   └── validators.ts           # Form validation functions
│   │
│   ├── types/                       # TypeScript type definitions
│   │   └── index.ts                # All interfaces and types
│   │
│   ├── App.tsx                      # Root component with routing
│   ├── main.tsx                     # Application entry point
│   └── index.css                    # Global styles + Tailwind directives
│
├── index.html                       # HTML template
├── package.json                     # Dependencies and scripts
├── tsconfig.json                    # TypeScript configuration
├── tsconfig.node.json              # TypeScript config for Vite
├── vite.config.ts                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS configuration
├── postcss.config.js               # PostCSS configuration
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── README.md                        # Full documentation
├── QUICKSTART.md                   # Quick start guide
├── DEPLOYMENT.md                   # Deployment guide
└── STRUCTURE.md                    # This file
```

## 🎨 Component Architecture

### Layout Hierarchy

```
App
└── ThemeProvider
    └── AppProvider
        └── Router
            └── Layout
                ├── Header (with theme toggle, chat toggle)
                ├── Main Content (routes)
                │   ├── LandingPage
                │   ├── EligibilityFormPage
                │   │   ├── VoiceInput
                │   │   ├── DocumentUpload
                │   │   └── Form
                │   └── ResultsPage
                ├── ChatPanel (drawer)
                └── Footer
```

## 🔄 Data Flow

### State Management

```
ThemeContext
├── theme: 'light' | 'dark'
└── toggleTheme()

AppContext
├── userProfile: UserProfile | null
├── evaluationResults: EvaluationResult[]
├── chatHistory: ChatMessage[]
├── setUserProfile()
├── setEvaluationResults()
├── addChatMessage()
└── clearChatHistory()
```

### API Flow

```
User Action
    ↓
Component
    ↓
api.ts (service layer)
    ↓
Axios Request
    ↓
Backend API
    ↓
Response
    ↓
Update Context/State
    ↓
Re-render UI
```

## 🎯 Key Features by File

### Components

**Layout.tsx**
- Responsive header with logo
- Theme toggle button (moon/sun icon)
- Chat panel toggle button
- Sticky header
- Footer with copyright

**ChatPanel.tsx**
- Side drawer (slides from right)
- Message history display
- User/assistant message bubbles
- Real-time chat with backend
- Auto-scroll to latest message
- Loading indicator

**VoiceInput.tsx**
- Microphone button with pulse animation
- Audio recording using MediaRecorder API
- Upload to backend /upload-audio
- Extract data and auto-fill form
- Visual feedback (recording/processing states)

**DocumentUpload.tsx**
- Drag-and-drop file upload
- File type validation (PDF, JPG, PNG)
- Upload to backend /upload-document
- Extract data and auto-fill form
- Success confirmation

### Pages

**LandingPage.tsx**
- Hero section with gradient logo
- Project description
- "Start Eligibility Check" CTA button
- 3 feature cards (Fast, Secure, Voice-enabled)
- "How It Works" section (3 steps)

**EligibilityFormPage.tsx**
- Voice input section
- Document upload section
- User profile form (7 fields)
- State dropdown (28 Indian states)
- Category dropdown (5 categories)
- Advanced fields toggle (land_size)
- Form validation
- Submit to /evaluate endpoint
- Navigate to results on success

**ResultsPage.tsx**
- Summary statistics (3 cards)
- Eligible schemes (green badges)
- Partially eligible (yellow badges)
- Not eligible (red badges)
- Missing fields list
- Failed conditions list
- "Proceed to Application" buttons
- Back to form button

### Context

**ThemeContext.tsx**
- Manages light/dark theme
- Persists to localStorage
- Detects system preference
- Applies 'dark' class to <html>
- Smooth transitions

**AppContext.tsx**
- Stores user profile
- Stores evaluation results
- Stores chat history
- Provides state update methods
- Shared across all components

### Services

**api.ts**
- Axios instance with base URL
- Request/response interceptors
- Error handling
- Type-safe API methods:
  - checkHealth()
  - evaluateEligibility()
  - sendChatMessage()
  - uploadAudio()
  - uploadDocument()

### Hooks

**useApi.ts**
- Custom hook for API calls
- Manages loading state
- Manages error state
- Returns execute function
- Provides reset function

### Utils

**formatters.ts**
- formatCurrency() - Indian Rupees
- formatDate() - Readable dates
- formatTime() - Readable times
- capitalizeWords()
- snakeToTitle()
- truncate()
- formatFileSize()

**validators.ts**
- validateUserProfile()
- isValidEmail()
- isValidPhone()
- isValidFileType()
- isValidFileSize()

### Types

**index.ts**
- UserProfile interface
- EligibilityRule interface
- Scheme interface
- EvaluationResult interface
- ChatMessage interface
- HealthResponse interface
- DocumentUploadResponse interface
- AudioUploadResponse interface

## 🎨 Styling System

### Tailwind Configuration

**Colors:**
- Primary: Blue shades (50-900)
- Saffron: Orange shades (50-900)
- Gray: For backgrounds and text

**Dark Mode:**
- Class-based: `dark:` prefix
- Applied to <html> element
- Smooth transitions

**Custom Classes:**
- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.input-field` - Form input style
- `.card` - Card container style

### Responsive Breakpoints

- `sm:` - 640px (mobile landscape)
- `md:` - 768px (tablet)
- `lg:` - 1024px (desktop)
- `xl:` - 1280px (large desktop)

## 🔌 API Integration

### Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Health check |
| POST | /evaluate | Evaluate eligibility |
| POST | /chat | Chat with assistant |
| POST | /upload-audio | Upload voice recording |
| POST | /upload-document | Upload document |

### Request/Response Flow

1. **Health Check**
   - Request: None
   - Response: `{ status, timestamp }`

2. **Evaluate Eligibility**
   - Request: `UserProfile` object
   - Response: `EvaluationResult[]` array

3. **Chat**
   - Request: `{ message, history }`
   - Response: `{ response }`

4. **Upload Audio**
   - Request: FormData with audio blob
   - Response: `{ success, transcript, extracted_data }`

5. **Upload Document**
   - Request: FormData with file
   - Response: `{ success, message, extracted_data }`

## 🚀 Build & Deploy

### Development

```bash
npm install          # Install dependencies
npm run dev          # Start dev server (port 3000)
```

### Production

```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

### Output

- Optimized bundle in `dist/`
- Minified CSS and JS
- Tree-shaken dependencies
- Gzip-ready assets

## 📊 Performance Metrics

### Bundle Size Targets

- Initial JS: <200KB (gzipped)
- Initial CSS: <50KB (gzipped)
- Total: <500KB (gzipped)

### Performance Goals

- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Lighthouse Score: >90

## 🔒 Security Features

- HTTPS required for voice input
- No sensitive data in localStorage
- XSS protection via React
- Input validation on forms
- CORS handled by backend
- Environment variables for config

## 📱 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎯 User Flows

### Flow 1: Quick Eligibility Check

1. Land on homepage
2. Click "Start Eligibility Check"
3. Fill form manually
4. Submit
5. View results
6. Click "Proceed to Application"

### Flow 2: Voice Input

1. Navigate to form page
2. Click microphone button
3. Speak details
4. Form auto-fills
5. Submit
6. View results

### Flow 3: Document Upload

1. Navigate to form page
2. Upload document (PDF/image)
3. Data extracted and filled
4. Review and submit
5. View results

### Flow 4: Chat Assistant

1. Click chat icon in header
2. Ask question about schemes
3. Get instant response
4. Continue conversation
5. Close drawer when done

## 🛠️ Development Guidelines

### Adding New Page

1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Update navigation if needed

### Adding New API Endpoint

1. Add method to `src/services/api.ts`
2. Add types to `src/types/index.ts`
3. Use in component with error handling

### Styling New Component

1. Use Tailwind utility classes
2. Add dark mode variants with `dark:`
3. Ensure responsive with breakpoints
4. Test in both themes

### State Management

1. Use Context for global state
2. Use local state for component-specific
3. Use useApi hook for API calls

## 📚 Documentation Files

- **README.md** - Complete documentation
- **QUICKSTART.md** - Get started in 3 minutes
- **DEPLOYMENT.md** - Production deployment guide
- **STRUCTURE.md** - This file (architecture overview)

## 🎓 Learning Resources

### React + TypeScript
- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Vite
- [Vite Guide](https://vitejs.dev/guide/)

### Tailwind CSS
- [Tailwind Docs](https://tailwindcss.com/docs)
- [Dark Mode Guide](https://tailwindcss.com/docs/dark-mode)

### React Router
- [React Router Docs](https://reactrouter.com)

## 🤝 Contributing

1. Follow existing code structure
2. Use TypeScript for type safety
3. Follow Tailwind utility-first approach
4. Test on both light and dark modes
5. Ensure mobile responsive
6. Add comments for complex logic
7. Update documentation

## 📝 Notes

- All components are functional (no class components)
- Hooks are used for state and side effects
- Context API for global state (no Redux needed)
- Axios for API calls (configured in one place)
- Tailwind for all styling (no CSS modules)
- TypeScript for type safety
- Vite for fast development and builds
