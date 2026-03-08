"""
OTP Repository for JanMitra AI.
Handles DynamoDB operations for OTP sessions with TTL.
"""

import boto3
import logging
import time
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from models.config import Settings

logger = logging.getLogger(__name__)

class OTPSessionRepository:
    def __init__(self, table_name: str = "otp_sessions"):
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
        
        # Ensure table exists
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        try:
            self.table.table_status
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info(f"Creating DynamoDB table: {self.table_name}")
                self.dynamodb.create_table(
                    TableName=self.table_name,
                    KeySchema=[{'AttributeName': 'mobile', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[{'AttributeName': 'mobile', 'AttributeType': 'S'}],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )
                # Note: TTL must be enabled via separate call or AWS console normally, 
                # but for this script we assume it's handled or we'll hint it.
            else:
                logger.error(f"Error checking OTP table: {e}")

    async def save_otp(self, mobile: str, otp: str, expires_in_mins: int = 5):
        """Saves an OTP for a mobile number with a TTL."""
        try:
            now = int(time.time())
            expires_at = now + (expires_in_mins * 60)
            
            item = {
                'mobile': mobile,
                'otp': otp,
                'created_at': now,
                'expires_at': expires_at,
                'attempts': 0
            }
            
            self.table.put_item(Item=item)
            return item
        except Exception as e:
            logger.error(f"Failed to save OTP: {e}")
            raise

    async def verify_otp(self, mobile: str, otp: str) -> bool:
        """Verifies an OTP and increments attempt count."""
        try:
            response = self.table.get_item(Key={'mobile': mobile})
            item = response.get('Item')
            
            if not item:
                return False
                
            # Check expiry
            if int(time.time()) > item.get('expires_at', 0):
                await self.delete_otp(mobile)
                return False
                
            # Check attempts
            if item.get('attempts', 0) >= 3:
                await self.delete_otp(mobile)
                return False
                
            if item.get('otp') == otp:
                await self.delete_otp(mobile)
                return True
            else:
                # Increment attempts
                self.table.update_item(
                    Key={'mobile': mobile},
                    UpdateExpression="set attempts = attempts + :inc",
                    ExpressionAttributeValues={':inc': 1}
                )
                return False
        except Exception as e:
            logger.error(f"Failed to verify OTP: {e}")
            return False

    async def delete_otp(self, mobile: str):
        """Deletes an OTP session."""
        try:
            self.table.delete_item(Key={'mobile': mobile})
        except Exception as e:
            logger.error(f"Failed to delete OTP: {e}")
