import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from services.bedrock_service import BedrockService
import asyncio

@pytest.fixture
def mock_settings():
    with patch('services.bedrock_service.Settings') as MockSettings:
        settings_instance = MockSettings.return_value
        settings_instance.aws_region = 'us-east-1'
        settings_instance.bedrock_model_id = 'test-model'
        settings_instance.chat_history_table = 'test-table'
        settings_instance.aws_access_key_id = None
        settings_instance.aws_secret_access_key = None
        yield settings_instance

@pytest.fixture
def bedrock_service(mock_settings):
    with patch('boto3.client') as mock_boto_client, patch('boto3.resource') as mock_boto_resource:
        mock_table = MagicMock()
        mock_boto_resource.return_value.Table.return_value = mock_table
        service = BedrockService()
        service.bedrock = mock_boto_client.return_value
        service.history_table = mock_table
        yield service


@pytest.mark.asyncio
async def test_bedrock_fallback_on_client_error(bedrock_service):
    """
    Test that if the Bedrock AWS client throws a ClientError (e.g., credentials expired),
    the Hackathon Demo Mode fallback string is seamlessly returned instead of crashing.
    """
    # Force the mocked bedrock client to raise a ClientError on invoke
    error_response = {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access Denied'}}
    bedrock_service.bedrock.invoke_model.side_effect = ClientError(error_response, 'InvokeModel')
    
    # Also mock history retrieval to just return empty so we isolate Bedrock
    with patch.object(bedrock_service, '_get_history', return_value=[]):
        response = await bedrock_service.get_response(
            session_id="test_123",
            user_message="Hello",
            user_profile={"name": "Test"},
            eligibility_results=[]
        )
        
        # Verify the static fallback was triggered successfully
        assert "response_text" in response
        assert "Hackathon Demo Mode" in response["response_text"]
        assert "Ayushman" in response["response_text"]

