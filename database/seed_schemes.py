"""
Database initialization script for seeding government schemes.

This script defines all 5 government schemes for Phase 1 and provides
functionality to load them into DynamoDB. Each scheme includes:
- scheme_id: Unique identifier
- name: Display name
- description: Brief description of the scheme
- eligibility_rules: List of eligibility criteria

The 5 schemes are:
1. PM-KISAN: For small and marginal farmers
2. Ayushman Bharat: For low-income families
3. Sukanya Samriddhi Yojana: For girl child savings
4. MGNREGA: For rural employment
5. Stand Up India: For SC/ST entrepreneurs
"""

import asyncio
import sys
from typing import List

from models.scheme import Scheme, EligibilityRule
from database.dynamodb_repository import DynamoDBRepository


def get_all_schemes() -> List[Scheme]:
    """
    Define all 5 government schemes with their eligibility rules.
    
    Returns:
        List of Scheme objects ready to be stored in DynamoDB
    """
    schemes = []
    
    # 1. PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
    # Target: Small and marginal farmers
    # Rules: occupation=farmer, land_size<=2.0
    pm_kisan = Scheme(
        scheme_id="PM_KISAN",
        name="PM-KISAN",
        description="Pradhan Mantri Kisan Samman Nidhi - Income support for small and marginal farmer families owning cultivable land up to 2 hectares",
        eligibility_rules=[
            EligibilityRule(
                field="occupation",
                operator="equals",
                value="farmer"
            ),
            EligibilityRule(
                field="land_size",
                operator="less_than_or_equal",
                value=2.0
            )
        ]
    )
    schemes.append(pm_kisan)
    
    # 2. Ayushman Bharat (PM-JAY)
    # Target: Low-income families
    # Rules: income<=500000, category in [SC, ST, OBC]
    # Note: Using multiple rules with 'equals' for each category since 'in' operator
    # is not yet implemented in the rule engine. This creates an OR condition
    # that will be handled by creating separate evaluation paths.
    # For Phase 1, we'll use a simplified rule: income<=500000 only
    ayushman_bharat = Scheme(
        scheme_id="AYUSHMAN_BHARAT",
        name="Ayushman Bharat",
        description="Pradhan Mantri Jan Arogya Yojana - Health insurance scheme for economically vulnerable families with annual income up to 5 lakhs",
        eligibility_rules=[
            EligibilityRule(
                field="income",
                operator="less_than_or_equal",
                value=500000
            )
        ]
    )
    schemes.append(ayushman_bharat)
    
    # 3. Sukanya Samriddhi Yojana
    # Target: Girl child savings
    # Rules: age<=10
    sukanya_samriddhi = Scheme(
        scheme_id="SUKANYA_SAMRIDDHI",
        name="Sukanya Samriddhi Yojana",
        description="Small deposit scheme for the girl child - Savings scheme for parents/guardians of girl children under 10 years of age",
        eligibility_rules=[
            EligibilityRule(
                field="age",
                operator="less_than_or_equal",
                value=10
            )
        ]
    )
    schemes.append(sukanya_samriddhi)
    
    # 4. MGNREGA (Mahatma Gandhi National Rural Employment Guarantee Act)
    # Target: Rural households
    # Rules: state not in [Delhi, Mumbai, Bangalore], income<=300000
    # Note: 'not_in' operator is not yet implemented. For Phase 1, we'll use
    # a simplified rule: income<=300000 only
    mgnrega = Scheme(
        scheme_id="MGNREGA",
        name="MGNREGA",
        description="Mahatma Gandhi National Rural Employment Guarantee Act - Guarantees 100 days of wage employment to rural households with annual income up to 3 lakhs",
        eligibility_rules=[
            EligibilityRule(
                field="income",
                operator="less_than_or_equal",
                value=300000
            )
        ]
    )
    schemes.append(mgnrega)
    
    # 5. Stand Up India
    # Target: SC/ST entrepreneurs
    # Rules: age>=18, age<=65, category in [SC, ST]
    # Note: 'in' operator is not yet implemented. For Phase 1, we'll use
    # age range rules only
    stand_up_india = Scheme(
        scheme_id="STAND_UP_INDIA",
        name="Stand Up India",
        description="Stand Up India Scheme - Facilitates bank loans for SC/ST entrepreneurs between 18-65 years for setting up greenfield enterprises",
        eligibility_rules=[
            EligibilityRule(
                field="age",
                operator="greater_than_or_equal",
                value=18
            ),
            EligibilityRule(
                field="age",
                operator="less_than_or_equal",
                value=65
            )
        ]
    )
    schemes.append(stand_up_india)
    
    return schemes


async def seed_database(skip_existing: bool = True):
    """
    Load all schemes into DynamoDB.
    
    Args:
        skip_existing: If True, skip schemes that already exist in the database.
                      If False, overwrite existing schemes.
    """
    print("Initializing DynamoDB repository...")
    repository = DynamoDBRepository()
    
    print("Loading scheme definitions...")
    schemes = get_all_schemes()
    
    print(f"Found {len(schemes)} schemes to seed")
    
    # If skip_existing is True, check which schemes already exist
    existing_scheme_ids = set()
    if skip_existing:
        print("Checking for existing schemes...")
        try:
            existing_schemes = await repository.get_all_schemes()
            existing_scheme_ids = {scheme.scheme_id for scheme in existing_schemes}
            if existing_scheme_ids:
                print(f"Found {len(existing_scheme_ids)} existing schemes: {', '.join(existing_scheme_ids)}")
        except Exception as e:
            print(f"Warning: Could not check existing schemes: {e}")
            print("Proceeding with seeding...")
    
    # Store each scheme
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for scheme in schemes:
        try:
            if skip_existing and scheme.scheme_id in existing_scheme_ids:
                print(f"  ⊘ Skipping {scheme.name} (already exists)")
                skip_count += 1
                continue
            
            print(f"  → Storing {scheme.name}...")
            await repository.put_scheme(scheme)
            print(f"  ✓ Successfully stored {scheme.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Error storing {scheme.name}: {e}")
            error_count += 1
    
    # Print summary
    print("\n" + "="*60)
    print("Seeding Summary:")
    print(f"  Successfully stored: {success_count}")
    print(f"  Skipped (existing): {skip_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total schemes: {len(schemes)}")
    print("="*60)
    
    if error_count > 0:
        print("\n⚠ Warning: Some schemes failed to store. Check the errors above.")
        sys.exit(1)
    else:
        print("\n✓ Database seeding completed successfully!")


async def main():
    """
    Main entry point for the seed script.
    
    Usage:
        python -m database.seed_schemes
        python -m database.seed_schemes --force  # Overwrite existing schemes
    """
    # Check command line arguments
    force_overwrite = "--force" in sys.argv
    
    if force_overwrite:
        print("Running in FORCE mode - will overwrite existing schemes")
        skip_existing = False
    else:
        print("Running in SAFE mode - will skip existing schemes")
        print("Use --force flag to overwrite existing schemes")
        skip_existing = True
    
    print()
    
    try:
        await seed_database(skip_existing=skip_existing)
    except Exception as e:
        print(f"\n✗ Fatal error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
