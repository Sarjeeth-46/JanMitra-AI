"""
Amazon Transcribe Service – JanMitra AI
========================================

Key behaviours:
  • IdentifyLanguage=True is ALWAYS used for 'auto' or unknown lang codes.
  • LanguageOptions restricted to 8 Indian locales for accuracy.
  • If a UI language is explicitly chosen, it is passed as LanguageCode
    (bypasses auto-detection → faster + more accurate).
  • Short transcript retry: if transcript < 2 chars, one retry with a
    broader language set before falling back to a safe default message.
  • S3 fallback so demo keeps running even if S3 is unavailable.
"""

import boto3
import asyncio
import json
import time
import uuid
import logging
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from models.config import Settings
from fastapi.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)
settings = Settings()

# ─── Supported Indian Locales ─────────────────────────────────────────────────
# These are the AWS Transcribe locale codes for IdentifyLanguage mode.
INDIAN_LANGUAGE_OPTIONS = [
    "en-IN",   # Indian English
    "hi-IN",   # Hindi
    "ta-IN",   # Tamil
    "te-IN",   # Telugu
    "kn-IN",   # Kannada
    "ml-IN",   # Malayalam
    "mr-IN",   # Marathi
    "bn-IN",   # Bengali
]

# Short‑code → Transcribe locale (used when UI language is manually selected)
SHORT_TO_LOCALE: Dict[str, str] = {
    "en":    "en-IN",
    "en-in": "en-IN",
    "hi":    "hi-IN",
    "hi-in": "hi-IN",
    "ta":    "ta-IN",
    "ta-in": "ta-IN",
    "te":    "te-IN",
    "te-in": "te-IN",
    "kn":    "kn-IN",
    "kn-in": "kn-IN",
    "ml":    "ml-IN",
    "ml-in": "ml-IN",
    "mr":    "mr-IN",
    "mr-in": "mr-IN",
    "bn":    "bn-IN",
    "bn-in": "bn-IN",
}

# Fallback message when transcription yields nothing
EMPTY_TRANSCRIPT_FALLBACK = "Tell me about government schemes I am eligible for."
EMPTY_TRANSCRIPT_LANGUAGE  = "en-IN"

# Job polling settings
_POLL_INTERVAL_SECONDS = 3
_MAX_POLL_ATTEMPTS     = 40    # 40 × 3s = 120s max wait


def _resolve_locale(language_code: str) -> Optional[str]:
    """
    Converts a UI language code into a Transcribe locale.
    Returns None when auto-detection should be used.
    """
    if not language_code:
        return None
    lc = language_code.strip().lower()
    if lc in ("auto", ""):
        return None
    return SHORT_TO_LOCALE.get(lc) or SHORT_TO_LOCALE.get(lc.split("-")[0])


