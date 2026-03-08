"""
Chat Service for JanMitra AI

Implements a rule-based FAQ chatbot that answers questions about
government schemes and the eligibility process. Uses keyword matching
(no LLM) consistent with the project's deterministic design philosophy.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# Scheme knowledge base
SCHEME_INFO = {
    "PM-KISAN": {
        "keywords": ["pm kisan", "pmkisan", "kisan", "pm-kisan", "samman nidhi"],
        "description": "PM Kisan Samman Nidhi provides income support of ₹6,000 per year to small and marginal farmer families.",
        "eligibility": "Eligibility: Must be a farmer, own ≤ 2 hectares of land. Income must not exceed ₹2 lakh/year.",
        "how_to_apply": "Apply at pmkisan.gov.in or visit your nearest Common Service Centre (CSC).",
        "benefit": "₹6,000 per year in three installments of ₹2,000 directly to bank account.",
    },
    "Ayushman Bharat": {
        "keywords": ["ayushman", "ayushman bharat", "pmjay", "pm jay", "health insurance", "health scheme"],
        "description": "Ayushman Bharat PM-JAY provides health cover of ₹5 lakh per family per year for secondary and tertiary hospitalisation.",
        "eligibility": "Eligibility: Families in SECC database, BPL categories. Annual income ≤ ₹5 lakh. ST/SC/OBC families are prioritised.",
        "how_to_apply": "Apply at pmjay.gov.in or visit your nearest Ayushman Bharat empanelled hospital.",
        "benefit": "₹5 lakh per family per year for hospitalisation expenses.",
    },
    "PM Awas Yojana": {
        "keywords": ["awas", "pmay", "pm awas", "housing", "house scheme", "pradhan mantri awas"],
        "description": "Pradhan Mantri Awas Yojana provides financial assistance to economically weaker sections for construction or enhancement of houses.",
        "eligibility": "Eligibility: EWS/LIG/MIG families without a pucca house. Annual income up to ₹18 lakh (for MIG-II).",
        "how_to_apply": "Apply at pmaymis.gov.in or visit your local urban local body or Gram Panchayat.",
        "benefit": "Subsidy up to ₹2.67 lakh on home loan interest for EWS/LIG category.",
    },
    "MGNREGA": {
        "keywords": ["mgnrega", "mgnregs", "narega", "nrega", "employment guarantee", "work guarantee"],
        "description": "Mahatma Gandhi National Rural Employment Guarantee Act provides at least 100 days of guaranteed wage employment per year to rural households.",
        "eligibility": "Eligibility: Adult members of any rural household willing to do manual unskilled work.",
        "how_to_apply": "Register at your nearest Gram Panchayat by submitting a job card application.",
        "benefit": "Minimum 100 days of paid employment per year at state-notified minimum wages.",
    },
    "PM Jan Dhan Yojana": {
        "keywords": ["jan dhan", "jandhan", "pmjdy", "jan dhan yojana", "bank account scheme"],
        "description": "Pradhan Mantri Jan Dhan Yojana ensures access to financial services such as banking, savings, remittance, credit, insurance, and pension.",
        "eligibility": "Eligibility: Any Indian citizen who does not have a bank account, with no minimum balance requirement.",
        "how_to_apply": "Visit any bank branch or Business Correspondent with ID proof and address proof.",
        "benefit": "Zero-balance account, RuPay debit card, ₹1 lakh accident insurance, ₹30,000 life cover.",
    },
}

GREETINGS = ["hello", "hi", "hey", "namaste", "namaskar", "good morning", "good afternoon", "good evening"]
THANKS = ["thank", "thanks", "thank you", "dhanyawad", "shukriya"]
HELP_KEYWORDS = ["help", "what can you do", "how do you work", "what is janmitra", "who are you"]
ELIGIBILITY_KEYWORDS = ["eligible", "eligibility", "qualify", "am i eligible", "who can apply", "criteria"]
HOW_TO_APPLY_KEYWORDS = ["apply", "how to apply", "application", "register", "sign up"]
BENEFIT_KEYWORDS = ["benefit", "amount", "money", "how much", "rupees", "payment"]
ALL_SCHEMES_KEYWORDS = ["all schemes", "list schemes", "schemes available", "what schemes", "show schemes", "schemes"]


FALLBACK_RESPONSE = (
    "I'm JanMitra AI's assistant. I can help you with information about these government schemes:\n\n"
    "• **PM-KISAN** – Income support for farmers\n"
    "• **Ayushman Bharat** – Health insurance up to ₹5 lakh\n"
    "• **PM Awas Yojana** – Housing assistance\n"
    "• **MGNREGA** – Employment guarantee\n"
    "• **PM Jan Dhan Yojana** – Financial inclusion\n\n"
    "You can ask me things like:\n"
    "- \"Tell me about PM-KISAN\"\n"
    "- \"How do I apply for Ayushman Bharat?\"\n"
    "- \"What are the benefits of MGNREGA?\"\n"
    "- \"Am I eligible for PM Awas Yojana?\"\n\n"
    "Or go back and use the **eligibility checker** to find schemes you qualify for!"
)


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return re.sub(r"[^\w\s]", " ", text.lower()).strip()


def _match_scheme(text: str) -> Optional[str]:
    """Return the first scheme whose keywords are found in the text."""
    for scheme_name, info in SCHEME_INFO.items():
        for kw in info["keywords"]:
            if kw in text:
                return scheme_name
    return None


def _build_scheme_response(scheme_name: str, text: str) -> str:
    """Build a detailed scheme response based on what the user is asking."""
    info = SCHEME_INFO[scheme_name]
    response_parts = [f"**{scheme_name}**\n\n{info['description']}"]

    # Check if user is asking about something specific
    if any(kw in text for kw in HOW_TO_APPLY_KEYWORDS):
        response_parts.append(f"\n\n📋 **How to Apply:** {info['how_to_apply']}")
    elif any(kw in text for kw in BENEFIT_KEYWORDS):
        response_parts.append(f"\n\n💰 **Benefits:** {info['benefit']}")
    elif any(kw in text for kw in ELIGIBILITY_KEYWORDS):
        response_parts.append(f"\n\n✅ **Eligibility:** {info['eligibility']}")
    else:
        # Provide all info
        response_parts.append(f"\n\n✅ {info['eligibility']}")
        response_parts.append(f"\n\n💰 **Benefits:** {info['benefit']}")
        response_parts.append(f"\n\n📋 **How to Apply:** {info['how_to_apply']}")

    response_parts.append(
        "\n\nWould you like to check your eligibility? Use the **Eligibility Checker** on the form page!"
    )
    return "".join(response_parts)


def _list_all_schemes() -> str:
    """Return a formatted list of all available schemes."""
    lines = ["Here are all the government schemes I know about:\n"]
    for name, info in SCHEME_INFO.items():
        lines.append(f"• **{name}** – {info['description']}")
    lines.append("\nAsk me about any specific scheme for more details!")
    return "\n".join(lines)


def generate_chat_response(message: str, history: List[Dict[str, str]]) -> str:
    """
    Generate a rule-based chat response.

    Args:
        message: The user's current message
        history: List of previous messages with 'role' and 'content' keys

    Returns:
        Assistant response string
    """
    normalized = _normalize(message)
    logger.info(
        "Processing chat message",
        extra={
            "event": "chat_message_received",
            "message_length": len(message),
            "history_length": len(history),
        },
    )

    # Greetings
    if any(g in normalized for g in GREETINGS):
        return (
            "Namaste! 🙏 I'm JanMitra AI's assistant. I'm here to help you understand "
            "government schemes and eligibility. What would you like to know?"
        )

    # Thank you
    if any(t in normalized for t in THANKS):
        return (
            "You're welcome! 😊 If you have more questions about government schemes, "
            "feel free to ask. Best of luck with your applications!"
        )

    # Help / who are you
    if any(kw in normalized for kw in HELP_KEYWORDS):
        return FALLBACK_RESPONSE

    # List all schemes
    if any(kw in normalized for kw in ALL_SCHEMES_KEYWORDS):
        return _list_all_schemes()

    # Scheme-specific response
    matched_scheme = _match_scheme(normalized)
    if matched_scheme:
        return _build_scheme_response(matched_scheme, normalized)

    # Eligibility general question
    if any(kw in normalized for kw in ELIGIBILITY_KEYWORDS):
        return (
            "To check your eligibility for government schemes, please use the **Eligibility Checker** "
            "on the form page. Fill in your name, age, income, state, occupation, and category, "
            "and our system will instantly tell you which schemes you qualify for.\n\n"
            "You can also ask me about a specific scheme's eligibility criteria, for example:\n"
            "\"What are the eligibility criteria for PM-KISAN?\""
        )

    # How to apply general question
    if any(kw in normalized for kw in HOW_TO_APPLY_KEYWORDS):
        return (
            "Each scheme has its own application process. Which scheme are you interested in?\n\n"
            "For example, you can ask:\n"
            "- \"How do I apply for Ayushman Bharat?\"\n"
            "- \"How to apply for PM Awas Yojana?\"\n\n"
            "Or use the **Eligibility Checker** to find which schemes you qualify for first!"
        )

    # Fallback
    logger.info(
        "No matching intent found, returning fallback",
        extra={"event": "chat_fallback", "normalized_message": normalized[:100]},
    )
    return FALLBACK_RESPONSE
