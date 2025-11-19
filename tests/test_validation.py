"""Tests for data validation."""

import pytest
from peewee import SqliteDatabase
from datetime import datetime

from bedfellows.models import (
    init_models,
    create_all_tables,
    FecCandidates,
    FecCommittees,
    FecContributions,
)
from bedfellows.validation import DataValidator


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    db = SqliteDatabase(":memory:")
    init_models(db)
    create_all_tables()
    return db


def test_validate_empty_database(test_db):
    """Test validation on empty database."""
    validator = DataValidator(test_db)
    results = validator.validate_all()

    assert not results["valid"]  # Should have errors
    assert len(results["errors"]) > 0  # Should have "no records" errors


def test_validate_candidates(test_db):
    """Test candidate validation."""
    # Add valid candidate
    FecCandidates.create(
        fecid="H0TX01234",
        name="TEST CANDIDATE",
        cycle="2024"
    )

    # Add invalid candidate (missing fecid)
    FecCandidates.create(
        fecid=None,
        name="INVALID CANDIDATE",
        cycle="2024"
    )

    validator = DataValidator(test_db)
    results = validator.validate_all()

    # Should have error about missing fecid
    assert any("missing FEC ID" in str(error) for error in results["errors"])


def test_validate_committees(test_db):
    """Test committee validation."""
    # Add valid committee
    FecCommittees.create(
        fecid="C00123456",
        name="TEST PAC",
        cycle="2024"
    )

    # Add Super PAC
    FecCommittees.create(
        fecid="C00999999",
        name="SUPER PAC",
        is_super_pac=True,
        cycle="2024"
    )

    validator = DataValidator(test_db)
    results = validator.validate_all()

    assert results["stats"]["committees_total"] == 2
    assert results["stats"]["super_pacs"] == 1


def test_validate_contributions(test_db):
    """Test contribution validation."""
    # Add contributions
    FecContributions.create(
        fec_committee_id="C00111111",
        contributor_name="DONOR",
        other_id="C00222222",
        recipient_name="RECIPIENT",
        amount="5000",
        date=datetime(2024, 1, 15),
        cycle="2024"
    )

    FecContributions.create(
        fec_committee_id="C00111111",
        contributor_name="DONOR",
        other_id="C00333333",
        recipient_name="RECIPIENT 2",
        amount=None,  # Missing amount
        date=None,  # Missing date
        cycle="2024"
    )

    validator = DataValidator(test_db)
    results = validator.validate_all()

    # Should have warnings about missing data
    assert any("missing amount" in str(w) for w in results["warnings"])
    assert any("missing date" in str(w) for w in results["warnings"])
