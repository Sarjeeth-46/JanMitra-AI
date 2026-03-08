"""
Local In-Memory Repository for JanMitra AI

Provides a drop-in replacement for DynamoDBRepository that serves
the 5 government schemes from memory. Activated automatically when
AWS credentials are not available (development / local mode).
"""

import logging
from typing import List, Optional

from models.scheme import Scheme, EligibilityRule

logger = logging.getLogger(__name__)


def _build_local_schemes() -> List[Scheme]:
    """Return the canonical list of 5 government schemes (mirrors seed_schemes.py)."""
    return [
        Scheme(
            scheme_id="PM_KISAN",
            name="PM-KISAN",
            description=(
                "Pradhan Mantri Kisan Samman Nidhi – Income support of ₹6,000/year "
                "for small and marginal farmer families owning cultivable land up to 2 hectares."
            ),
            eligibility_rules=[
                EligibilityRule(field="occupation", operator="equals", value="farmer"),
                EligibilityRule(field="land_size", operator="less_than_or_equal", value=2.0),
            ],
        ),
        Scheme(
            scheme_id="AYUSHMAN_BHARAT",
            name="Ayushman Bharat",
            description=(
                "Pradhan Mantri Jan Arogya Yojana – Health insurance of ₹5 lakh/year "
                "for economically vulnerable families with annual income up to ₹5 lakh."
            ),
            eligibility_rules=[
                EligibilityRule(field="income", operator="less_than_or_equal", value=500000),
            ],
        ),
        Scheme(
            scheme_id="SUKANYA_SAMRIDDHI",
            name="Sukanya Samriddhi Yojana",
            description=(
                "Small deposit savings scheme for parents/guardians of girl children "
                "under 10 years of age."
            ),
            eligibility_rules=[
                EligibilityRule(field="age", operator="less_than_or_equal", value=10),
            ],
        ),
        Scheme(
            scheme_id="MGNREGA",
            name="MGNREGA",
            description=(
                "Mahatma Gandhi National Rural Employment Guarantee Act – Guarantees "
                "100 days of wage employment to rural households with annual income up to ₹3 lakh."
            ),
            eligibility_rules=[
                EligibilityRule(field="income", operator="less_than_or_equal", value=300000),
            ],
        ),
        Scheme(
            scheme_id="STAND_UP_INDIA",
            name="Stand Up India",
            description=(
                "Facilitates bank loans for SC/ST entrepreneurs between 18–65 years "
                "for setting up greenfield enterprises."
            ),
            eligibility_rules=[
                EligibilityRule(field="age", operator="greater_than_or_equal", value=18),
                EligibilityRule(field="age", operator="less_than_or_equal", value=65),
            ],
        ),
    ]


# Module-level cache so schemes are built once
_SCHEMES: List[Scheme] = _build_local_schemes()


class LocalRepository:
    """
    In-memory repository that mirrors the DynamoDBRepository interface.

    Drop-in replacement activated when AWS credentials are unavailable.
    All schemes are stored in module-level memory – no I/O required.
    """

    async def get_all_schemes(self) -> List[Scheme]:
        logger.info(
            "Serving schemes from local in-memory repository",
            extra={"event": "local_repo_get_all", "scheme_count": len(_SCHEMES)},
        )
        return list(_SCHEMES)

    async def get_scheme_by_id(self, scheme_id: str) -> Optional[Scheme]:
        for scheme in _SCHEMES:
            if scheme.scheme_id == scheme_id:
                return scheme
        return None

    async def put_scheme(self, scheme: Scheme) -> None:
        """No-op in local mode. Schemes are defined at module level."""
        logger.warning(
            "put_scheme called on LocalRepository – data will not be persisted",
            extra={"event": "local_repo_put_scheme", "scheme_id": scheme.scheme_id},
        )
