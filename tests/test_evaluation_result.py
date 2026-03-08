import pytest
from models.evaluation_result import EvaluationResult


def test_evaluation_result_creation():
    """Test creating an EvaluationResult with all fields."""
    result = EvaluationResult(
        scheme_name="PM-KISAN",
        eligible=True,
        missing_fields=[],
        failed_conditions=[]
    )
    
    assert result.scheme_name == "PM-KISAN"
    assert result.eligible is True
    assert result.missing_fields == []
    assert result.failed_conditions == []


def test_evaluation_result_with_missing_fields():
    """Test EvaluationResult with missing fields populated."""
    result = EvaluationResult(
        scheme_name="Ayushman Bharat",
        eligible=False,
        missing_fields=["income", "category"],
        failed_conditions=[]
    )
    
    assert result.scheme_name == "Ayushman Bharat"
    assert result.eligible is False
    assert len(result.missing_fields) == 2
    assert "income" in result.missing_fields
    assert "category" in result.missing_fields


def test_evaluation_result_with_failed_conditions():
    """Test EvaluationResult with failed conditions populated."""
    result = EvaluationResult(
        scheme_name="MGNREGA",
        eligible=False,
        missing_fields=[],
        failed_conditions=["income must be <= 300000", "state must not be in [Delhi, Mumbai]"]
    )
    
    assert result.scheme_name == "MGNREGA"
    assert result.eligible is False
    assert len(result.failed_conditions) == 2
    assert "income must be <= 300000" in result.failed_conditions


def test_evaluation_result_default_values():
    """Test that missing_fields and failed_conditions default to empty lists."""
    result = EvaluationResult(
        scheme_name="Stand Up India",
        eligible=True
    )
    
    assert result.missing_fields == []
    assert result.failed_conditions == []


def test_evaluation_result_json_serialization():
    """Test that EvaluationResult can be serialized to JSON."""
    result = EvaluationResult(
        scheme_name="Sukanya Samriddhi Yojana",
        eligible=False,
        missing_fields=["age"],
        failed_conditions=["age must be <= 10"]
    )
    
    json_data = result.model_dump()
    
    assert json_data["scheme_name"] == "Sukanya Samriddhi Yojana"
    assert json_data["eligible"] is False
    assert json_data["missing_fields"] == ["age"]
    assert json_data["failed_conditions"] == ["age must be <= 10"]


def test_evaluation_result_json_deserialization():
    """Test that EvaluationResult can be created from JSON."""
    json_data = {
        "scheme_name": "PM-KISAN",
        "eligible": True,
        "missing_fields": [],
        "failed_conditions": []
    }
    
    result = EvaluationResult(**json_data)
    
    assert result.scheme_name == "PM-KISAN"
    assert result.eligible is True
    assert result.missing_fields == []
    assert result.failed_conditions == []
