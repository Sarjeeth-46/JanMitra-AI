import asyncio
import json
import logging
from services.bedrock_service import BedrockService

async def test_bedrock_chat():
    logging.basicConfig(level=logging.INFO)
    service = BedrockService()
    
    session_id = "test-session-123"
    user_message = "Why am I not eligible for PM-Kisan?"
    user_profile = {
        "name": "Rajesh Kumar",
        "age": 45,
        "income": 150000,
        "state": "Uttar Pradesh",
        "occupation": "Farmer",
        "category": "General",
        "land_size": 2.5
    }
    eligibility_results = [
        {
            "scheme_name": "PM-Kisan",
            "eligible": False,
            "failed_conditions": ["Land ownership exceeds 2 hectares"],
            "missing_fields": []
        }
    ]
    
    print(f"--- Sending Message: {user_message} ---")
    try:
        response = await service.get_response(
            session_id=session_id,
            user_message=user_message,
            user_profile=user_profile,
            eligibility_results=eligibility_results
        )
        print("--- Response Received ---")
        print(json.dumps(response, indent=2))
        
        # Test follow-up
        print("\n--- Sending Follow-up: What can I do? ---")
        follow_up = await service.get_response(
            session_id=session_id,
            user_message="What can I do?",
            user_profile=user_profile,
            eligibility_results=eligibility_results
        )
        print("--- Follow-up Response ---")
        print(json.dumps(follow_up, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bedrock_chat())
