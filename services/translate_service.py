"""
Translate Service for JanMitra AI.

Wraps Amazon Translate with:
  - In-memory LRU cache to avoid re-translating identical strings.
  - Crash-proof fallback: always returns a string, never raises.
  - Short language code normalisation (e.g. 'hi-IN' → 'hi').
"""
import boto3
import logging
from functools import lru_cache
from typing import Optional
from models.config import Settings
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
settings = Settings()

# Supported short language codes for AWS Translate
SUPPORTED_LANGS = {"en", "hi", "ta", "te", "bn", "mr", "kn", "ml"}

# Simple in-process translation cache (up to 512 entries per worker)
_translation_cache: dict = {}
_CACHE_MAX = 512


def _cache_key(text: str, src: str, tgt: str) -> str:
    return f"{src}::{tgt}::{hash(text)}"


def _try_cache(text: str, src: str, tgt: str) -> Optional[str]:
    return _translation_cache.get(_cache_key(text, src, tgt))


def _put_cache(text: str, src: str, tgt: str, result: str):
    if len(_translation_cache) >= _CACHE_MAX:
        # Evict oldest entry (Python 3.7+ dicts are ordered)
        oldest_key = next(iter(_translation_cache))
        del _translation_cache[oldest_key]
    _translation_cache[_cache_key(text, src, tgt)] = result


def _normalise_lang(lang: str) -> str:
    """Convert 'hi-IN' → 'hi', 'auto' stays 'auto'."""
    if not lang or lang.lower() == "auto":
        return "auto"
    short = lang.split("-")[0].lower()
    return short if short in SUPPORTED_LANGS else "en"


class TranslateService:
    def __init__(self):
        client_kwargs = {"region_name": settings.aws_region}
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.translate_client = boto3.client("translate", **client_kwargs)
        logger.info("TranslateService initialized")

    async def translate_text(
        self,
        text: str,
        source_lang: str = "auto",
        target_lang: str = "en",
    ) -> tuple[str, str]:
        """
        Translate text from source_lang → target_lang.

        Returns (translated_text, detected_source_lang).
        Falls back to original text if translation fails (demo safe).
        Uses an in-process cache to skip duplicate calls and reduce latency.
        """
        if not text or not text.strip():
            return text, source_lang

        src = _normalise_lang(source_lang)
        tgt = _normalise_lang(target_lang)

        # Skip translation if same language
        if src != "auto" and src == tgt:
            return text, src

        # Check cache first
        cached = _try_cache(text, src, tgt)
        if cached is not None:
            logger.debug("[Translate] Cache HIT %s→%s", src, tgt)
            return cached, src

        try:
            response = await run_in_threadpool(
                self.translate_client.translate_text,
                Text=text[:5000],          # AWS limit
                SourceLanguageCode=src,
                TargetLanguageCode=tgt,
            )
            translated = response.get("TranslatedText", text)
            actual_src = response.get("SourceLanguageCode", src)

            _put_cache(text, src, tgt, translated)
            logger.info("[Translate] %s→%s: '%s' → '%s'", actual_src, tgt, text[:60], translated[:60])
            return translated, actual_src

        except Exception as e:
            logger.warning("[Translate] FAILED %s→%s – returning original. %s", src, tgt, e)
            # Crash-proof: return the original text so the pipeline continues
            return text, src
