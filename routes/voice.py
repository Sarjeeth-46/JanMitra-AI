"""
Voice Routes
Handles audio upload and transcription endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio
import logging
import time

from slowapi import Limiter
from slowapi.util import get_remote_address
from middleware.auth import verify_token

from services.transcribe_service import TranscribeService
from services.audio_parser import AudioParser
from services.eligibility_service import evaluate_eligibility
from services.translate_service import TranslateService
from services.polly_service import PollyService
from services.bedrock_service import BedrockService
from models.user_profile import UserProfile
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# ─── Session Request Registry ─────────────────────────────────────────────────
# Maps session_id -> {"cancel": bool, "request_id": str, "started_at": float}
# Tracks the in-flight voice request so a new one can cancel the previous.
_active_voice_requests: Dict[str, Dict] = {}
_SESSION_TIMEOUT_SECONDS = 30   # safety expiry for stale entries


def _register_request(session_id: str) -> Dict:
    """Register a new request for a session, cancelling any existing one."""
    now = time.time()
    # Cancel any previous in-flight request for this session
    if session_id in _active_voice_requests:
        prev = _active_voice_requests[session_id]
        prev["cancel"] = True
        logger.info(
            f"[SessionLock] Cancelled stale request {prev['request_id']} "
            f"for session {session_id}"
        )
    ctx = {"cancel": False, "request_id": str(uuid.uuid4()), "started_at": now}
    _active_voice_requests[session_id] = ctx
    return ctx


def _release_request(session_id: str, request_id: str):
    """Remove a session's entry only if it still belongs to this request."""
    entry = _active_voice_requests.get(session_id)
    if entry and entry["request_id"] == request_id:
        del _active_voice_requests[session_id]


def _is_cancelled(ctx: Dict) -> bool:
    """Return True if this request has been superseded by a newer one."""
    return ctx.get("cancel", False)

# Initialize services
transcribe_service = TranscribeService()
audio_parser = AudioParser()
translate_service = TranslateService()
polly_service = PollyService()
bedrock_service = BedrockService()


