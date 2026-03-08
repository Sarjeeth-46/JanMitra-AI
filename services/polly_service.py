import boto3
import logging
import base64
from typing import Optional
from botocore.exceptions import ClientError
from models.config import Settings
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
settings = Settings()

# ─── Language → Polly Voice Configuration ────────────────────────────────────
# engine: 'neural' | 'standard'
# Kajal is the only Neural voice with Indian-English/Hindi support.
# Aditi/Raveena are Standard voices that cover most Indian scripts via SSML.
POLLY_VOICE_CONFIG = {
    "en":  {"voice_id": "Kajal",   "engine": "neural",   "lang_code": "en-IN"},
    "hi":  {"voice_id": "Kajal",   "engine": "neural",   "lang_code": "hi-IN"},
    "ta":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},   # Polly has no native Tamil TTS voice; Aditi (Hindi) provides best approximation
    "te":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},
    "bn":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},
    "mr":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},
    "kn":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},
    "ml":  {"voice_id": "Aditi",   "engine": "standard", "lang_code": "hi-IN"},
}

# Ultimate fallback if language is unknown
_DEFAULT_CONFIG = {"voice_id": "Kajal", "engine": "neural", "lang_code": "en-IN"}


class PollyService:
    def __init__(self):
        client_kwargs = {"region_name": settings.aws_region}
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.polly_client = boto3.client('polly', **client_kwargs)
        logger.info("PollyService initialized with %d language configs", len(POLLY_VOICE_CONFIG))

    async def synthesize_speech(self, text: str, language_code: str = "en") -> str:
        """
        Synthesizes text to speech using Amazon Polly.
        Returns a base64-encoded MP3 string, or "" if Polly is unavailable.

        language_code can be short ('hi') or full ('hi-IN').
        """
        if not text or not text.strip():
            return ""

        # Normalise to short code
        lang = language_code.split("-")[0].lower() if language_code else "en"
        cfg  = POLLY_VOICE_CONFIG.get(lang, _DEFAULT_CONFIG)

        logger.info(
            "[Polly] Synthesizing – lang=%s voice=%s engine=%s",
            lang, cfg["voice_id"], cfg["engine"]
        )

        try:
            audio_b64 = await self._call_polly(text, cfg)
            logger.info("[Polly] SUCCESS – %d chars of audio", len(audio_b64))
            return audio_b64

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.warning("[Polly] %s – trying standard engine fallback", error_code)
            # Retry with standard engine + Aditi
            try:
                fallback_cfg = {"voice_id": "Aditi", "engine": "standard", "lang_code": "hi-IN"}
                audio_b64 = await self._call_polly(text, fallback_cfg)
                return audio_b64
            except Exception as inner:
                logger.error("[Polly] Fallback also failed: %s", inner)
                return ""

        except Exception as e:
            logger.error("[Polly] Unexpected error: %s", e)
            return ""

    async def _call_polly(self, text: str, cfg: dict) -> str:
        """Internal: call synthesize_speech and return base64."""
        response = await run_in_threadpool(
            self.polly_client.synthesize_speech,
            Engine=cfg["engine"],
            LanguageCode=cfg["lang_code"],
            OutputFormat="mp3",
            Text=text[:2999],          # Polly limit is 3000 chars
            VoiceId=cfg["voice_id"]
        )
        if "AudioStream" not in response:
            raise Exception("No AudioStream in Polly response")
        audio_bytes = await run_in_threadpool(response["AudioStream"].read)
        return base64.b64encode(audio_bytes).decode("utf-8")



