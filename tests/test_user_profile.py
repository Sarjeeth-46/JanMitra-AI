import pytest
from pydantic import ValidationError
from models.user_profile import UserProfile


def test_valid_user_profile():
    """Test creating a valid UserProfile."""
    profile = UserProfile(
        name="Rajesh Kumar",
        age=35,
        income=250000.0,
        state="Maharashtra",
        occupation="farmer",
        category="OBC",
        land_size=1.5
    )
    
    assert profile.name == "Rajesh Kumar"
    assert profile.age == 35
    assert profile.income == 250000.0
    assert profile.state == "Maharashtra"
    assert profile.occupation == "farmer"
    assert profile.category == "OBC"
    assert profile.land_size == 1.5


def test_name_validation():
    """Test name field validation (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="",
            age=35,
            income=250000.0,
            state="Maharashtra",
            occupation="farmer",
            category="OBC",
            land_size=1.5
        )
    
    assert "name" in str(exc_info.value)


def test_age_validation_negative():
    """Test age field validation (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="Rajesh Kumar",
            age=-5,
            income=250000.0,
            state="Maharashtra",
            occupation="farmer",
            category="OBC",
            land_size=1.5
        )
    
    assert "age" in str(exc_info.value)


def test_age_validation_too_high():
    """Test age field validation (le=150)."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="Rajesh Kumar",
            age=200,
            income=250000.0,
            state="Maharashtra",
            occupation="farmer",
            category="OBC",
            land_size=1.5
        )
    
    assert "age" in str(exc_info.value)


def test_income_validation_negative():
    """Test income field validation (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="Rajesh Kumar",
            age=35,
            income=-1000.0,
            state="Maharashtra",
            occupation="farmer",
            category="OBC",
            land_size=1.5
        )
    
    assert "income" in str(exc_info.value)


def test_land_size_validation_negative():
    """Test land_size field validation (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="Rajesh Kumar",
            age=35,
            income=250000.0,
            state="Maharashtra",
            occupation="farmer",
            category="OBC",
            land_size=-0.5
        )
    
    assert "land_size" in str(exc_info.value)


def test_missing_required_fields():
    """Test that all fields are required."""
    with pytest.raises(ValidationError) as exc_info:
        UserProfile(
            name="Rajesh Kumar",
            age=35
        )
    
    error_str = str(exc_info.value)
    assert "income" in error_str or "field required" in error_str.lower()


def test_zero_values_allowed():
    """Test that zero is a valid value for numeric fields except where restricted."""
    profile = UserProfile(
        name="Rajesh Kumar",
        age=18, # Age must be at least 18
        income=0.0,
        state="Maharashtra",
        occupation="farmer",
        category="General",
        land_size=0.0
    )
    
    assert profile.age == 18
    assert profile.income == 0.0
    assert profile.land_size == 0.0
