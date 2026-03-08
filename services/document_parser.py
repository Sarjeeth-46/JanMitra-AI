"""
Document Parser Service for JanMitra AI

Extracts text from uploaded documents (PDF/image) and parses
structured user profile data from the extracted text.
Uses pdfminer.six for PDF text extraction (no LLM, no OCR).
For images, instructs the user to use a text-based PDF instead.
"""

import io
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Reuse AudioParser's field extraction logic
from services.audio_parser import AudioParser

_parser = AudioParser()


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract embedded text from a PDF using pdfminer.six.

    Args:
        pdf_bytes: Raw PDF file bytes

    Returns:
        Extracted text string (may be empty if PDF is image-only)
    """
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams

        output = io.StringIO()
        extract_text_to_fp(
            io.BytesIO(pdf_bytes),
            output,
            laparams=LAParams(),
            output_type="text",
            codec="utf-8",
        )
        text = output.getvalue()
        logger.info(
            "PDF text extraction complete",
            extra={
                "event": "pdf_text_extracted",
                "text_length": len(text),
            },
        )
        return text.strip()
    except ImportError:
        logger.error("pdfminer.six not installed")
        raise
    except Exception as e:
        logger.warning(
            "PDF text extraction failed",
            extra={"event": "pdf_extraction_error", "error": str(e)},
        )
        return ""


def parse_document(
    file_bytes: bytes,
    file_extension: str,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Parse a document and extract structured profile data.

    Args:
        file_bytes: Raw file bytes
        file_extension: Extension like '.pdf', '.jpg', '.png'

    Returns:
        Tuple of (success, message, extracted_data)
        - success: True if data was extracted
        - message: Human-readable result message
        - extracted_data: Partial UserProfile dict (may be empty)
    """
    ext = file_extension.lower()
    logger.info(
        "Starting document parsing",
        extra={"event": "document_parse_started", "extension": ext},
    )

    # ------------------------------------------------------------------ PDF --
    if ext == ".pdf":
        raw_text = _extract_text_from_pdf(file_bytes)

        if not raw_text:
            return (
                False,
                "The uploaded PDF appears to be scanned (image-only) and cannot be read by "
                "our text extractor. Please upload a text-based PDF or fill the form manually.",
                {},
            )

        # Reuse audio_parser regex logic on the extracted text
        parsed = _parser.parse_transcript(raw_text)
        validated = _parser.validate_profile(parsed)

        # Remove default zero-values that were not actually extracted
        # (audio_parser.validate_profile sets age/income/land_size to 0 by default)
        for field in ("age", "income", "land_size"):
            raw_val = parsed.get(field)
            if raw_val is None and validated.get(field) == 0:
                validated.pop(field, None)

        if not validated:
            return (
                True,
                "Document uploaded but no recognisable profile data was found. "
                "Please fill the form manually or ensure the document contains fields "
                "like name, age, state, occupation, and income.",
                {},
            )

        logger.info(
            "Document parsed successfully",
            extra={
                "event": "document_parse_complete",
                "fields_extracted": list(validated.keys()),
            },
        )
        return (
            True,
            f"Successfully extracted {len(validated)} field(s) from the document.",
            validated,
        )

    # -------------------------------------------------- Image (JPG / PNG) --
    elif ext in (".jpg", ".jpeg", ".png"):
        return (
            True,
            "Image document received. Automatic data extraction from images is not yet supported. "
            "Please upload a text-based PDF for automatic form filling, or fill the form manually.",
            {},
        )

    else:
        return (
            False,
            f"Unsupported file type '{ext}'. Please upload a PDF, JPG, or PNG file.",
            {},
        )
