"""
Unit tests for DynamoDB repository.

Tests the initialization and basic functionality of the DynamoDB repository class.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from database.dynamodb_repository import DynamoDBRepository


class TestDynamoDBRepositoryInit:
    """Test cases for DynamoDB repository initialization."""
    
    @patch('database.dynamodb_repository.boto3.resource')
    def test_init_with_default_table_name(self, mock_boto3_resource):
        """Test initialization with default table name."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Act
        repo = DynamoDBRepository()
        
        # Assert
        assert repo.table_name == "government_schemes"
        mock_boto3_resource.assert_called_once()
        mock_dynamodb.Table.assert_called_once_with("government_schemes")
        assert repo.table == mock_table
    
    @patch('database.dynamodb_repository.boto3.resource')
    def test_init_with_custom_table_name(self, mock_boto3_resource):
        """Test initialization with custom table name."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        custom_table = "custom_schemes_table"
        
        # Act
        repo = DynamoDBRepository(table_name=custom_table)
        
        # Assert
        assert repo.table_name == custom_table
        mock_dynamodb.Table.assert_called_once_with(custom_table)
    
    @patch('database.dynamodb_repository.boto3.resource')
    def test_init_uses_aws_region_from_env(self, mock_boto3_resource):
        """Test that initialization uses AWS_REGION from environment."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        test_region = "us-west-2"
        # Patch both Settings AND os.environ since the repo uses os.getenv('AWS_REGION', settings.aws_region)
        with patch('database.dynamodb_repository.Settings') as MockSettings, \
             patch.dict(os.environ, {'AWS_REGION': test_region}):
            settings_instance = MockSettings.return_value
            settings_instance.aws_region = test_region
            settings_instance.aws_access_key_id = None
            settings_instance.aws_secret_access_key = None
            
            # Act
            repo = DynamoDBRepository()
            
            # Assert
            mock_boto3_resource.assert_called_once_with(
                'dynamodb',
                region_name=test_region
            )
    
    @patch('database.dynamodb_repository.boto3.resource')
    def test_init_uses_default_region_when_env_not_set(self, mock_boto3_resource):
        """Test that initialization uses default region when AWS_REGION not set."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Ensure AWS_REGION is not set
        with patch.dict(os.environ, {}, clear=True):
            # Act
            repo = DynamoDBRepository()
            
            # Assert
            # Should use default region from Settings (ap-south-1)
            call_args = mock_boto3_resource.call_args
            assert call_args[1]['region_name'] == 'ap-south-1'
    
    @patch('database.dynamodb_repository.boto3.resource')
    def test_init_no_hardcoded_credentials(self, mock_boto3_resource):
        """Test that initialization passes None credentials if not fetched from SecretManager."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        with patch('database.dynamodb_repository.Settings') as MockSettings:
            settings_instance = MockSettings.return_value
            settings_instance.aws_region = 'ap-south-1'
            settings_instance.aws_access_key_id = None
            settings_instance.aws_secret_access_key = None
            
            # Act
            repo = DynamoDBRepository()
            
            # Assert
            call_args = mock_boto3_resource.call_args
            assert call_args[0][0] == 'dynamodb'
            assert 'region_name' in call_args[1]



