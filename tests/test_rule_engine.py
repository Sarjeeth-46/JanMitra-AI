"""
Unit tests for rule engine operator evaluation
"""

import pytest
from services.rule_engine import apply_operator


class TestApplyOperator:
    """Test cases for the apply_operator function"""
    
    def test_equals_operator_with_matching_values(self):
        """Test equals operator returns True when values match"""
        assert apply_operator("equals", 25, 25) is True
        assert apply_operator("equals", "farmer", "farmer") is True
        assert apply_operator("equals", 2.5, 2.5) is True
    
    def test_equals_operator_with_different_values(self):
        """Test equals operator returns False when values differ"""
        assert apply_operator("equals", 25, 30) is False
        assert apply_operator("equals", "farmer", "teacher") is False
    
    def test_not_equals_operator(self):
        """Test not_equals operator"""
        assert apply_operator("not_equals", 25, 30) is True
        assert apply_operator("not_equals", 25, 25) is False
        assert apply_operator("not_equals", "farmer", "teacher") is True
    
    def test_less_than_operator(self):
        """Test less_than operator"""
        assert apply_operator("less_than", 20, 30) is True
        assert apply_operator("less_than", 30, 20) is False
        assert apply_operator("less_than", 25, 25) is False
        assert apply_operator("less_than", 1.5, 2.0) is True
    
    def test_less_than_or_equal_operator(self):
        """Test less_than_or_equal operator"""
        assert apply_operator("less_than_or_equal", 20, 30) is True
        assert apply_operator("less_than_or_equal", 25, 25) is True
        assert apply_operator("less_than_or_equal", 30, 20) is False
        assert apply_operator("less_than_or_equal", 2.0, 2.0) is True
    
    def test_greater_than_operator(self):
        """Test greater_than operator"""
        assert apply_operator("greater_than", 30, 20) is True
        assert apply_operator("greater_than", 20, 30) is False
        assert apply_operator("greater_than", 25, 25) is False
        assert apply_operator("greater_than", 2.5, 1.5) is True
    
    def test_greater_than_or_equal_operator(self):
        """Test greater_than_or_equal operator"""
        assert apply_operator("greater_than_or_equal", 30, 20) is True
        assert apply_operator("greater_than_or_equal", 25, 25) is True
        assert apply_operator("greater_than_or_equal", 20, 30) is False
        assert apply_operator("greater_than_or_equal", 2.0, 2.0) is True
    
    def test_unsupported_operator_raises_error(self):
        """Test that unsupported operators raise ValueError"""
        with pytest.raises(ValueError, match="Unsupported operator"):
            apply_operator("invalid_operator", 25, 30)
    
    def test_operators_with_zero_values(self):
        """Test operators handle zero values correctly"""
        assert apply_operator("equals", 0, 0) is True
        assert apply_operator("greater_than", 1, 0) is True
        assert apply_operator("less_than", 0, 1) is True
        assert apply_operator("less_than_or_equal", 0, 0) is True
    
    def test_operators_with_mixed_numeric_types(self):
        """Test operators work with both int and float"""
        assert apply_operator("equals", 2, 2.0) is True
        assert apply_operator("less_than", 2, 2.5) is True
        assert apply_operator("greater_than", 3.0, 2) is True



