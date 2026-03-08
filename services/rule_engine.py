"""
Rule Engine for JanMitra AI Phase 1 Backend

This module implements the core rule evaluation logic for determining
government scheme eligibility. It provides deterministic, operator-based
comparison functions without any LLM involvement.
"""

from typing import Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def apply_operator(operator: str, profile_value: Any, rule_value: Any) -> bool:
    """
    Apply comparison operator to values.
    
    Supports the following operators:
    - equals: profile_value == rule_value
    - not_equals: profile_value != rule_value
    - less_than: profile_value < rule_value
    - less_than_or_equal: profile_value <= rule_value
    - greater_than: profile_value > rule_value
    - greater_than_or_equal: profile_value >= rule_value
    
    Args:
        operator: The comparison operator to apply
        profile_value: The value from the user profile
        rule_value: The value from the eligibility rule
    
    Returns:
        Boolean result of the comparison
    
    Raises:
        ValueError: If the operator is not supported
    
    Requirements: 1.4, 3.3
    """
    if operator == "equals":
        return profile_value == rule_value
    elif operator == "not_equals":
        return profile_value != rule_value
    elif operator == "less_than":
        return profile_value < rule_value
    elif operator == "less_than_or_equal":
        return profile_value <= rule_value
    elif operator == "greater_than":
        return profile_value > rule_value
    elif operator == "greater_than_or_equal":
        return profile_value >= rule_value
    else:
        raise ValueError(f"Unsupported operator: {operator}")


def evaluate_rule(rule: 'EligibilityRule', user_profile: 'UserProfile') -> Tuple[bool, Optional[str]]:
    """
    Evaluate a single rule against user profile.
    
    Compares the specified field from the user profile against the rule's value
    using the rule's operator. Handles missing fields by returning an appropriate
    failure message.
    
    Args:
        rule: The eligibility rule to evaluate
        user_profile: The user profile to evaluate against
    
    Returns:
        A tuple of (passed, failed_condition_message) where:
        - passed: True if the rule passes, False otherwise
        - failed_condition_message: None if passed, otherwise a description of why it failed
    
    Requirements: 3.3, 3.6, 3.7
    """
    from models.scheme import EligibilityRule
    from models.user_profile import UserProfile
    
    # Check if the field exists in the user profile
    if not hasattr(user_profile, rule.field):
        return False, f"Missing field: {rule.field}"
    
    # Get the profile value
    profile_value = getattr(user_profile, rule.field)
    
    # Check if the value is None (missing)
    if profile_value is None:
        return False, f"Missing field: {rule.field}"
    
    # Apply the operator
    try:
        passed = apply_operator(rule.operator, profile_value, rule.value)
        
        if passed:
            return True, None
        else:
            # Create a descriptive failed condition message
            return False, f"{rule.field} {rule.operator} {rule.value} (actual: {profile_value})"
    
    except Exception as e:
        # Handle any comparison errors
        return False, f"Error evaluating {rule.field} {rule.operator} {rule.value}: {str(e)}"


def evaluate_scheme(scheme: 'Scheme', user_profile: 'UserProfile') -> 'EvaluationResult':
    """
    Evaluate all rules for a single scheme.
    
    Processes all eligibility rules for a scheme against the user profile.
    Tracks missing fields and failed conditions. Determines eligibility based
    on whether all rules pass.
    
    Args:
        scheme: The government scheme to evaluate
        user_profile: The user profile to evaluate against
    
    Returns:
        EvaluationResult object with:
        - scheme_name: Name of the scheme
        - eligible: True if all rules pass, False otherwise
        - missing_fields: Array of field names that are missing from the profile
        - failed_conditions: Array of rule descriptions that failed
    
    Requirements: 3.1, 3.4, 3.5, 3.6, 3.7
    """
    from models.scheme import Scheme
    from models.user_profile import UserProfile
    from models.evaluation_result import EvaluationResult
    
    missing_fields = []
    failed_conditions = []
    
    # Evaluate each rule in the scheme
    for rule in scheme.eligibility_rules:
        passed, failed_message = evaluate_rule(rule, user_profile)
        
        if not passed:
            # Check if it's a missing field or a failed condition
            if failed_message and failed_message.startswith("Missing field:"):
                # Extract the field name from the message
                field_name = failed_message.replace("Missing field: ", "")
                if field_name not in missing_fields:
                    missing_fields.append(field_name)
                    logger.warning(
                        "Missing field detected during rule evaluation",
                        extra={
                            "event": "rule_evaluation_missing_field",
                            "scheme_id": scheme.scheme_id,
                            "scheme_name": scheme.name,
                            "field_name": field_name
                        }
                    )
            else:
                # It's a failed condition
                if failed_message and failed_message not in failed_conditions:
                    failed_conditions.append(failed_message)
                    logger.info(
                        "Rule condition failed",
                        extra={
                            "event": "rule_evaluation_failed",
                            "scheme_id": scheme.scheme_id,
                            "scheme_name": scheme.name,
                            "failed_condition": failed_message
                        }
                    )
    
    # Determine eligibility: true only if all rules pass (no missing fields and no failed conditions)
    eligible = len(missing_fields) == 0 and len(failed_conditions) == 0
    
    return EvaluationResult(
        scheme_name=scheme.name,
        eligible=eligible,
        missing_fields=missing_fields,
        failed_conditions=failed_conditions,
        scheme_id=scheme.scheme_id,
        scheme_description=getattr(scheme, 'description', None),
    )
