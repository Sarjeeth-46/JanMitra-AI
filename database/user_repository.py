"""
User Repository for JanMitra AI.
Handles DynamoDB operations for user accounts.
"""

import boto3
import logging
import time
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from models.config import Settings

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, table_name: str = "janmitra_users"):
        settings = Settings()
        client_kwargs = {
            "region_name": settings.aws_region
        }
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.dynamodb = boto3.resource('dynamodb', **client_kwargs)
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        
        # Ensure table exists (optional for hackathon demo, but good practice)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        try:
            self.table.table_status
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table: {self.table_name}")
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'}],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )
            else:
                logger.error(f"Error checking user table: {e}")

    async def create_user(self, user_data: Dict[str, Any]):
        """Creates a new user in DynamoDB."""
        try:
            user_data['created_at'] = str(time.time())
            if 'language' not in user_data:
                user_data['language'] = 'en'
            
            self.table.put_item(Item=user_data)
            return user_data
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by email."""
        try:
            response = self.table.get_item(Key={'email': email.lower().strip()})
            return response.get('Item')
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user by phone number using a scan (demo mode)."""
        try:
            # In a real app, we'd use a GSI. For demo, we scan.
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('phone').eq(phone.strip())
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Failed to get user by phone: {e}")
            return None

    async def update_user_language(self, email: str, language: str):
        """Updates user's preferred language."""
        try:
            self.table.update_item(
                Key={'email': email.lower().strip()},
                UpdateExpression="set #lang = :l",
                ExpressionAttributeNames={'#lang': 'language'},
                ExpressionAttributeValues={':l': language}
            )
        except Exception as e:
            logger.error(f"Failed to update language: {e}")