class TestEvaluateRule:
    """Test cases for the evaluate_rule function"""
    
    def test_rule_passes_with_matching_values(self):
        """Test that a rule passes when profile value matches rule value"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        rule = EligibilityRule(field="occupation", operator="equals", value="farmer")
        passed, message = evaluate_rule(rule, profile)
        
        assert passed is True
        assert message is None
    
    def test_rule_fails_with_non_matching_values(self):
        """Test that a rule fails when profile value doesn't match rule value"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="teacher",
            category="General",
            land_size=1.5
        )
        
        rule = EligibilityRule(field="occupation", operator="equals", value="farmer")
        passed, message = evaluate_rule(rule, profile)
        
        assert passed is False
        assert message is not None
        assert "occupation" in message
        assert "farmer" in message
    
    def test_rule_handles_missing_field(self):
        """Test that a rule correctly identifies missing fields"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        # Test with a field that doesn't exist in UserProfile
        rule = EligibilityRule(field="nonexistent_field", operator="equals", value="test")
        passed, message = evaluate_rule(rule, profile)
        
        assert passed is False
        assert message is not None
        assert "Missing field" in message
        assert "nonexistent_field" in message
    
    def test_rule_with_numeric_comparison(self):
        """Test that numeric comparison operators work correctly"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        # Test less_than_or_equal
        rule = EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
        passed, message = evaluate_rule(rule, profile)
        assert passed is True
        assert message is None
        
        # Test greater_than
        rule = EligibilityRule(field="age", operator="greater_than", value=25)
        passed, message = evaluate_rule(rule, profile)
        assert passed is True
        assert message is None
        
        # Test less_than (should fail)
        rule = EligibilityRule(field="income", operator="less_than", value=100000)
        passed, message = evaluate_rule(rule, profile)
        assert passed is False
        assert "income" in message
    
    def test_rule_with_zero_values(self):
        """Test that rules handle zero values correctly (not as missing)"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=0,  # Zero income
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=0  # Zero land size
        )
        
        # Zero should be treated as a valid value, not missing
        rule = EligibilityRule(field="income", operator="equals", value=0)
        passed, message = evaluate_rule(rule, profile)
        assert passed is True
        assert message is None
        
        rule = EligibilityRule(field="land_size", operator="greater_than_or_equal", value=0)
        passed, message = evaluate_rule(rule, profile)
        assert passed is True
        assert message is None
    
    def test_failed_condition_message_format(self):
        """Test that failed condition messages include relevant details"""
        from services.rule_engine import evaluate_rule
        from models.scheme import EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=600000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        rule = EligibilityRule(field="income", operator="less_than", value=500000)
        passed, message = evaluate_rule(rule, profile)
        
        assert passed is False
        assert message is not None
        # Message should contain field name, operator, expected value, and actual value
        assert "income" in message
        assert "less_than" in message
        assert "500000" in message
        assert "600000" in message



class TestEvaluateScheme:
    """Test cases for the evaluate_scheme function"""
    
    def test_scheme_eligible_when_all_rules_pass(self):
        """Test that a scheme is eligible when all rules pass"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="PM_KISAN",
            name="PM-KISAN",
            description="Income support for farmer families",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "PM-KISAN"
        assert result.eligible is True
        assert len(result.missing_fields) == 0
        assert len(result.failed_conditions) == 0
    
    def test_scheme_not_eligible_when_rule_fails(self):
        """Test that a scheme is not eligible when a rule fails"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="teacher",  # Not a farmer
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="PM_KISAN",
            name="PM-KISAN",
            description="Income support for farmer families",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "PM-KISAN"
        assert result.eligible is False
        assert len(result.missing_fields) == 0
        assert len(result.failed_conditions) == 1
        assert "occupation" in result.failed_conditions[0]
    
    def test_scheme_tracks_missing_fields(self):
        """Test that missing fields are tracked correctly"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="TEST_SCHEME",
            name="Test Scheme",
            description="Test scheme with missing field",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="nonexistent_field", operator="equals", value="test")
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "Test Scheme"
        assert result.eligible is False
        assert len(result.missing_fields) == 1
        assert "nonexistent_field" in result.missing_fields
        assert len(result.failed_conditions) == 0
    
    def test_scheme_tracks_multiple_failed_conditions(self):
        """Test that multiple failed conditions are tracked"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=600000,  # Too high
            state="Karnataka",
            occupation="teacher",  # Wrong occupation
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="TEST_SCHEME",
            name="Test Scheme",
            description="Test scheme with multiple failures",
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="income", operator="less_than", value=500000)
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "Test Scheme"
        assert result.eligible is False
        assert len(result.missing_fields) == 0
        assert len(result.failed_conditions) == 2
    
    def test_scheme_with_empty_rules_is_eligible(self):
        """Test that a scheme with no rules is eligible for all profiles"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="UNIVERSAL_SCHEME",
            name="Universal Scheme",
            description="Scheme with no eligibility rules",
            eligibility_rules=[]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "Universal Scheme"
        assert result.eligible is True
        assert len(result.missing_fields) == 0
        assert len(result.failed_conditions) == 0
    
    def test_scheme_with_complex_rules(self):
        """Test scheme evaluation with multiple complex rules"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="Jane Smith",
            age=25,
            income=300000,
            state="Maharashtra",
            occupation="farmer",
            category="SC",
            land_size=1.8
        )
        
        scheme = Scheme(
            scheme_id="COMPLEX_SCHEME",
            name="Complex Scheme",
            description="Scheme with multiple eligibility criteria",
            eligibility_rules=[
                EligibilityRule(field="age", operator="greater_than_or_equal", value=18),
                EligibilityRule(field="age", operator="less_than_or_equal", value=65),
                EligibilityRule(field="income", operator="less_than_or_equal", value=500000),
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0)
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "Complex Scheme"
        assert result.eligible is True
        assert len(result.missing_fields) == 0
        assert len(result.failed_conditions) == 0
    
    def test_scheme_does_not_duplicate_missing_fields(self):
        """Test that missing fields are not duplicated in the array"""
        from services.rule_engine import evaluate_scheme
        from models.scheme import Scheme, EligibilityRule
        from models.user_profile import UserProfile
        
        profile = UserProfile(
            name="John Doe",
            age=30,
            income=200000,
            state="Karnataka",
            occupation="farmer",
            category="General",
            land_size=1.5
        )
        
        scheme = Scheme(
            scheme_id="TEST_SCHEME",
            name="Test Scheme",
            description="Test scheme with duplicate missing field references",
            eligibility_rules=[
                EligibilityRule(field="missing_field", operator="equals", value="value1"),
                EligibilityRule(field="missing_field", operator="not_equals", value="value2")
            ]
        )
        
        result = evaluate_scheme(scheme, profile)
        
        assert result.scheme_name == "Test Scheme"
        assert result.eligible is False
        assert len(result.missing_fields) == 1
        assert "missing_field" in result.missing_fields
