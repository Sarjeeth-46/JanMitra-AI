"""
Prompt Builder for JanMitra AI Bedrock Assistant.

Constructs detailed system and user prompts for Claude 3 Haiku,
incorporating user profile, eligibility results, and missing fields.
"""

import json
from typing import List, Dict, Any

class PromptBuilder:
    """
    Builds structured prompts for Amazon Bedrock.
    """

    SYSTEM_ROLE = (
        "You are JanMitra AI, a personal, empathetic government scheme assistant for Indian citizens. "
        "Your mission is to guide users through the complex landscape of welfare programs with clarity and warmth. "
        "Strictly follow these rules:\n"
        "1. Accuracy: Use only the provided evaluation results. Do not speculate on eligibility.\n"
        "2. Tone: Be helpful, professional, and culturally sensitive. Use 'Citizen' as a respectful default.\n"
        "3. Conversationality: Avoid being a dry data bot. Phrasings should be natural and proactive (e.g., 'I notice you mentioned... you might also be interested in...').\n"
        "4. Output: Always return a valid JSON object with the following structure:\n"
        "{\n"
        '  "response_text": "A natural, warm explanation including specific reasoning for eligibility decisions.",\n'
        '  "missing_fields": ["any", "additional", "data", "needed", "to", "confirm", "other", "schemes"],\n'
        '  "recommended_next_step": "A single, clear action for the user to take right now."\n'
        "}\n"
    )

    @staticmethod
    def build_user_context_prompt(
        user_message: str,
        user_profile: Dict[str, Any],
        eligibility_results: List[Dict[str, Any]]
    ) -> str:
        """
        Constructs the user prompt with context.
        Strips highly sensitive PII (Aadhaar, Name) before sending to LLM.
        """
        # Privacy-First AI Processing: Scrub PII
        safe_profile = user_profile.copy()
        if "aadhaar_number" in safe_profile:
            safe_profile["aadhaar_number"] = "REDACTED"
        if "name" in safe_profile and safe_profile.get("name"):
            safe_profile["name"] = "Citizen"
        if "phone" in safe_profile:
            safe_profile["phone"] = "REDACTED"
            
        context = {
            "user_profile": safe_profile,
            "eligibility_results": eligibility_results,
            "current_message": user_message
        }
        
        prompt = (
            f"Context Information:\n{json.dumps(context, indent=2)}\n\n"
            f"User Message: {user_message}\n\n"
            "Based on the context, provide a JSON response as specified in the system instructions."
        )
        return prompt

    @staticmethod
    def get_system_prompt() -> str:
        """Returns the base system role prompt."""
        return PromptBuilder.SYSTEM_ROLE
