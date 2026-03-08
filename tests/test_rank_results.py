"""
Unit tests for the rank_results function in eligibility_service.py

Tests verify that results are sorted with eligible=True schemes first,
then alphabetically by scheme_name within each group.
"""

import pytest
from models.evaluation_result import EvaluationResult
from services.eligibility_service import rank_results


def test_rank_results_eligible_first():
    """Test that eligible schemes appear before ineligible schemes."""
    results = [
        EvaluationResult(
            scheme_name="Scheme B",
            eligible=False,
            missing_fields=[],
            failed_conditions=["age < 18"]
        ),
        EvaluationResult(
            scheme_name="Scheme A",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Scheme C",
            eligible=False,
            missing_fields=["income"],
            failed_conditions=[]
        ),
    ]
    
    ranked = rank_results(results)
    
    # First result should be eligible
    assert ranked[0].eligible is True
    assert ranked[0].scheme_name == "Scheme A"
    
    # Next two should be ineligible
    assert ranked[1].eligible is False
    assert ranked[2].eligible is False


def test_rank_results_alphabetical_within_eligible():
    """Test that eligible schemes are sorted alphabetically."""
    results = [
        EvaluationResult(
            scheme_name="Zebra Scheme",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Alpha Scheme",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Beta Scheme",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
    ]
    
    ranked = rank_results(results)
    
    assert ranked[0].scheme_name == "Alpha Scheme"
    assert ranked[1].scheme_name == "Beta Scheme"
    assert ranked[2].scheme_name == "Zebra Scheme"


def test_rank_results_alphabetical_within_ineligible():
    """Test that ineligible schemes are sorted alphabetically."""
    results = [
        EvaluationResult(
            scheme_name="Zebra Scheme",
            eligible=False,
            missing_fields=[],
            failed_conditions=["age < 18"]
        ),
        EvaluationResult(
            scheme_name="Alpha Scheme",
            eligible=False,
            missing_fields=["income"],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Beta Scheme",
            eligible=False,
            missing_fields=[],
            failed_conditions=["state != 'Karnataka'"]
        ),
    ]
    
    ranked = rank_results(results)
    
    assert ranked[0].scheme_name == "Alpha Scheme"
    assert ranked[1].scheme_name == "Beta Scheme"
    assert ranked[2].scheme_name == "Zebra Scheme"


def test_rank_results_mixed_eligible_and_ineligible():
    """Test complete ranking with mixed eligible and ineligible schemes."""
    results = [
        EvaluationResult(
            scheme_name="Ineligible Z",
            eligible=False,
            missing_fields=[],
            failed_conditions=["age < 18"]
        ),
        EvaluationResult(
            scheme_name="Eligible B",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Ineligible A",
            eligible=False,
            missing_fields=["income"],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Eligible A",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        ),
        EvaluationResult(
            scheme_name="Ineligible M",
            eligible=False,
            missing_fields=[],
            failed_conditions=["state != 'Karnataka'"]
        ),
    ]
    
    ranked = rank_results(results)
    
    # First two should be eligible, sorted alphabetically
    assert ranked[0].eligible is True
    assert ranked[0].scheme_name == "Eligible A"
    assert ranked[1].eligible is True
    assert ranked[1].scheme_name == "Eligible B"
    
    # Last three should be ineligible, sorted alphabetically
    assert ranked[2].eligible is False
    assert ranked[2].scheme_name == "Ineligible A"
    assert ranked[3].eligible is False
    assert ranked[3].scheme_name == "Ineligible M"
    assert ranked[4].eligible is False
    assert ranked[4].scheme_name == "Ineligible Z"


def test_rank_results_empty_list():
    """Test that empty list returns empty list."""
    results = []
    ranked = rank_results(results)
    assert ranked == []


def test_rank_results_single_item():
    """Test that single item list returns unchanged."""
    results = [
        EvaluationResult(
            scheme_name="Only Scheme",
            eligible=True,
            missing_fields=[],
            failed_conditions=[]
        )
    ]
    ranked = rank_results(results)
    assert len(ranked) == 1
    assert ranked[0].scheme_name == "Only Scheme"


def test_rank_results_all_eligible():
    """Test ranking when all schemes are eligible."""
    results = [
        EvaluationResult(scheme_name="C", eligible=True, missing_fields=[], failed_conditions=[]),
        EvaluationResult(scheme_name="A", eligible=True, missing_fields=[], failed_conditions=[]),
        EvaluationResult(scheme_name="B", eligible=True, missing_fields=[], failed_conditions=[]),
    ]
    
    ranked = rank_results(results)
    
    assert ranked[0].scheme_name == "A"
    assert ranked[1].scheme_name == "B"
    assert ranked[2].scheme_name == "C"


def test_rank_results_all_ineligible():
    """Test ranking when all schemes are ineligible."""
    results = [
        EvaluationResult(scheme_name="C", eligible=False, missing_fields=[], failed_conditions=["test"]),
        EvaluationResult(scheme_name="A", eligible=False, missing_fields=[], failed_conditions=["test"]),
        EvaluationResult(scheme_name="B", eligible=False, missing_fields=[], failed_conditions=["test"]),
    ]
    
    ranked = rank_results(results)
    
    assert ranked[0].scheme_name == "A"
    assert ranked[1].scheme_name == "B"
    assert ranked[2].scheme_name == "C"
