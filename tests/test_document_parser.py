"""
Unit Tests for Document Parser Service
"""
import pytest
from services.document_parser import parse_document


# ---- Image file tests (no OCR) ----
def test_jpg_returns_empty_extracted_data():
    fake_bytes = b"\xff\xd8\xff"  # JPEG magic bytes
    success, message, extracted = parse_document(fake_bytes, ".jpg")
    assert success is True
    assert extracted == {}
    assert "image" in message.lower() or "not yet supported" in message.lower()

def test_jpeg_returns_empty_extracted_data():
    fake_bytes = b"\xff\xd8\xff"
    success, message, extracted = parse_document(fake_bytes, ".jpeg")
    assert success is True
    assert extracted == {}

def test_png_returns_empty_extracted_data():
    fake_bytes = b"\x89PNG"
    success, message, extracted = parse_document(fake_bytes, ".png")
    assert success is True
    assert extracted == {}


# ---- Unsupported extension test ----
def test_unsupported_extension():
    success, message, extracted = parse_document(b"data", ".txt")
    assert success is False
    assert "unsupported" in message.lower()
    assert extracted == {}


# ---- PDF tests (testing parse logic via text directly through AudioParser) ----
def test_audio_parser_reuse_on_transcript():
    """Verify that AudioParser can parse the kind of text a PDF might contain."""
    from services.audio_parser import AudioParser
    parser = AudioParser()
    text = "My name is Rajesh Kumar. I am 35 years old. I live in Maharashtra. I am a farmer. I belong to OBC category. My income is 2 lakh."
    parsed = parser.parse_transcript(text)
    validated = parser.validate_profile(parsed)

    # AudioParser reliably extracts these fields via regex
    assert validated.get("state") == "Maharashtra"
    assert validated.get("occupation") == "farmer"
    assert validated.get("category") == "OBC"
    assert validated.get("age") == 35
    assert validated.get("income") == 200000


def test_empty_pdf_text_handling():
    """An empty PDF should return success=False."""
    # We can't easily create a real PDF in a unit test without pdfminer,
    # so we test the branch directly by patching the extraction function.
    import unittest.mock as mock
    with mock.patch("services.document_parser._extract_text_from_pdf", return_value=""):
        success, message, extracted = parse_document(b"%PDF-1.4", ".pdf")
        assert success is False
        assert "scanned" in message.lower() or "text-based" in message.lower()


def test_pdf_no_recognisable_fields():
    """A PDF with text but no parseable fields returns success=True, empty extracted_data."""
    import unittest.mock as mock
    with mock.patch("services.document_parser._extract_text_from_pdf", return_value="Hello world. Blah blah blah."):
        success, message, extracted = parse_document(b"%PDF-1.4", ".pdf")
        assert success is True
        assert extracted == {}


def test_pdf_with_profile_text():
    """A PDF with profile data returns extracted_data dict."""
    import unittest.mock as mock
    sample_text = "My name is Priya Sharma. I am 28. I live in Gujarat. I am a student. General category. Income 1 lakh."
    with mock.patch("services.document_parser._extract_text_from_pdf", return_value=sample_text):
        success, message, extracted = parse_document(b"%PDF-1.4", ".pdf")
        assert success is True
        # AudioParser reliably extracts state, occupation, category, and numeric fields
        assert extracted.get("state") == "Gujarat"
        assert extracted.get("occupation") == "student"
        assert extracted.get("category") == "General"
        assert extracted.get("income") == 100000
