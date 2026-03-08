import pytest
from unittest.mock import patch, MagicMock
from services.document_extraction_service import TextractService

@pytest.fixture
def mock_settings():
    with patch('services.document_extraction_service.Settings') as MockSettings:
        settings_instance = MockSettings.return_value
        settings_instance.aws_region = 'ap-south-1'
        settings_instance.aws_access_key_id = None
        settings_instance.aws_secret_access_key = None
        yield settings_instance

@pytest.fixture
def textract_service(mock_settings):
    with patch('boto3.client') as mock_boto_client:
        service = TextractService()
        service.textract = mock_boto_client.return_value
        yield service
        
def test_textract_structured_form_extraction(textract_service):
    """
    Test that the analyze_document KEY_VALUE_SET blocks accurately link
    and retrieve Name, DOB, and Aadhaar numbers.
    """
    # Mocking a simplistic Textract AnalyzeDocument 'Blocks' response
    mock_boto_response = {
        "Blocks": [
            {"BlockType": "PAGE", "Id": "page1"},
            # Keys
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "key1", 
                "EntityTypes": ["KEY"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_name_label"]},
                    {"Type": "VALUE", "Ids": ["val1"]}
                ]
            },
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "key2", 
                "EntityTypes": ["KEY"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_aadhaar_label"]},
                    {"Type": "VALUE", "Ids": ["val2"]}
                ]
            },
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "key3", 
                "EntityTypes": ["KEY"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_dob_label"]},
                    {"Type": "VALUE", "Ids": ["val3"]}
                ]
            },
            # Values
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "val1", 
                "EntityTypes": ["VALUE"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_name_val_1", "word_name_val_2"]}
                ]
            },
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "val2", 
                "EntityTypes": ["VALUE"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_aadhaar_val"]}
                ]
            },
            {
                "BlockType": "KEY_VALUE_SET", 
                "Id": "val3", 
                "EntityTypes": ["VALUE"],
                "Relationships": [
                    {"Type": "CHILD", "Ids": ["word_dob_val"]}
                ]
            },
            # Words
            {"BlockType": "WORD", "Id": "word_name_label", "Text": "Name"},
            {"BlockType": "WORD", "Id": "word_name_val_1", "Text": "Rajesh"},
            {"BlockType": "WORD", "Id": "word_name_val_2", "Text": "Kumar"},
            
            {"BlockType": "WORD", "Id": "word_aadhaar_label", "Text": "Aadhaar Number"},
            {"BlockType": "WORD", "Id": "word_aadhaar_val", "Text": "1234 5678 9012"},
            
            {"BlockType": "WORD", "Id": "word_dob_label", "Text": "DOB"},
            {"BlockType": "WORD", "Id": "word_dob_val", "Text": "01/01/1985"}
        ]
    }
    
    textract_service.textract.analyze_document.return_value = mock_boto_response
    
    result = textract_service.extract_document_data(b"fake_bytes")
    
    fields = result.get("extracted_fields", {})
    assert fields.get("name") == "Rajesh Kumar"
    assert fields.get("aadhaar_number") == "1234 5678 9012"
    
    import datetime
    expected_age = datetime.datetime.now().year - 1985
    assert fields.get("age") == expected_age
    
    # Assert KVS captured
    forms = result.get("structured_forms", {})
    assert "name" in forms
    assert "aadhaar number" in forms
