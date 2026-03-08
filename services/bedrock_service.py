"""
Bedrock Service – JanMitra AI
==============================

3-Tier Model Cascade (hackathon demo-safe):
  1. Claude 3 Haiku  (primary  – best quality)
  2. Meta Llama 3 8B (fallback – if Haiku unavailable/billing fails)
  3. Static demo response (final safety net – demo NEVER crashes)

Chat history stored in DynamoDB; silently ignored if unavailable (memoryless mode).
"""

import boto3
import json
import logging
import time
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from models.config import Settings
from services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

# ─── Model IDs ────────────────────────────────────────────────────────────────
MODEL_CLAUDE_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
MODEL_LLAMA3       = "meta.llama3-8b-instruct-v1:0"

# ─── Static Demo Fallback ─────────────────────────────────────────────────────
DEMO_FALLBACK_RESPONSE = {
    "response_text": (
        "Based on your profile, here are the top government schemes you may be eligible for:\n\n"
        "🌾 PM Kisan Samman Nidhi – ₹6,000/year direct benefit for farmers\n"
        "🏥 Ayushman Bharat (PM-JAY) – Free health coverage up to ₹5 lakh/year\n"
        "🏠 PM Awas Yojana (PMAY) – Housing subsidy for affordable homes\n"
        "📚 National Scholarship Portal – Education support for students\n"
        "👩‍🌾 PM Fasal Bima Yojana – Crop insurance for agricultural protection\n\n"
        "Click 'Start Eligibility Check' to get a detailed, personalised evaluation."
    ),
    "missing_fields": [],
    "recommended_next_step": "Would you like to start the detailed eligibility check?",
    "suggested_schemes": [
        {"name": "PM Kisan Samman Nidhi", "benefit": "₹6,000/year",          "category": "Agriculture"},
        {"name": "Ayushman Bharat",        "benefit": "₹5 lakh health cover", "category": "Health"},
        {"name": "PM Awas Yojana",         "benefit": "Housing subsidy",      "category": "Housing"},
    ]
}


# ─── Request Body Builders ────────────────────────────────────────────────────

def _build_claude_body(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """
    Builds the Anthropic Claude Messages API body for Amazon Bedrock.
    https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html
    """
    return json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    })


def _extract_claude_text(response_body: dict) -> str:
    """Extracts the assistant text from Claude Messages API response."""
    content = response_body.get("content", [])
    if content and isinstance(content, list):
        return content[0].get("text", "").strip()
    return ""


