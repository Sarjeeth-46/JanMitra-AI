"""
Services and FAQs Routes

Provides static data for the Services and FAQ pages.
Also exposes GET /api/services and GET /api/faqs.
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["content"])


# ─── FAQ Data ────────────────────────────────────────────────────────────────
FAQS = [
    {
        "id": 1,
        "question": "What is JanMitra AI?",
        "answer": "JanMitra AI is an AI-powered GovTech platform that helps Indian citizens discover and apply for government welfare schemes using voice, text, and documents in their native language."
    },
    {
        "id": 2,
        "question": "Which languages are supported?",
        "answer": "JanMitra AI supports English, Hindi (हिंदी), Tamil (தமிழ்), Telugu (తెలుగు), Bengali (বাংলা), Marathi (मराठी), Kannada (ಕನ್ನಡ), and Malayalam (മലയാളം)."
    },
    {
        "id": 3,
        "question": "How do I check my eligibility?",
        "answer": "Click 'Start Eligibility Check' on the home page. Fill in your basic details (age, income, occupation, state, category) or upload an Aadhaar / Income Certificate to auto-fill the form."
    },
    {
        "id": 4,
        "question": "How do I upload documents?",
        "answer": "Go to 'Upload Documents'. Drag and drop your Aadhaar Card or Income Certificate (PDF, JPG, or PNG). Our AI will automatically extract and pre-fill your profile details."
    },
    {
        "id": 5,
        "question": "Is my personal data secure?",
        "answer": "Yes. JanMitra AI uses Zero-Trust security with encrypted HTTPS, JWT authentication, and no permanent storage of raw documents. Data is processed per Indian data protection standards."
    },
    {
        "id": 6,
        "question": "Which schemes does JanMitra cover?",
        "answer": "We cover 500+ central and state government schemes including PM-KISAN, Ayushman Bharat (PM-JAY), PM Awas Yojana, PMEGP, National Scholarship Portal, PM Fasal Bima, and many more."
    },
    {
        "id": 7,
        "question": "How does the voice assistant work?",
        "answer": "Tap the microphone and speak your question in any supported language. Our pipeline automatically detects your language, translates, queries the AI, and replies in your native tongue using voice synthesis."
    },
    {
        "id": 8,
        "question": "What if I don't have internet?",
        "answer": "Currently JanMitra AI requires internet connectivity for AI features. We are working on an offline USSD mode for rural areas with limited connectivity."
    }
]

# ─── Services Data ────────────────────────────────────────────────────────────
SERVICES = [
    {
        "id": "eligibility",
        "title": "Eligibility Checker",
        "description": "AI-powered eligibility check across 500+ government schemes in under 60 seconds.",
        "icon": "CheckCircle",
        "link": "/eligibility",
        "badge": "Most Popular"
    },
    {
        "id": "voice",
        "title": "Voice Assistant",
        "description": "Ask questions in your regional language and get instant voice responses.",
        "icon": "Mic",
        "link": "/voice-assistant",
        "badge": "8 Languages"
    },
    {
        "id": "document",
        "title": "Document Upload & OCR",
        "description": "Upload Aadhaar or Income Certificate to auto-fill your eligibility form instantly.",
        "icon": "FileText",
        "link": "/upload",
        "badge": "AI-Powered"
    },
    {
        "id": "schemes",
        "title": "Scheme Finder",
        "description": "Browse and search all central and state government schemes in one place.",
        "icon": "Search",
        "link": "/schemes",
        "badge": "500+ Schemes"
    },
    {
        "id": "track",
        "title": "Track Application",
        "description": "Monitor the real-time progress of your submitted scheme applications.",
        "icon": "BarChart2",
        "link": "/track-status",
        "badge": "Live Status"
    },
    {
        "id": "profile",
        "title": "Citizen Profile",
        "description": "Maintain your profile for faster eligibility checks and personalized recommendations.",
        "icon": "User",
        "link": "/profile",
        "badge": "Personalized"
    }
]


@router.get("/faqs")
async def get_faqs() -> JSONResponse:
    """Returns the list of FAQs for the Help & FAQ page."""
    return JSONResponse(content={"faqs": FAQS, "total": len(FAQS)})


@router.get("/services")
async def get_services() -> JSONResponse:
    """Returns the list of platform services."""
    return JSONResponse(content={"services": SERVICES, "total": len(SERVICES)})