@router.post("/upload-audio")
@limiter.limit("50/minute")
async def upload_audio(
    request: Request,
    audio: UploadFile = File(...),
    token: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Upload audio file, transcribe, parse, and evaluate eligibility
    
    Steps:
    1. Validate audio file
    2. Upload to S3
    3. Transcribe using Amazon Transcribe
    4. Parse transcript to structured data
    5. Evaluate eligibility (optional)
    
    Returns:
        JSON with transcript, structured profile, and eligibility results
    """
    try:
    # --- Validate file type ---
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.webm']
        file_extension = None
        
        for ext in allowed_extensions:
            if audio.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        logger.info(f"Processing audio file: {audio.filename}")
        
        # Read and validate file size (max 10MB) — no python-magic dependency needed
        audio_bytes = await audio.read()
        max_size = 10 * 1024 * 1024  # 10MB

        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: 10MB"
            )
        
        # Step 1: Upload to S3
        logger.info("Uploading audio to S3...")
        s3_key = await transcribe_service.upload_audio_to_s3(audio_bytes, file_extension)
        
        # Step 2: Start transcription job
        logger.info("Starting transcription job...")
        job_id = await transcribe_service.start_transcription(s3_key)
        
        # Return response immediately with job_id
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "message": "Audio upload successful. Transcription job queued."
        }, status_code=202)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )


@router.get("/check-transcription/{job_id}")
@limiter.limit("100/minute")
async def check_transcription_job(
    request: Request,
    job_id: str,
    token: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Check the status of a transcription job and process it if complete.
    
    Returns:
        JSON with job status. If COMPLETED, includes transcript and eligibility data.
    """
    try:
        job_details = await transcribe_service.check_transcription_status(job_id)
        status = job_details['TranscriptionJobStatus']
        
        if status in ['IN_PROGRESS', 'QUEUED']:
            return JSONResponse(content={"status": status}, status_code=200)
            
        if status == 'FAILED':
            failure_reason = job_details.get('FailureReason', 'Unknown error')
            logger.error(f"Transcription failed: {failure_reason}")
            return JSONResponse(
                content={"status": "FAILED", "error": failure_reason},
                status_code=500
            )
            
        # Parse logic if completed
        logger.info("Extracting transcript...")
        transcript = await transcribe_service.get_transcript_text(job_details)
        
        # Clean up audio file from S3 if possible
        try:
            media_uri = job_details.get('Media', {}).get('MediaFileUri', '')
            if media_uri:
                s3_key_to_delete = media_uri.split(f"{transcribe_service.bucket_name}/")[-1]
                await transcribe_service.delete_audio_file(s3_key_to_delete)
        except Exception as e:
            logger.warning(f"Could not delete completed audio file: {e}")
            
        logger.info(f"Parsing transcript to structured data...")
        parsed_profile = audio_parser.parse_transcript(transcript)
        validated_profile = audio_parser.validate_profile(parsed_profile)
        
        eligibility_results = None
        has_required_fields = (validated_profile.get('state') and validated_profile.get('occupation'))
        
        if has_required_fields:
            try:
                user_profile = UserProfile(
                    name=validated_profile.get('name', 'User'),
                    age=validated_profile.get('age', 0),
                    income=validated_profile.get('income', 0),
                    state=validated_profile['state'],
                    occupation=validated_profile['occupation'],
                    category=validated_profile.get('category', 'General'),
                    land_size=validated_profile.get('land_size', 0)
                )
                logger.info("Evaluating eligibility...")
                eligibility_results = await evaluate_eligibility(user_profile)
            except Exception as e:
                logger.warning(f"Eligibility evaluation parsed failure: {e}")
                
        response_content = {
            "status": status,
            "success": True,
            "transcript": transcript,
            "extracted_data": validated_profile,
            "eligibility_results": eligibility_results,
            "message": "Audio processed successfully"
        }
        
        if not has_required_fields:
            response_content["warning"] = "Insufficient data for eligibility evaluation. Please provide state and occupation."
            
        return JSONResponse(content=response_content, status_code=200)
        
    except Exception as e:
        logger.error(f"Failed to check transcription: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Checking transcription status failed: {str(e)}"
        )


@router.post("/transcribe-only")
async def transcribe_only(
    audio: UploadFile = File(...),
    token: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Transcribe audio without parsing or evaluation
    Useful for testing transcription accuracy
    
    Returns:
        JSON with transcript text only
    """
    try:
        # Validate file type
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.webm']
        file_extension = None
        
        for ext in allowed_extensions:
            if audio.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read audio file
        audio_bytes = await audio.read()
        
        # Validate file size
        max_size = 10 * 1024 * 1024  # 10MB
        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: 10MB"
            )
        
        # Transcribe (returns dict with transcript and language_code)
        transcript_data = await transcribe_service.transcribe_audio(
            audio_file=audio_bytes,
            file_extension=file_extension,
            cleanup=True
        )
        
        return JSONResponse(content={
            "success": True,
            "transcript": transcript_data.get("transcript", "")
        }, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/voice/query")
@limiter.limit("50/minute")
async def voice_query(
    request: Request,
    lang: str = "auto",
    audio: UploadFile = File(...),
    token: dict = Depends(verify_token)
) -> JSONResponse:

    """
    Multilingual AI Voice Assistant Pipeline (Demo-Safe + Concurrency-Controlled)
    Speech -> Transcribe -> [cancel check] -> Translate -> [cancel check]
           -> Bedrock AI -> [cancel check] -> Translate -> Polly -> Response

    • Only ONE request runs per session at a time.
    • A new request immediately cancels the previous one.
    • Cancelled pipelines return HTTP 204 so the frontend can ignore them.
    • Every stage has its own fallback — the endpoint NEVER crashes.
    """
    FALLBACK_TRANSCRIPT = "Tell me about schemes for farmers"
    FALLBACK_RESPONSE = (
        "Based on your query, here are some popular government schemes:\n"
        "🌾 PM Kisan Samman Nidhi – ₹6,000/year\n"
        "🏥 Ayushman Bharat – Health coverage up to ₹5 lakh\n"
        "🏠 PM Awas Yojana – Housing subsidy\n"
        "Visit the eligibility checker for a personalised list."
    )

    # ── Session ID & lock registration ──────────────────────────────────────
    session_id = request.headers.get("X-Session-Id") or str(uuid.uuid4())
    ctx = _register_request(session_id)
    request_id = ctx["request_id"]
    logger.info(f"[VoiceQuery] START request_id={request_id} session={session_id}")

    try:
        allowed_extensions = ['.wav', '.mp3', '.m4a', '.webm', '.ogg']
        file_extension = next(
            (ext for ext in allowed_extensions if audio.filename.lower().endswith(ext)),
            '.webm'   # default for browser recordings
        )
        audio_bytes = await audio.read()

        # ── Stage 1: Transcribe ──────────────────────────────────────────────
        native_text   = FALLBACK_TRANSCRIPT
        detected_lang = lang if lang != "auto" else "en-IN"
        try:
            logger.info(f"[VoiceQuery:{request_id}] Stage 1 – Transcribing...")
            transcript_result = await asyncio.wait_for(
                transcribe_service.transcribe_audio(
                    audio_file=audio_bytes,
                    file_extension=file_extension,
                    language_code=lang,
                    cleanup=True
                ),
                timeout=90.0   # Transcribe jobs take 25-60s on average
            )
            native_text   = transcript_result.get("transcript", "").strip() or FALLBACK_TRANSCRIPT
            detected_lang = transcript_result.get("language_code", "en-IN")
            logger.info(f"[VoiceQuery:{request_id}] Transcribed: '{native_text}' lang={detected_lang}")
        except asyncio.TimeoutError:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 1 TIMEOUT – using fallback transcript")
        except Exception as e:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 1 FAILED – {e}")

        # ── Cancellation checkpoint 1 ────────────────────────────────────────
        if _is_cancelled(ctx):
            logger.info(f"[VoiceQuery:{request_id}] Cancelled after Stage 1. Aborting.")
            return JSONResponse(content={"status": "cancelled"}, status_code=204)

        # ── Stage 2: Translate to English ─────────────────────────────────────
        english_text = native_text
        try:
            logger.info(f"[VoiceQuery:{request_id}] Stage 2 – Translating to EN...")
            english_text, _ = await translate_service.translate_text(
                text=native_text, source_lang=detected_lang, target_lang="en"
            )
        except Exception as e:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 2 FAILED – {e}")

        # ── Cancellation checkpoint 2 ────────────────────────────────────────
        if _is_cancelled(ctx):
            logger.info(f"[VoiceQuery:{request_id}] Cancelled after Stage 2. Aborting.")
            return JSONResponse(content={"status": "cancelled"}, status_code=204)

        # ── Stage 3: Bedrock AI ───────────────────────────────────────────────
        english_response = FALLBACK_RESPONSE
        try:
            logger.info(f"[VoiceQuery:{request_id}] Stage 3 – Querying Bedrock...")
            ai_response = await asyncio.wait_for(
                bedrock_service.get_response(
                    session_id=session_id,
                    user_message=english_text,
                    user_profile={},
                    eligibility_results=[]
                ),
                timeout=15.0
            )
            english_response = ai_response.get("response_text", FALLBACK_RESPONSE)
            logger.info(f"[VoiceQuery:{request_id}] Bedrock SUCCESS.")
        except asyncio.TimeoutError:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 3 TIMEOUT – using fallback response")
        except Exception as e:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 3 FAILED – {e}")

        # ── Cancellation checkpoint 3 ────────────────────────────────────────
        if _is_cancelled(ctx):
            logger.info(f"[VoiceQuery:{request_id}] Cancelled after Stage 3. Aborting.")
            return JSONResponse(content={"status": "cancelled"}, status_code=204)

        # ── Stage 4: Translate back to Native ────────────────────────────────
        native_response = english_response
        try:
            logger.info(f"[VoiceQuery:{request_id}] Stage 4 – Translating back to {detected_lang}...")
            native_response, _ = await translate_service.translate_text(
                text=english_response, source_lang="en", target_lang=detected_lang
            )
        except Exception as e:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 4 FAILED – {e}")

        # ── Stage 5: Polly TTS ────────────────────────────────────────────────
        audio_base64 = ""
        try:
            logger.info(f"[VoiceQuery:{request_id}] Stage 5 – Synthesizing via Polly...")
            audio_base64 = await polly_service.synthesize_speech(
                text=native_response, language_code=detected_lang
            )
        except Exception as e:
            logger.warning(f"[VoiceQuery:{request_id}] Stage 5 FAILED – no audio: {e}")

        logger.info(f"[VoiceQuery:{request_id}] COMPLETE for session={session_id}")
        return JSONResponse(content={
            "transcript":    native_text,
            "language":      detected_lang,
            "response_text": native_response,
            "audio_url":     audio_base64
        })

    except Exception as e:
        logger.error(f"[VoiceQuery:{request_id}] Unhandled error: {e}", exc_info=True)
        return JSONResponse(content={
            "transcript":    FALLBACK_TRANSCRIPT,
            "language":      "en-IN",
            "response_text": FALLBACK_RESPONSE,
            "audio_url":     ""
        })
    finally:
        _release_request(session_id, request_id)


