"""
System Health Check Endpoint

Returns the live status of every AWS service used by JanMitra AI.
Designed for the frontend GET /api/system-health call.
"""

import logging
import boto3
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system-health"])


def _check_service(name: str, fn) -> str:
    """Run a quick probe function and return 'connected' or 'unavailable'."""
    try:
        fn()
        return "connected"
    except (ClientError, NoCredentialsError):
        logger.warning(f"AWS service probe failed: {name}")
        return "unavailable"
    except Exception as e:
        logger.warning(f"Service probe error ({name}): {e}")
        return "unavailable"


@router.get("/system-health")
async def system_health():
    """
    Deep health check – probes every AWS service used by JanMitra AI.

    Response shape:
    {
        "api": "running",
        "s3": "connected" | "unavailable",
        "textract": "active" | "unavailable",
        "bedrock": "active" | "unavailable",
        "transcribe": "active" | "unavailable",
        "translate": "active" | "unavailable",
        "polly": "active" | "unavailable",
        "dynamodb": "connected" | "unavailable"
    }
    """
    from models.config import Settings
    settings = Settings()
    region = settings.aws_region

    # --- S3 ---
    def probe_s3():
        boto3.client("s3", region_name=region).list_buckets()

    # --- Textract ---
    def probe_textract():
        boto3.client("textract", region_name=region) \
             .detect_document_text(Document={"Bytes": b"\x89PNG"})  # will fail but proves auth

    # --- Transcribe ---
    def probe_transcribe():
        boto3.client("transcribe", region_name=region).list_transcription_jobs(MaxResults=1)

    # --- Translate ---
    def probe_translate():
        boto3.client("translate", region_name=region) \
             .translate_text(Text="hi", SourceLanguageCode="en", TargetLanguageCode="hi")

    # --- Polly ---
    def probe_polly():
        boto3.client("polly", region_name=region).describe_voices(LanguageCode="hi-IN")

    # --- Bedrock ---
    def probe_bedrock():
        boto3.client("bedrock", region_name=region).list_foundation_models()

    # --- DynamoDB ---
    def probe_dynamodb():
        boto3.client("dynamodb", region_name=region).list_tables(Limit=1)

    s3_status      = _check_service("S3", probe_s3)
    textract_status = _check_service("Textract", probe_textract)
    transcribe_status = _check_service("Transcribe", probe_transcribe)
    translate_status = _check_service("Translate", probe_translate)
    polly_status   = _check_service("Polly", probe_polly)
    bedrock_status = _check_service("Bedrock", probe_bedrock)
    dynamodb_status = _check_service("DynamoDB", probe_dynamodb)

    # Remap "connected" → "active" for AI services for clarity
    for svc_name in ("textract", "transcribe", "translate", "polly", "bedrock"):
        pass  # labels already set below

    health_data = {
        "api": "running",
        "s3": s3_status,
        "textract": "active" if textract_status == "connected" else "unavailable",
        "transcribe": "active" if transcribe_status == "connected" else "unavailable",
        "translate": "active" if translate_status == "connected" else "unavailable",
        "polly": "active" if polly_status == "connected" else "unavailable",
        "bedrock": "active" if bedrock_status == "connected" else "unavailable",
        "dynamodb": dynamodb_status,
    }

    logger.info("System health check completed", extra={"event": "system_health", **health_data})
    return JSONResponse(content=health_data)
