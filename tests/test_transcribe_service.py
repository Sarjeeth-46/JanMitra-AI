import pytest
from unittest.mock import patch
from services.transcribe_service import TranscribeService

@pytest.fixture
def mock_settings():
    with patch('services.transcribe_service.Settings') as MockSettings:
        settings_instance = MockSettings.return_value
        settings_instance.aws_region = 'ap-south-1'
        settings_instance.aws_access_key_id = None
        settings_instance.aws_secret_access_key = None
        settings_instance.s3_audio_bucket = "test-bucket"
        yield settings_instance

@pytest.fixture
def transcribe_service(mock_settings):
    with patch('boto3.client') as mock_boto_client:
        service = TranscribeService()
        service.s3_client = mock_boto_client.return_value
        service.transcribe_client = mock_boto_client.return_value
        yield service
        
@pytest.mark.asyncio
async def test_s3_upload_optimization_headers(transcribe_service):
    """
    Asserts Phase 4 optimization headers (ContentType="audio/wav", CacheControl="no-cache")
    are correctly appended to skip AWS Transcribe media sniffing penalty latency.
    """
    with patch('services.transcribe_service.run_in_threadpool') as mock_run:
        # Mock threadpool simply executing the target sync function (won't actually call network)
        mock_run.return_value = None
        
        file_key = await transcribe_service.upload_audio_to_s3(b"fake_audio_bytes", ".wav")
        
        # Verify the underlying call signature inside the threadpool wrapper
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        
        # Extract the kwargs passed to the underlying s3_client.put_object
        assert kwargs["Bucket"] == "janmitra-audio-files"
        assert kwargs["ContentType"] == "audio/wav"
        assert kwargs["CacheControl"] == "no-cache"
        assert kwargs["Key"].startswith("audio/")
        assert kwargs["Key"].endswith(".wav")
