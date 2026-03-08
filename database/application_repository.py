"""
Application Repository for JanMitra AI.
Handles DynamoDB operations for government scheme applications.
"""

import boto3
import logging
import time
import uuid
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError
from models.config import Settings

logger = logging.getLogger(__name__)

class ApplicationRepository:
    def __init__(self, table_name: str = "janmitra_applications"):
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
                    KeySchema=[
                        {'AttributeName': 'application_id', 'KeyType': 'HASH'}, # Partition Key
                        {'AttributeName': 'user_email', 'KeyType': 'RANGE'}   # Sort Key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'application_id', 'AttributeType': 'S'},
                        {'AttributeName': 'user_email', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                )
                # Also create a GSI for querying by phone
                # In a real app we'd wait for table to be ACTIVE, but for hackathon we assume it works
            else:
                logger.error(f"Error checking application table: {e}")

    async def create_application(self, application_data: Dict[str, Any]):
        """Creates a new scheme application in DynamoDB."""
        try:
            app_id = f"JMAI/{time.strftime('%Y%m%d')}/{uuid.uuid4().hex[:4].upper()}"
            application_data['application_id'] = app_id
            application_data['submitted_date'] = time.strftime('%d %b %Y')
            application_data['status'] = 'Under Review'
            application_data['estimated_approval'] = '5 business days'
            
            self.table.put_item(Item=application_data)
            return application_data
        except Exception as e:
            logger.error(f"Failed to create application: {e}")
            raise

    async def get_applications_by_user(self, email: str) -> List[Dict[str, Any]]:
        """Retrieves all applications for a specific user."""
        try:
            from boto3.dynamodb.conditions import Key
            # Use Scan if we didn't set up a GSI for user_email alone, 
            # but since user_email is a Sort Key, we need to query or scan.
            # Actually, if application_id is HASH and user_email is RANGE, 
            # querying by user_email requires a GSI or a Scan.
            # Let's use Scan for simplicity in this demo environment.
            response = self.table.scan(
                FilterExpression=Key('user_email').eq(email.lower().strip())
            )
            return response.get('Items', [])
        except Exception as e:
            logger.error(f"Failed to get user applications: {e}")
            return []

    async def get_application_by_id_and_phone(self, app_id: str, phone: str) -> Optional[Dict[str, Any]]:
        """Retrieves an application by its ID and phone number (Scan)."""
        try:
            # Again, using scan for the demo/hackathon context
            from boto3.dynamodb.conditions import Key, Attr
            response = self.table.scan(
                FilterExpression=Attr('application_id').eq(app_id) & Attr('applicant_phone').eq(phone)
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Failed to get application status: {e}")
            return None