def _build_llama_body(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """
    Builds the request body for Meta Llama 3 on Amazon Bedrock.
    Uses <|begin_of_text|> ... instruction format.
    """
    prompt = (
        "<|begin_of_text|>"
        "<|start_header_id|>system<|end_header_id|>\n"
        f"{system_prompt}<|eot_id|>"
        "<|start_header_id|>user<|end_header_id|>\n"
        f"{user_message}<|eot_id|>"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )
    return json.dumps({
        "prompt": prompt,
        "max_gen_len": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
    })


def _extract_llama_text(response_body: dict) -> str:
    """Extracts assistant text from Meta Llama 3 response body."""
    return response_body.get("generation", "").strip()


def _parse_ai_response(raw_text: str) -> Dict[str, Any]:
    """
    Tries to parse structured JSON from the model's raw text output.
    Falls back to a plain-text wrapper if the response isn't JSON.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:].rstrip("`").strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:].rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "response_text": raw_text,
            "missing_fields": [],
            "recommended_next_step": "Is there anything else I can help you with?"
        }


# ─── Main Service ─────────────────────────────────────────────────────────────

class BedrockService:
    """
    Interacts with Amazon Bedrock using a 3-tier cascade:
      Claude 3 Haiku → Llama 3 8B → Static fallback
    """

    def __init__(self):
        self.settings = Settings()
        client_kwargs = {"region_name": self.settings.aws_region}
        if getattr(self.settings, "aws_access_key_id", None) and getattr(self.settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = self.settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = self.settings.aws_secret_access_key

        self.bedrock = boto3.client(service_name="bedrock-runtime", **client_kwargs)
        self.dynamodb = boto3.resource("dynamodb", **client_kwargs)
        self.history_table = self.dynamodb.Table(self.settings.chat_history_table)

        logger.info(
            "[Bedrock] Service initialized. Cascade: %s → %s → demo fallback",
            MODEL_CLAUDE_HAIKU, MODEL_LLAMA3
        )

    # ─── DynamoDB History ──────────────────────────────────────────────────────

    def _get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Returns last 5 messages from DynamoDB; silently returns [] on failure."""
        try:
            from boto3.dynamodb.conditions import Key
            resp = self.history_table.query(
                KeyConditionExpression=Key("session_id").eq(session_id),
                ScanIndexForward=False,
                Limit=1
            )
            items = resp.get("Items", [])
            return items[0].get("messages", [])[-5:] if items else []
        except Exception as e:
            logger.warning("[Bedrock] DynamoDB unavailable – memoryless mode: %s", e)
            return []

    def _save_history(self, session_id: str, new_messages: List[Dict[str, str]]):
        """Appends messages to DynamoDB history; silently skips on failure."""
        try:
            current = self._get_history(session_id)
            self.history_table.put_item(Item={
                "session_id": session_id,
                "timestamp": str(time.time()),
                "messages": (current + new_messages)[-10:]
            })
        except Exception as e:
            logger.warning("[Bedrock] DynamoDB save skipped: %s", e)

    # ─── Model Invocations ─────────────────────────────────────────────────────

    def _invoke_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke Claude 3 Haiku and return raw text. Raises on any error."""
        body = _build_claude_body(system_prompt, user_prompt)
        logger.info("[Bedrock] Trying Claude 3 Haiku (%s)...", MODEL_CLAUDE_HAIKU)
        response = self.bedrock.invoke_model(
            modelId=MODEL_CLAUDE_HAIKU,
            contentType="application/json",
            accept="application/json",
            body=body
        )
        resp_body = json.loads(response["body"].read())
        text = _extract_claude_text(resp_body)
        if not text:
            raise ValueError("Empty response from Claude")
        logger.info("[Bedrock] Claude Haiku SUCCESS (%d chars)", len(text))
        return text

    def _invoke_llama(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke Meta Llama 3 8B and return raw text. Raises on any error."""
        body = _build_llama_body(system_prompt, user_prompt)
        logger.info("[Bedrock] Trying Llama 3 8B (%s)...", MODEL_LLAMA3)
        response = self.bedrock.invoke_model(
            modelId=MODEL_LLAMA3,
            contentType="application/json",
            accept="application/json",
            body=body
        )
        resp_body = json.loads(response["body"].read())
        text = _extract_llama_text(resp_body)
        if not text:
            raise ValueError("Empty response from Llama 3")
        logger.info("[Bedrock] Llama 3 SUCCESS (%d chars)", len(text))
        return text

    # ─── Public Interface ──────────────────────────────────────────────────────

    async def get_response(
        self,
        session_id: str,
        user_message: str,
        user_profile: Dict[str, Any],
        eligibility_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        3-tier cascade:
          1. Claude 3 Haiku
          2. Llama 3 8B (if Haiku fails)
          3. DEMO_FALLBACK_RESPONSE (if both fail)

        Always returns a dict — never raises.
        """
        system_prompt = PromptBuilder.get_system_prompt()
        user_prompt   = PromptBuilder.build_user_context_prompt(
            user_message, user_profile, eligibility_results
        )

        raw_text: str | None = None

        # ── Tier 1: Claude 3 Haiku ────────────────────────────────────────────
        try:
            raw_text = self._invoke_claude(system_prompt, user_prompt)
        except ClientError as e:
            ec = e.response.get("Error", {}).get("Code", "Unknown")
            logger.warning("[Bedrock] Claude FAILED (%s) – trying Llama 3", ec)
        except Exception as e:
            logger.warning("[Bedrock] Claude FAILED (%s) – trying Llama 3", e)

        # ── Tier 2: Llama 3 8B ───────────────────────────────────────────────
        if raw_text is None:
            try:
                raw_text = self._invoke_llama(system_prompt, user_prompt)
            except ClientError as e:
                ec = e.response.get("Error", {}).get("Code", "Unknown")
                logger.error("[Bedrock] Llama 3 FAILED (%s) – using demo fallback", ec)
            except Exception as e:
                logger.error("[Bedrock] Llama 3 FAILED (%s) – using demo fallback", e)

        # ── Tier 3: Static Demo Fallback ─────────────────────────────────────
        if raw_text is None:
            logger.info("[Bedrock] Both models failed – returning DEMO_FALLBACK_RESPONSE")
            return DEMO_FALLBACK_RESPONSE

        # Parse and save history
        result = _parse_ai_response(raw_text)
        self._save_history(session_id, [
            {"role": "user",      "content": user_message},
            {"role": "assistant", "content": raw_text}
        ])
        return result

    # ─── Streaming (for chat endpoint) ────────────────────────────────────────

    def _invoke_stream_claude(self, body: str):
        return self.bedrock.invoke_model_with_response_stream(
            modelId=MODEL_CLAUDE_HAIKU,
            contentType="application/json",
            accept="application/json",
            body=body
        )

    def _invoke_stream_llama(self, body: str):
        return self.bedrock.invoke_model_with_response_stream(
            modelId=MODEL_LLAMA3,
            contentType="application/json",
            accept="application/json",
            body=body
        )

    async def stream_chat(self, user_message: str, history: List[Dict[str, str]]):
        """
        Streams a chat response token-by-token.
        Cascade: Claude → Llama → static fallback text.
        """
        from fastapi.concurrency import run_in_threadpool

        system_prompt = (
            "You are JanMitra AI, a helpful government scheme eligibility assistant for Indian citizens. "
            "Provide clear, concise, empathetic answers in plain text."
        )

        full_response = ""

        # ── Try Claude streaming ──────────────────────────────────────────────
        try:
            body = _build_claude_body(system_prompt, user_message, max_tokens=800)
            logger.info("[Bedrock Stream] Starting Claude streaming...")
            response = await run_in_threadpool(self._invoke_stream_claude, body)
            async for event in _iter_stream(response):
                # Claude streaming: delta.text
                chunk_body = json.loads(event.get("bytes", b"{}").decode("utf-8"))
                delta = chunk_body.get("delta", {})
                text  = delta.get("text", "")
                if text:
                    full_response += text
                    yield text
            logger.info("[Bedrock Stream] Claude SUCCESS (%d chars)", len(full_response))
            return
        except Exception as e:
            logger.warning("[Bedrock Stream] Claude FAILED – trying Llama: %s", e)
            full_response = ""

        # ── Try Llama streaming ───────────────────────────────────────────────
        try:
            body = _build_llama_body(system_prompt, user_message, max_tokens=800)
            logger.info("[Bedrock Stream] Starting Llama streaming...")
            response = await run_in_threadpool(self._invoke_stream_llama, body)
            async for event in _iter_stream(response):
                chunk_body = json.loads(event.get("bytes", b"{}").decode("utf-8"))
                text = chunk_body.get("generation", "")
                if text:
                    full_response += text
                    yield text
            logger.info("[Bedrock Stream] Llama SUCCESS (%d chars)", len(full_response))
            return
        except Exception as e:
            logger.error("[Bedrock Stream] Llama FAILED – returning fallback: %s", e)

        # ── Static fallback ───────────────────────────────────────────────────
        yield DEMO_FALLBACK_RESPONSE["response_text"]


async def _iter_stream(response):
    """Async-friendly iterator over a Bedrock streaming response body."""
    stream = response.get("body")
    for event in stream:
        chunk = event.get("chunk")
        if chunk:
            yield chunk
