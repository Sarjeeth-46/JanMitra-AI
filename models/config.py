import os
import json
import boto3
import logging
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables and AWS Secrets."""
    
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-south-1"
    environment: str = "development"
    app_env: str = "development"
    
    dynamodb_table_name: str = "government_schemes"
    chat_history_table: str = "janmitra_chat_history"
    s3_audio_bucket: str = "janmitra-audio-files"
    bedrock_model_id: str = "meta.llama3-8b-instruct-v1:0"
    api_port: int = 8000
    
    jwt_secret: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets_manager()

    def _load_secrets_manager(self):
        """
        Attempt to load production secrets (JWT, AWS keys) from AWS Secrets Manager.
        Falls back to .env values if Secrets Manager is unreachable or secret is missing.
        """
        # Use Secrets Manager only in production when APP_ENV=production
        if self.app_env != "production" or not self.aws_access_key_id:
            logger.info(f"Skipping Secrets Manager in {self.app_env} environment")
            return
            
        try:
            client = boto3.client(
                "secretsmanager",
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            
            response = client.get_secret_value(SecretId="janmitra-ai-secrets")
            if "SecretString" in response:
                secrets = json.loads(response["SecretString"])
                
                # Override Pydantic defaults with securely fetched secrets
                if "JWT_SECRET" in secrets:
                    self.jwt_secret = secrets["JWT_SECRET"]
                if "AWS_ACCESS_KEY_ID" in secrets:
                    self.aws_access_key_id = secrets["AWS_ACCESS_KEY_ID"]
                if "AWS_SECRET_ACCESS_KEY" in secrets:
                    self.aws_secret_access_key = secrets["AWS_SECRET_ACCESS_KEY"]
                    
                logger.info("Successfully loaded secure configuration from AWS Secrets Manager")
                
        except ClientError as e:
            # Expected during local development without Secrets Manager access
            logger.warning(f"Could not load from Secrets Manager, falling back to local .env: {str(e)}")
        except Exception as e:
            logger.warning(f"Unexpected error loading Secrets Manager: {str(e)}")