class TestDynamoDBRepositoryGetAllSchemes:
    """Test cases for get_all_schemes method."""
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_all_schemes_returns_schemes(self, mock_boto3_resource):
        """Test that get_all_schemes returns list of Scheme objects."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response
        mock_table.scan.return_value = {
            'Items': [
                {
                    'scheme_id': 'PM_KISAN',
                    'name': 'PM-KISAN',
                    'description': 'Income support for farmer families',
                    'eligibility_rules': [
                        {
                            'field': 'occupation',
                            'operator': 'equals',
                            'value': 'farmer'
                        },
                        {
                            'field': 'land_size',
                            'operator': 'less_than_or_equal',
                            'value': 2.0
                        }
                    ]
                },
                {
                    'scheme_id': 'AYUSHMAN_BHARAT',
                    'name': 'Ayushman Bharat',
                    'description': 'Health insurance for low-income families',
                    'eligibility_rules': [
                        {
                            'field': 'income',
                            'operator': 'less_than_or_equal',
                            'value': 500000
                        }
                    ]
                }
            ]
        }
        
        repo = DynamoDBRepository()
        
        # Act
        schemes = await repo.get_all_schemes()
        
        # Assert
        assert len(schemes) == 2
        assert schemes[0].scheme_id == 'PM_KISAN'
        assert schemes[0].name == 'PM-KISAN'
        assert schemes[0].description == 'Income support for farmer families'
        assert len(schemes[0].eligibility_rules) == 2
        assert schemes[0].eligibility_rules[0].field == 'occupation'
        assert schemes[0].eligibility_rules[0].operator == 'equals'
        assert schemes[0].eligibility_rules[0].value == 'farmer'
        
        assert schemes[1].scheme_id == 'AYUSHMAN_BHARAT'
        assert len(schemes[1].eligibility_rules) == 1
        
        mock_table.scan.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_all_schemes_handles_empty_table(self, mock_boto3_resource):
        """Test that get_all_schemes handles empty table gracefully."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock empty DynamoDB response
        mock_table.scan.return_value = {
            'Items': []
        }
        
        repo = DynamoDBRepository()
        
        # Act
        schemes = await repo.get_all_schemes()
        
        # Assert
        assert schemes == []
        mock_table.scan.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_all_schemes_handles_missing_items_key(self, mock_boto3_resource):
        """Test that get_all_schemes handles response without Items key."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response without Items key
        mock_table.scan.return_value = {}
        
        repo = DynamoDBRepository()
        
        # Act
        schemes = await repo.get_all_schemes()
        
        # Assert
        assert schemes == []
        mock_table.scan.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_all_schemes_raises_client_error(self, mock_boto3_resource):
        """Test that get_all_schemes raises ClientError on DynamoDB failure."""
        # Arrange
        from botocore.exceptions import ClientError
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB error
        error_response = {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}}
        mock_table.scan.side_effect = ClientError(error_response, 'Scan')
        
        repo = DynamoDBRepository()
        
        # Act & Assert
        with pytest.raises(ClientError):
            await repo.get_all_schemes()



class TestDynamoDBRepositoryPutScheme:
    """Test cases for put_scheme method."""
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_put_scheme_stores_scheme(self, mock_boto3_resource):
        """Test that put_scheme stores a Scheme object in DynamoDB."""
        # Arrange
        from models.scheme import Scheme, EligibilityRule
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        repo = DynamoDBRepository()
        
        # Create a test scheme
        scheme = Scheme(
            scheme_id='TEST_SCHEME',
            name='Test Scheme',
            description='A test scheme for unit testing',
            eligibility_rules=[
                EligibilityRule(field='age', operator='greater_than', value=18),
                EligibilityRule(field='income', operator='less_than', value=100000)
            ]
        )
        
        # Act
        await repo.put_scheme(scheme)
        
        # Assert
        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        
        assert item['scheme_id'] == 'TEST_SCHEME'
        assert item['name'] == 'Test Scheme'
        assert item['description'] == 'A test scheme for unit testing'
        assert len(item['eligibility_rules']) == 2
        assert item['eligibility_rules'][0]['field'] == 'age'
        assert item['eligibility_rules'][0]['operator'] == 'greater_than'
        assert item['eligibility_rules'][0]['value'] == 18
        assert item['eligibility_rules'][1]['field'] == 'income'
        assert item['eligibility_rules'][1]['operator'] == 'less_than'
        assert item['eligibility_rules'][1]['value'] == 100000
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_put_scheme_with_empty_rules(self, mock_boto3_resource):
        """Test that put_scheme handles schemes with no eligibility rules."""
        # Arrange
        from models.scheme import Scheme
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        repo = DynamoDBRepository()
        
        # Create a scheme with no rules
        scheme = Scheme(
            scheme_id='EMPTY_RULES',
            name='Empty Rules Scheme',
            description='Scheme with no eligibility rules',
            eligibility_rules=[]
        )
        
        # Act
        await repo.put_scheme(scheme)
        
        # Assert
        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        
        assert item['scheme_id'] == 'EMPTY_RULES'
        assert item['eligibility_rules'] == []
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_put_scheme_raises_client_error(self, mock_boto3_resource):
        """Test that put_scheme raises ClientError on DynamoDB failure."""
        # Arrange
        from botocore.exceptions import ClientError
        from models.scheme import Scheme
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB error
        error_response = {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throughput exceeded'}}
        mock_table.put_item.side_effect = ClientError(error_response, 'PutItem')
        
        repo = DynamoDBRepository()
        
        scheme = Scheme(
            scheme_id='TEST',
            name='Test',
            description='Test',
            eligibility_rules=[]
        )
        
        # Act & Assert
        with pytest.raises(ClientError):
            await repo.put_scheme(scheme)
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_put_scheme_converts_pydantic_to_dict(self, mock_boto3_resource):
        """Test that put_scheme properly converts Pydantic models to dict format."""
        # Arrange
        from models.scheme import Scheme, EligibilityRule
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        repo = DynamoDBRepository()
        
        # Create a scheme with various value types
        scheme = Scheme(
            scheme_id='MIXED_TYPES',
            name='Mixed Types Scheme',
            description='Scheme with different value types',
            eligibility_rules=[
                EligibilityRule(field='age', operator='equals', value=25),
                EligibilityRule(field='state', operator='equals', value='Karnataka'),
                EligibilityRule(field='income', operator='less_than', value=50000.50)
            ]
        )
        
        # Act
        await repo.put_scheme(scheme)
        
        # Assert
        mock_table.put_item.assert_called_once()
        call_args = mock_table.put_item.call_args
        item = call_args[1]['Item']
        
        # Verify all rules are properly converted to dict format
        assert isinstance(item['eligibility_rules'], list)
        assert isinstance(item['eligibility_rules'][0], dict)
        assert item['eligibility_rules'][0]['value'] == 25
        assert item['eligibility_rules'][1]['value'] == 'Karnataka'
        assert item['eligibility_rules'][2]['value'] == 50000.50


class TestDynamoDBRepositoryGetSchemeById:
    """Test cases for get_scheme_by_id method."""
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_scheme_by_id_returns_scheme(self, mock_boto3_resource):
        """Test that get_scheme_by_id returns a Scheme object when found."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response
        mock_table.get_item.return_value = {
            'Item': {
                'scheme_id': 'PM_KISAN',
                'name': 'PM-KISAN',
                'description': 'Income support for farmer families',
                'eligibility_rules': [
                    {
                        'field': 'occupation',
                        'operator': 'equals',
                        'value': 'farmer'
                    },
                    {
                        'field': 'land_size',
                        'operator': 'less_than_or_equal',
                        'value': 2.0
                    }
                ]
            }
        }
        
        repo = DynamoDBRepository()
        
        # Act
        scheme = await repo.get_scheme_by_id('PM_KISAN')
        
        # Assert
        assert scheme is not None
        assert scheme.scheme_id == 'PM_KISAN'
        assert scheme.name == 'PM-KISAN'
        assert scheme.description == 'Income support for farmer families'
        assert len(scheme.eligibility_rules) == 2
        assert scheme.eligibility_rules[0].field == 'occupation'
        assert scheme.eligibility_rules[0].operator == 'equals'
        assert scheme.eligibility_rules[0].value == 'farmer'
        assert scheme.eligibility_rules[1].field == 'land_size'
        assert scheme.eligibility_rules[1].operator == 'less_than_or_equal'
        assert scheme.eligibility_rules[1].value == 2.0
        
        mock_table.get_item.assert_called_once_with(Key={'scheme_id': 'PM_KISAN'})
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_scheme_by_id_returns_none_when_not_found(self, mock_boto3_resource):
        """Test that get_scheme_by_id returns None when scheme is not found."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response with no Item
        mock_table.get_item.return_value = {}
        
        repo = DynamoDBRepository()
        
        # Act
        scheme = await repo.get_scheme_by_id('NONEXISTENT_SCHEME')
        
        # Assert
        assert scheme is None
        mock_table.get_item.assert_called_once_with(Key={'scheme_id': 'NONEXISTENT_SCHEME'})
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_scheme_by_id_with_empty_rules(self, mock_boto3_resource):
        """Test that get_scheme_by_id handles schemes with no eligibility rules."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response with empty rules
        mock_table.get_item.return_value = {
            'Item': {
                'scheme_id': 'EMPTY_RULES',
                'name': 'Empty Rules Scheme',
                'description': 'Scheme with no eligibility rules',
                'eligibility_rules': []
            }
        }
        
        repo = DynamoDBRepository()
        
        # Act
        scheme = await repo.get_scheme_by_id('EMPTY_RULES')
        
        # Assert
        assert scheme is not None
        assert scheme.scheme_id == 'EMPTY_RULES'
        assert scheme.eligibility_rules == []
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_scheme_by_id_raises_client_error(self, mock_boto3_resource):
        """Test that get_scheme_by_id raises ClientError on DynamoDB failure."""
        # Arrange
        from botocore.exceptions import ClientError
        
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB error
        error_response = {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}}
        mock_table.get_item.side_effect = ClientError(error_response, 'GetItem')
        
        repo = DynamoDBRepository()
        
        # Act & Assert
        with pytest.raises(ClientError):
            await repo.get_scheme_by_id('PM_KISAN')
    
    @pytest.mark.asyncio
    @patch('database.dynamodb_repository.boto3.resource')
    async def test_get_scheme_by_id_with_various_value_types(self, mock_boto3_resource):
        """Test that get_scheme_by_id properly handles different value types in rules."""
        # Arrange
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_boto3_resource.return_value = mock_dynamodb
        
        # Mock DynamoDB response with various value types
        mock_table.get_item.return_value = {
            'Item': {
                'scheme_id': 'MIXED_TYPES',
                'name': 'Mixed Types Scheme',
                'description': 'Scheme with different value types',
                'eligibility_rules': [
                    {'field': 'age', 'operator': 'equals', 'value': 25},
                    {'field': 'state', 'operator': 'equals', 'value': 'Karnataka'},
                    {'field': 'income', 'operator': 'less_than', 'value': 50000.50}
                ]
            }
        }
        
        repo = DynamoDBRepository()
        
        # Act
        scheme = await repo.get_scheme_by_id('MIXED_TYPES')
        
        # Assert
        assert scheme is not None
        assert len(scheme.eligibility_rules) == 3
        assert scheme.eligibility_rules[0].value == 25
        assert scheme.eligibility_rules[1].value == 'Karnataka'
        assert scheme.eligibility_rules[2].value == 50000.50

