"""Tests for database models."""

import pytest
from peewee import SqliteDatabase

from bedfellows.models import (
    init_models,
    create_all_tables,
    FecCandidates,
    FecCommittees,
    FecContributions,
    FinalScores,
)


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    db = SqliteDatabase(":memory:")
    init_models(db)
    create_all_tables()
    return db


def test_create_candidate(test_db):
    """Test creating a candidate record."""
    candidate = FecCandidates.create(
        fecid="H0TX01234",
        name="TEST CANDIDATE",
        party="DEM",
        state="TX",
        cycle="2024",
        district="01",
        office_state="TX",
        branch="H"
    )

    assert candidate.fecid == "H0TX01234"
    assert candidate.name == "TEST CANDIDATE"
    assert FecCandidates.select().count() == 1


def test_create_committee(test_db):
    """Test creating a committee record."""
    committee = FecCommittees.create(
        fecid="C00123456",
        name="TEST PAC",
        committee_type="N",
        cycle="2024",
        is_super_pac=False
    )

    assert committee.fecid == "C00123456"
    assert committee.name == "TEST PAC"
    assert FecCommittees.select().count() == 1


def test_create_contribution(test_db):
    """Test creating a contribution record."""
    from datetime import datetime

    contrib = FecContributions.create(
        fec_committee_id="C00111111",
        contributor_name="DONOR PAC",
        other_id="C00222222",
        recipient_name="RECIPIENT PAC",
        amount="5000",
        cycle="2024",
        date=datetime(2024, 1, 15)
    )

    assert contrib.fec_committee_id == "C00111111"
    assert contrib.amount == "5000"
    assert FecContributions.select().count() == 1


def test_model_relationships(test_db):
    """Test relationships between models."""
    # Create committee
    committee = FecCommittees.create(
        fecid="C00123456",
        name="TEST PAC",
        cycle="2024"
    )

    # Create contributions from this committee
    for i in range(3):
        FecContributions.create(
            fec_committee_id=committee.fecid,
            contributor_name=committee.name,
            other_id=f"C0000000{i}",
            recipient_name=f"RECIPIENT {i}",
            amount="1000",
            cycle="2024"
        )

    # Query contributions
    contribs = FecContributions.select().where(
        FecContributions.fec_committee_id == committee.fecid
    )

    assert contribs.count() == 3
