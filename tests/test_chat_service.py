"""
Unit Tests for Chat Service
"""
import pytest
from services.chat_service import generate_chat_response


# ---- Greeting tests ----
def test_greeting_response():
    response = generate_chat_response("hello", [])
    assert "namaste" in response.lower() or "assistant" in response.lower()

def test_hindi_greeting():
    response = generate_chat_response("namaste", [])
    assert len(response) > 10

# ---- Thank you tests ----
def test_thank_you_response():
    response = generate_chat_response("thank you", [])
    assert "welcome" in response.lower() or "luck" in response.lower()

# ---- Scheme-specific tests ----
def test_pm_kisan_response():
    response = generate_chat_response("Tell me about PM-KISAN", [])
    assert "PM-KISAN" in response or "kisan" in response.lower()
    assert "₹" in response or "farmer" in response.lower()

def test_ayushman_bharat_response():
    response = generate_chat_response("What is Ayushman Bharat?", [])
    assert "Ayushman" in response
    assert "₹5 lakh" in response or "health" in response.lower()

def test_mgnrega_response():
    response = generate_chat_response("Tell me about MGNREGA", [])
    assert "MGNREGA" in response
    assert "100 days" in response or "employment" in response.lower()

def test_pm_awas_response():
    response = generate_chat_response("PM Awas Yojana housing scheme", [])
    assert "Awas" in response or "housing" in response.lower()

def test_jan_dhan_response():
    response = generate_chat_response("jan dhan yojana", [])
    assert "Jan Dhan" in response or "bank" in response.lower()

# ---- Intent tests ----
def test_how_to_apply_pm_kisan():
    response = generate_chat_response("How do I apply for PM-KISAN?", [])
    assert "apply" in response.lower() or "pmkisan.gov.in" in response

def test_benefit_ayushman():
    response = generate_chat_response("What is the benefit of Ayushman Bharat?", [])
    assert "₹5 lakh" in response or "benefit" in response.lower()

def test_eligibility_generic():
    response = generate_chat_response("Am I eligible for any scheme?", [])
    assert "eligib" in response.lower()

def test_all_schemes_list():
    response = generate_chat_response("Show me all schemes", [])
    assert "PM-KISAN" in response
    assert "Ayushman" in response
    assert "MGNREGA" in response

def test_list_schemes_keyword():
    response = generate_chat_response("what schemes are available?", [])
    assert "PM-KISAN" in response

# ---- Help tests ----
def test_help_response():
    response = generate_chat_response("what can you do?", [])
    assert "PM-KISAN" in response or "scheme" in response.lower()

# ---- Fallback tests ----
def test_unknown_message_returns_fallback():
    response = generate_chat_response("xyzzy foobar blorp", [])
    assert "scheme" in response.lower() or "PM-KISAN" in response

def test_empty_history_works():
    response = generate_chat_response("hello", [])
    assert len(response) > 0

def test_with_history_still_works():
    history = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Namaste!"},
    ]
    response = generate_chat_response("Tell me about MGNREGA", history)
    assert "MGNREGA" in response
