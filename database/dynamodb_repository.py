"""
DynamoDB repository for managing government schemes.

This module provides a repository class for interacting with AWS DynamoDB
to store and retrieve government scheme data. It uses boto3 for AWS SDK
operations and supports IAM role-based authentication.
"""

import os
import boto3
import logging
from typing import List, Optional
from botocore.exceptions import ClientError

from models.scheme import Scheme, EligibilityRule
from models.config import Settings

logger = logging.getLogger(__name__)


class DynamoDBRepository:
    """
    Repository class for DynamoDB operations on government schemes.
    
    This class manages the connection to DynamoDB and provides methods
    for CRUD operations on scheme data. It uses IAM role-based authentication
    when running on EC2, or environment variables for local development.
    
    Attributes:
        table_name: Name of the DynamoDB table (default: 'government_schemes')
        dynamodb: boto3 DynamoDB resource
        table: DynamoDB table object
    """
    
    def __init__(self, table_name: str = "government_schemes"):
        """
        Initialize DynamoDB client using boto3.
        
        This method sets up the DynamoDB connection using boto3. It reads
        AWS credentials from environment variables (AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY) if available, or uses IAM role-based
        authentication when running on EC2.
        
        Args:
            table_name: Name of the DynamoDB table to use
        
        Environment Variables:
            AWS_REGION: AWS region (default: ap-south-1)
            AWS_ACCESS_KEY_ID: AWS access key (optional, for local dev)
            AWS_SECRET_ACCESS_KEY: AWS secret key (optional, for local dev)
        """
        # Load settings from environment
        settings = Settings()
        
        # Get AWS region from environment or use default
        aws_region = os.getenv('AWS_REGION', settings.aws_region)
        
        logger.info(
            "Initializing DynamoDB repository",
            extra={
                "event": "dynamodb_init",
                "table_name": table_name,
                "aws_region": aws_region
            }
        )
        
        # Initialize boto3 DynamoDB resource
        # If AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are set in environment,
        # boto3 will use them automatically. Otherwise, it will use IAM role
        # credentials when running on EC2.
        client_kwargs = {
            "region_name": aws_region
        }
        if getattr(settings, "aws_access_key_id", None) and getattr(settings, "aws_secret_access_key", None):
            client_kwargs["aws_access_key_id"] = settings.aws_access_key_id
            client_kwargs["aws_secret_access_key"] = settings.aws_secret_access_key

        self.dynamodb = boto3.resource(
            'dynamodb',
            **client_kwargs
        )
        
        # Get reference to the table
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        
        logger.info(
            "DynamoDB repository initialized successfully",
            extra={
                "event": "dynamodb_init_success",
                "table_name": table_name
            }
        )
    
    async def get_all_schemes(self) -> List[Scheme]:
        """
        Retrieve all schemes from DynamoDB.
        
        Performs a scan operation to fetch all schemes from the table.
        Converts DynamoDB items to Scheme objects.
        
        Returns:
            List of Scheme objects
        
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.info(
                "Scanning DynamoDB for all schemes",
                extra={
                    "event": "dynamodb_scan_started",
                    "table_name": self.table_name
                }
            )
            
            # Perform scan operation to get all items
            response = self.table.scan()
            
            # Get items from response
            items = response.get('Items', [])
            
            # Handle empty table gracefully
            if not items:
                logger.warning(
                    "No schemes found in DynamoDB",
                    extra={
                        "event": "dynamodb_scan_empty",
                        "table_name": self.table_name
                    }
                )
                return []
            
            # Parse items into Scheme objects
            schemes = []
            for item in items:
                # Convert eligibility_rules from DynamoDB format to EligibilityRule objects
                eligibility_rules = [
                    EligibilityRule(**rule) for rule in item.get('eligibility_rules', [])
                ]
                
                # Create Scheme object
                scheme = Scheme(
                    scheme_id=item['scheme_id'],
                    name=item['name'],
                    description=item['description'],
                    eligibility_rules=eligibility_rules
                )
                schemes.append(scheme)
            
            logger.info(
                "Successfully retrieved schemes from DynamoDB",
                extra={
                    "event": "dynamodb_scan_success",
                    "table_name": self.table_name,
                    "scheme_count": len(schemes)
                }
            )
            
            return schemes
            
        except ClientError as e:
            logger.error(
                "DynamoDB scan operation failed",
                extra={
                    "event": "dynamodb_scan_error",
                    "table_name": self.table_name,
                    "error_code": e.response['Error']['Code'],
                    "error_message": e.response['Error']['Message']
                },
                exc_info=True
            )
            # Re-raise DynamoDB errors for caller to handle
            raise
    
    async def get_scheme_by_id(self, scheme_id: str) -> Optional[Scheme]:
        """
        Retrieve a single scheme by ID.
        
        Args:
            scheme_id: Unique identifier for the scheme
        
        Returns:
            Scheme object if found, None otherwise
        
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.info(
                "Retrieving scheme by ID from DynamoDB",
                extra={
                    "event": "dynamodb_get_item_started",
                    "table_name": self.table_name,
                    "scheme_id": scheme_id
                }
            )
            
            # Perform get_item operation using partition key
            response = self.table.get_item(
                Key={'scheme_id': scheme_id}
            )
            
            # Check if item was found
            item = response.get('Item')
            if not item:
                logger.warning(
                    "Scheme not found in DynamoDB",
                    extra={
                        "event": "dynamodb_get_item_not_found",
                        "table_name": self.table_name,
                        "scheme_id": scheme_id
                    }
                )
                return None
            
            # Convert eligibility_rules from DynamoDB format to EligibilityRule objects
            eligibility_rules = [
                EligibilityRule(**rule) for rule in item.get('eligibility_rules', [])
            ]
            
            # Create and return Scheme object
            scheme = Scheme(
                scheme_id=item['scheme_id'],
                name=item['name'],
                description=item['description'],
                eligibility_rules=eligibility_rules
            )
            
            logger.info(
                "Successfully retrieved scheme from DynamoDB",
                extra={
                    "event": "dynamodb_get_item_success",
                    "table_name": self.table_name,
                    "scheme_id": scheme_id,
                    "scheme_name": scheme.name
                }
            )
            
            return scheme
            
        except ClientError as e:
            logger.error(
                "DynamoDB get_item operation failed",
                extra={
                    "event": "dynamodb_get_item_error",
                    "table_name": self.table_name,
                    "scheme_id": scheme_id,
                    "error_code": e.response['Error']['Code'],
                    "error_message": e.response['Error']['Message']
                },
                exc_info=True
            )
            # Re-raise DynamoDB errors for caller to handle
            raise
    
    async def put_scheme(self, scheme: Scheme) -> None:
        """
        Store or update a scheme in DynamoDB.
        
        Converts the Scheme object to DynamoDB item format and stores it.
        If a scheme with the same scheme_id exists, it will be overwritten.
        
        Args:
            scheme: Scheme object to store
        
        Raises:
            ClientError: If DynamoDB operation fails
        """
        try:
            logger.info(
                "Storing scheme in DynamoDB",
                extra={
                    "event": "dynamodb_put_item_started",
                    "table_name": self.table_name,
                    "scheme_id": scheme.scheme_id,
                    "scheme_name": scheme.name
                }
            )
            
            # Convert Scheme to DynamoDB item format
            item = {
                'scheme_id': scheme.scheme_id,
                'name': scheme.name,
                'description': scheme.description,
                'eligibility_rules': [
                    rule.model_dump() for rule in scheme.eligibility_rules
                ]
            }
            
            # Store item in DynamoDB
            self.table.put_item(Item=item)
            
            logger.info(
                "Successfully stored scheme in DynamoDB",
                extra={
                    "event": "dynamodb_put_item_success",
                    "table_name": self.table_name,
                    "scheme_id": scheme.scheme_id,
                    "scheme_name": scheme.name,
                    "rule_count": len(scheme.eligibility_rules)
                }
            )
            
        except ClientError as e:
            logger.error(
                "DynamoDB put_item operation failed",
                extra={
                    "event": "dynamodb_put_item_error",
                    "table_name": self.table_name,
                    "scheme_id": scheme.scheme_id,
                    "scheme_name": scheme.name,
                    "error_code": e.response['Error']['Code'],
                    "error_message": e.response['Error']['Message']
                },
                exc_info=True
            )
            # Re-raise DynamoDB errors for caller to handle
            raise
