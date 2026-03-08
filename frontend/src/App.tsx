import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AppProvider } from './context/AppContext'
import { ThemeProvider } from './context/ThemeContext'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import EligibilityFormPage from './pages/EligibilityFormPage'
import ResultsPage from './pages/ResultsPage'
import VoiceAssistant from './pages/VoiceAssistant'
import DocumentUpload from './pages/DocumentUpload'
import ServicesPage from './pages/ServicesPage'
import TrackStatusPage from './pages/TrackStatusPage'
import FeedbackPage from './pages/FeedbackPage'
import FAQPage from './pages/FAQPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import ProfilePage from './pages/ProfilePage'
import SchemeApplyPage from './pages/SchemeApplyPage'
import OTPVerifyPage from './pages/OTPVerifyPage'

function App() {
  return (
    <ThemeProvider>
      <AppProvider>
        <AuthProvider>
          <Router>
            <Layout>
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/services" element={<ServicesPage />} />
                <Route path="/eligibility" element={<EligibilityFormPage />} />
                <Route path="/results" element={<ResultsPage />} />
                <Route path="/apply" element={<SchemeApplyPage />} />
                <Route path="/voice-assistant" element={<VoiceAssistant />} />
                <Route path="/upload-document" element={<DocumentUpload />} />
                <Route path="/track" element={<TrackStatusPage />} />
                <Route path="/feedback" element={<FeedbackPage />} />
                <Route path="/faqs" element={<FAQPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/verify-otp" element={<OTPVerifyPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/profile" element={<ProfilePage />} />
              </Routes>
            </Layout>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: 'var(--toast-bg)',
                  color: 'var(--toast-color)',
                },
              }}
            />
          </Router>
        </AuthProvider>
      </AppProvider>
    </ThemeProvider>
  )
}

export default App