class TranscribeService:
    def __init__(self):
        client_kwargs = {"region_name": settings.aws_region}
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.s3_client         = boto3.client("s3",         **client_kwargs)
        self.transcribe_client = boto3.client("transcribe", **client_kwargs)
        self.bucket_name       = settings.s3_audio_bucket
        logger.info("[Transcribe] Service initialized with %d language options", len(INDIAN_LANGUAGE_OPTIONS))

    # ─── S3 Upload ────────────────────────────────────────────────────────────

    async def upload_audio_to_s3(self, audio_file: bytes, file_extension: str) -> str:
        """Upload audio to S3. Returns the S3 key (or a mock key on failure)."""
        file_key     = f"audio/{uuid.uuid4()}{file_extension}"
        content_type = "audio/wav" if file_extension == ".wav" else f"audio/{file_extension.lstrip('.')}"
        try:
            await run_in_threadpool(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=file_key,
                Body=audio_file,
                ContentType=content_type,
                CacheControl="no-cache",
            )
            logger.info("[Transcribe] Audio uploaded to S3: %s", file_key)
            return file_key
        except ClientError as e:
            logger.warning("[Transcribe] S3 upload failed (demo mode): %s", e)
            return "demo/fallback_audio.wav"
        except Exception as e:
            logger.warning("[Transcribe] S3 upload error (demo mode): %s", e)
            return "demo/fallback_audio.wav"

    # ─── Job Management ───────────────────────────────────────────────────────

    async def _start_job(self, s3_key: str, locale: Optional[str]) -> str:
        """Start a Transcribe job. Uses IdentifyLanguage if locale is None."""
        job_name = f"janmitra-{uuid.uuid4()}"
        s3_uri   = f"s3://{self.bucket_name}/{s3_key}"
        ext      = s3_key.rsplit(".", 1)[-1].lower()
        # Transcribe uses 'webm' not 'webm;codecs=opus'
        media_fmt = ext if ext in ("mp3", "mp4", "wav", "flac", "ogg", "amr", "webm") else "webm"

        kwargs: Dict[str, Any] = {
            "TranscriptionJobName": job_name,
            "Media":               {"MediaFileUri": s3_uri},
            "MediaFormat":         media_fmt,
            "OutputBucketName":    self.bucket_name,
            "OutputKey":           f"transcripts/{job_name}.json",
        }

        if locale:
            # User explicitly chose a language – skip auto-detect for speed
            kwargs["LanguageCode"] = locale
            logger.info("[Transcribe] Forced locale: %s", locale)
        else:
            # Auto-detect restricted to Indian languages for accuracy
            kwargs["IdentifyLanguage"] = True
            kwargs["LanguageOptions"]  = INDIAN_LANGUAGE_OPTIONS
            kwargs["LanguageIdSettings"] = {
                lang: {"VocabularyName": None} for lang in INDIAN_LANGUAGE_OPTIONS
                # VocabularyName=None is ignored – just signalling preference
            }
            logger.info("[Transcribe] IdentifyLanguage=True, options=%s", INDIAN_LANGUAGE_OPTIONS)

        # Remove None values from LanguageIdSettings (boto3 rejects them)
        if "LanguageIdSettings" in kwargs:
            del kwargs["LanguageIdSettings"]  # Not needed – LanguageOptions is sufficient

        await run_in_threadpool(
            self.transcribe_client.start_transcription_job,
            **kwargs
        )
        logger.info("[Transcribe] Job started: %s", job_name)
        return job_name

    async def _poll_job(self, job_name: str) -> Dict[str, Any]:
        """Poll until job completes. Returns job details dict."""
        for attempt in range(_MAX_POLL_ATTEMPTS):
            resp   = await run_in_threadpool(
                self.transcribe_client.get_transcription_job,
                TranscriptionJobName=job_name
            )
            job    = resp["TranscriptionJob"]
            status = job["TranscriptionJobStatus"]
            if status == "COMPLETED":
                logger.info("[Transcribe] Job %s COMPLETED (attempt %d)", job_name, attempt + 1)
                return job
            if status == "FAILED":
                reason = job.get("FailureReason", "Unknown")
                logger.error("[Transcribe] Job FAILED: %s", reason)
                raise RuntimeError(f"Transcribe job failed: {reason}")
            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        raise TimeoutError(f"Transcribe job timed out after {_MAX_POLL_ATTEMPTS * _POLL_INTERVAL_SECONDS}s")

    async def _fetch_transcript(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Download and parse the transcript JSON from S3."""
        transcript_uri = job["Transcript"]["TranscriptFileUri"]
        s3_key = transcript_uri.split(f"{self.bucket_name}/")[-1]

        resp       = await run_in_threadpool(self.s3_client.get_object, Bucket=self.bucket_name, Key=s3_key)
        body_bytes = await run_in_threadpool(resp["Body"].read)
        data       = json.loads(body_bytes.decode("utf-8"))

        transcript_text = (
            data.get("results", {})
                .get("transcripts", [{}])[0]
                .get("transcript", "")
                .strip()
        )

        # Detect language code from job result
        results = data.get("results", {})
        language_code = "en-IN"  # safe default
        if "language_codes" in results and results["language_codes"]:
            language_code = results["language_codes"][0].get("language_code", "en-IN")
        elif "language_code" in results:
            language_code = results["language_code"]
        # Also check the job-level field (present when LanguageCode was fixed)
        elif "LanguageCode" in job:
            language_code = job["LanguageCode"]

        logger.info(
            "[Transcribe] Result – lang=%s text='%s...'",
            language_code, transcript_text[:60]
        )
        return {"transcript": transcript_text, "language_code": language_code}

    async def _cleanup(self, s3_key: str):
        """Delete audio from S3 (best-effort)."""
        try:
            await run_in_threadpool(self.s3_client.delete_object, Bucket=self.bucket_name, Key=s3_key)
        except Exception as e:
            logger.debug("[Transcribe] Cleanup skipped: %s", e)

    # ─── Public Entry Point ───────────────────────────────────────────────────

    async def transcribe_audio(
        self,
        audio_file: bytes,
        file_extension: str,
        language_code: str = "auto",
        cleanup: bool = True,
    ) -> Dict[str, Any]:
        """
        Full pipeline: upload → start job → poll → fetch transcript.

        language_code behaviour:
          • 'auto' or ''  → IdentifyLanguage=True restricted to Indian locales
          • 'hi' / 'hi-IN' etc. → LanguageCode=hi-IN (bypass auto-detect)

        Short transcript (<2 chars) → one automatic retry with broader options,
        then returns EMPTY_TRANSCRIPT_FALLBACK so the voice pipeline never stalls.
        """
        locale = _resolve_locale(language_code)   # None means auto-detect

        s3_key = await self.upload_audio_to_s3(audio_file, file_extension)
        if s3_key.startswith("demo/"):
            # S3 unavailable – return a safe demo transcript
            logger.warning("[Transcribe] S3 unavailable – returning demo transcript")
            return {
                "transcript":    EMPTY_TRANSCRIPT_FALLBACK,
                "language_code": locale or "en-IN",
            }

        try:
            result = await self._run_single_transcription(s3_key, locale)

            # ── Short transcript retry ────────────────────────────────────────
            if len(result["transcript"]) < 2:
                logger.warning(
                    "[Transcribe] Transcript too short (%d chars) – retrying with broader options",
                    len(result["transcript"])
                )
                # Retry always with auto-detect regardless of user's lang choice
                retry_key = await self.upload_audio_to_s3(audio_file, file_extension)
                if not retry_key.startswith("demo/"):
                    try:
                        result = await self._run_single_transcription(retry_key, locale=None)
                    except Exception as e:
                        logger.warning("[Transcribe] Retry also failed: %s", e)
                    finally:
                        if cleanup:
                            await self._cleanup(retry_key)

            # Final safety: still empty → meaningful fallback
            if len(result["transcript"]) < 2:
                logger.warning("[Transcribe] Still empty after retry – using fallback transcript")
                result["transcript"]    = EMPTY_TRANSCRIPT_FALLBACK
                result["language_code"] = locale or "en-IN"

            return result

        finally:
            if cleanup and not s3_key.startswith("demo/"):
                await self._cleanup(s3_key)

    async def _run_single_transcription(
        self, s3_key: str, locale: Optional[str]
    ) -> Dict[str, Any]:
        """Start → poll → fetch for one transcription attempt."""
        job_name = await self._start_job(s3_key, locale)
        job      = await self._poll_job(job_name)
        return await self._fetch_transcript(job)

    # ─── Legacy helpers (kept for route backward-compat) ─────────────────────

    async def start_transcription(self, s3_key: str, language_code: str = "en-IN") -> str:
        locale = _resolve_locale(language_code) or "en-IN"
        return await self._start_job(s3_key, locale)

    async def check_transcription_status(self, job_name: str) -> Dict[str, Any]:
        resp = await run_in_threadpool(
            self.transcribe_client.get_transcription_job,
            TranscriptionJobName=job_name
        )
        return resp["TranscriptionJob"]

    async def get_transcript_text(self, job_details: Dict[str, Any]) -> Dict[str, Any]:
        return await self._fetch_transcript(job_details)

    async def delete_audio_file(self, s3_key: str) -> None:
        await self._cleanup(s3_key)
