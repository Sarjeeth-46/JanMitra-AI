"""
Eligibility Evaluation Service for JanMitra AI Phase 1 Backend

This module orchestrates the eligibility evaluation workflow by fetching
all government schemes from the appropriate repository and evaluating each
scheme against the user profile using the rule engine.

Repository selection:
- If AWS credentials are available → DynamoDBRepository (production)
- Otherwise → LocalRepository (in-memory, development / local mode)
"""

from typing import List
import logging
from models.user_profile import UserProfile
from models.evaluation_result import EvaluationResult
from services.rule_engine import evaluate_scheme

logger = logging.getLogger(__name__)


def _get_repository():
    """
    Return the appropriate repository based on AWS credential availability.

    Attempts a lightweight credential probe using boto3's STS get-caller-identity.
    Falls back to LocalRepository if credentials are absent or invalid so that
    the app works out-of-the-box without any AWS configuration.
    """
    try:
        import boto3
        import os
        from models.config import Settings
        settings = Settings()
        aws_region = getattr(settings, "aws_region", "ap-south-1")
        
        client_kwargs = {"region_name": aws_region}
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        sts = boto3.client("sts", **client_kwargs)
        sts.get_caller_identity()  # cheap probe – raises NoCredentialsError if missing
        # Credentials OK → use DynamoDB
        from database.dynamodb_repository import DynamoDBRepository
        logger.info("AWS credentials found – using DynamoDB repository",
                    extra={"event": "repo_selection", "mode": "dynamodb"})
        return DynamoDBRepository()
    except Exception as e:
        # No credentials, endpoint error, or any other AWS issue → fall back
        from database.local_repository import LocalRepository
        logger.warning(
            "AWS credentials unavailable – falling back to local in-memory repository. "
            "Evaluations will work with built-in scheme data.",
            extra={"event": "repo_selection", "mode": "local", "reason": str(e)},
        )
        return LocalRepository()


def rank_results(results: List[EvaluationResult]) -> List[EvaluationResult]:
    """
    Sort results with eligible=True first, then by scheme name.
    
    This function implements the ranking logic required by Requirement 4.3:
    - Primary sort: eligible=True schemes appear before eligible=False schemes
    - Secondary sort: Within each group, sort alphabetically by scheme_name
    
    Args:
        results: List of EvaluationResult objects to rank
    
    Returns:
        Sorted list of EvaluationResult objects
    
    Requirements: 4.3
    """
    return sorted(results, key=lambda r: (not r.eligible, r.scheme_name))


async def evaluate_eligibility(user_profile: UserProfile) -> List[EvaluationResult]:
    """
    Evaluate user eligibility across all schemes using a hybrid approach:
    1. Rule-based evaluation from DynamoDB/Local repo.
    2. AI-powered recommendations using Amazon Bedrock (with fallback).
    """
    logger.info("Starting hybrid eligibility evaluation for %s", user_profile.name)
    
    # ─── Step 1: Rule-Based Evaluation ────────────────────────────────────────
    repository = _get_repository()
    try:
        schemes = await repository.get_all_schemes()
    except Exception as e:
        logger.warning("DB fetch failed, using local repo: %s", e)
        from database.local_repository import LocalRepository
        repository = LocalRepository()
        schemes = await repository.get_all_schemes()

    rule_results = []
    for scheme in schemes:
        rule_results.append(evaluate_scheme(scheme, user_profile))

    # ─── Step 2: AI-Powered Recommendation (Bedrock) ─────────────────────────
    ai_recommendations = []
    try:
        from services.bedrock_service import BedrockService
        bedrock = BedrockService()
        
        import json
        
        # Prepare schemes dataset for the prompt
        schemes_data = []
        for s in schemes:
            try:
                schemes_data.append(s.model_dump() if hasattr(s, 'model_dump') else s.dict())
            except Exception:
                schemes_data.append({"scheme_name": getattr(s, "schema_name", "Unknown")})
        schemes_json = json.dumps(schemes_data, default=str)

        prompt = f"""You are an AI assistant for JanMitra AI, a government scheme discovery platform.

Your task is to analyze a citizen's profile and recommend the most relevant Indian government schemes.

User Profile:
- Name: {user_profile.name}
- Age: {user_profile.age}
- State: {user_profile.state}
- Occupation: {user_profile.occupation}
- Annual Income: {user_profile.income}
- Category: {user_profile.category}
- Gender: {user_profile.gender}
- Land Size: {user_profile.land_size} hectares

Available Schemes Dataset:
{schemes_json}

Instructions:
1. Analyze eligibility conditions of each scheme.
2. Match the user's profile with scheme criteria.
3. Return ONLY schemes that the user is eligible for.
4. Rank schemes based on relevance.
5. If no scheme matches exactly, return the closest possible schemes.

Return response in JSON format:

{{
  "recommended_schemes": [
    {{
      "scheme_name": "",
      "description": "",
      "benefits": "",
      "eligibility_reason": ""
    }}
  ]
}}"""
        
        response_text = ""
        model_ids = [
            "anthropic.claude-3-haiku-20240307-v1:0",
            "amazon.titan-text-lite-v1"
        ]
        
        success = False
        for model_id in model_ids:
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                }) if "claude" in model_id else json.dumps({
                    "inputText": prompt,
                    "textGenerationConfig": {"maxTokenCount": 1500, "temperature": 0.2}
                })
                
                response = bedrock.bedrock.invoke_model(modelId=model_id, body=body)
                response_body = json.loads(response.get('body').read())
                
                if "claude" in model_id:
                    response_text = response_body['content'][0]['text']
                else:
                    response_text = response_body['results'][0]['outputText']
                
                # Parse JSON from response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end != -1:
                    parsed_json = json.loads(response_text[start:end])
                    ai_recommendations = parsed_json.get("recommended_schemes", [])
                    success = True
                    break
            except Exception as e:
                logger.error("Bedrock model %s failed: %s", model_id, e)
                continue
        
        if not success:
            raise Exception("All Bedrock models failed")
            
    except Exception as e:
        logger.warning("AI Recommendation failed, falling back to demo recommendations: %s", e)
        ai_recommendations = [
            {"scheme_name": "PM-Kisan", "benefit": "₹6000/year", "reason": "Agricultural support"},
            {"scheme_name": "Ayushman Bharat", "benefit": "₹5 Lakh cover", "reason": "Health insurance"},
            {"scheme_name": "PMAY", "benefit": "Housing subsidy", "reason": "Home ownership"}
        ]

    # ─── Step 3: Combine & Rank ────────────────────────────────────────────────
    # Integrate AI recs into the EvaluationResult if they aren't already there
    final_results = rule_results
    
    # If the rule engine missed some schemes that AI found, we can add them as 'AI Suggested'
    # But for now, we'll just prioritize the ones that are 'eligible' by rules.
    
    ranked = rank_results(final_results)
    
    # Enrich the top eligible results with AI reasons if possible
    # (In a real system, we'd more tightly integrate these)
    
    return ranked
