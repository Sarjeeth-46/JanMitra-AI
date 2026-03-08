import pytest
from models.scheme import EligibilityRule, Scheme


def test_eligibility_rule_creation():
    """Test creating an EligibilityRule with valid data."""
    rule = EligibilityRule(
        field="age",
        operator="greater_than_or_equal",
        value=18
    )
    
    assert rule.field == "age"
    assert rule.operator == "greater_than_or_equal"
    assert rule.value == 18


def test_eligibility_rule_with_string_value():
    """Test EligibilityRule with string value."""
    rule = EligibilityRule(
        field="occupation",
        operator="equals",
        value="farmer"
    )
    
    assert rule.field == "occupation"
    assert rule.operator == "equals"
    assert rule.value == "farmer"


def test_scheme_creation():
    """Test creating a Scheme with eligibility rules."""
    rules = [
        EligibilityRule(field="occupation", operator="equals", value="farmer"),
        EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
    ]
    
    scheme = Scheme(
        scheme_id="PM_KISAN",
        name="PM-KISAN",
        description="Income support for farmer families",
        eligibility_rules=rules
    )
    
    assert scheme.scheme_id == "PM_KISAN"
    assert scheme.name == "PM-KISAN"
    assert scheme.description == "Income support for farmer families"
    assert len(scheme.eligibility_rules) == 2
    assert scheme.eligibility_rules[0].field == "occupation"
    assert scheme.eligibility_rules[1].field == "land_size"


def test_scheme_with_empty_rules():
    """Test creating a Scheme with no eligibility rules."""
    scheme = Scheme(
        scheme_id="TEST_SCHEME",
        name="Test Scheme",
        description="A test scheme with no rules",
        eligibility_rules=[]
    )
    
    assert scheme.scheme_id == "TEST_SCHEME"
    assert len(scheme.eligibility_rules) == 0


def test_scheme_json_serialization():
    """Test that Scheme can be serialized to JSON."""
    rules = [
        EligibilityRule(field="age", operator="greater_than", value=18)
    ]
    
    scheme = Scheme(
        scheme_id="TEST",
        name="Test",
        description="Test scheme",
        eligibility_rules=rules
    )
    
    # Pydantic v2 uses model_dump() instead of dict()
    scheme_dict = scheme.model_dump()
    
    assert scheme_dict["scheme_id"] == "TEST"
    assert scheme_dict["name"] == "Test"
    assert len(scheme_dict["eligibility_rules"]) == 1
    assert scheme_dict["eligibility_rules"][0]["field"] == "age"


def test_scheme_json_deserialization():
    """Test that Scheme can be created from JSON data."""
    data = {
        "scheme_id": "AYUSHMAN_BHARAT",
        "name": "Ayushman Bharat",
        "description": "Health insurance for low-income families",
        "eligibility_rules": [
            {"field": "income", "operator": "less_than_or_equal", "value": 500000},
            {"field": "category", "operator": "equals", "value": "SC"}
        ]
    }
    
    scheme = Scheme(**data)
    
    assert scheme.scheme_id == "AYUSHMAN_BHARAT"
    assert scheme.name == "Ayushman Bharat"
    assert len(scheme.eligibility_rules) == 2
    assert scheme.eligibility_rules[0].value == 500000
    assert scheme.eligibility_rules[1].value == "SC"
