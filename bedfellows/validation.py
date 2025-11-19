"""
Data validation module for Bedfellows.

Validates FEC data quality and completeness.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from peewee import Database

from bedfellows.models import (
    FecCandidates,
    FecCommittees,
    FecCommitteeContributions,
    FecContributions,
)

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates FEC data quality."""

    def __init__(self, database: Database):
        """
        Initialize validator.

        Args:
            database: Peewee database instance
        """
        self.db = database
        self.errors = []
        self.warnings = []
        self.stats = {}

    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks.

        Returns:
            Dictionary with validation results
        """
        logger.info("Starting data validation...")

        # Clear previous results
        self.errors = []
        self.warnings = []
        self.stats = {}

        # Run validation checks
        self.validate_candidates()
        self.validate_committees()
        self.validate_contributions()
        self.validate_referential_integrity()
        self.validate_data_quality()

        # Compile results
        results = {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }

        logger.info(f"Validation complete: {len(self.errors)} errors, {len(self.warnings)} warnings")

        return results

    def validate_candidates(self) -> None:
        """Validate candidate data."""
        logger.info("Validating candidates...")

        count = FecCandidates.select().count()
        self.stats["candidates_total"] = count

        if count == 0:
            self.errors.append("No candidate records found")
            return

        # Check for required fields
        null_fecid = FecCandidates.select().where(FecCandidates.fecid.is_null()).count()
        if null_fecid > 0:
            self.errors.append(f"{null_fecid} candidates missing FEC ID")

        null_name = FecCandidates.select().where(FecCandidates.name.is_null()).count()
        if null_name > 0:
            self.warnings.append(f"{null_name} candidates missing name")

        # Check for duplicates
        duplicates = (
            FecCandidates
            .select(FecCandidates.fecid, FecCandidates.cycle)
            .group_by(FecCandidates.fecid, FecCandidates.cycle)
            .having(fn.COUNT(FecCandidates.id) > 1)
            .count()
        )
        if duplicates > 0:
            self.warnings.append(f"{duplicates} duplicate candidate records (same FEC ID and cycle)")

        self.stats["candidates_valid"] = count - null_fecid

    def validate_committees(self) -> None:
        """Validate committee data."""
        logger.info("Validating committees...")

        count = FecCommittees.select().count()
        self.stats["committees_total"] = count

        if count == 0:
            self.errors.append("No committee records found")
            return

        # Check for required fields
        null_fecid = FecCommittees.select().where(FecCommittees.fecid.is_null()).count()
        if null_fecid > 0:
            self.errors.append(f"{null_fecid} committees missing FEC ID")

        null_name = FecCommittees.select().where(FecCommittees.name.is_null()).count()
        if null_name > 0:
            self.warnings.append(f"{null_name} committees missing name")

        # Check committee types
        invalid_types = (
            FecCommittees
            .select()
            .where(FecCommittees.committee_type.not_in(['P', 'H', 'S', 'C', 'N', 'Q', 'I', 'O', 'V', 'W']))
            .where(FecCommittees.committee_type.is_null(False))
            .count()
        )
        if invalid_types > 0:
            self.warnings.append(f"{invalid_types} committees with non-standard committee types")

        # Check Super PAC count
        super_pac_count = FecCommittees.select().where(FecCommittees.is_super_pac == True).count()
        self.stats["super_pacs"] = super_pac_count

        self.stats["committees_valid"] = count - null_fecid

    def validate_contributions(self) -> None:
        """Validate contribution data."""
        logger.info("Validating contributions...")

        # Check raw contributions
        raw_count = FecCommitteeContributions.select().count()
        self.stats["contributions_raw"] = raw_count

        if raw_count == 0:
            self.errors.append("No raw contribution records found")

        # Check filtered contributions
        filtered_count = FecContributions.select().count()
        self.stats["contributions_filtered"] = filtered_count

        if filtered_count == 0 and raw_count > 0:
            self.errors.append("Filtered contributions table is empty but raw data exists")
            return

        if filtered_count > 0:
            # Check for null amounts
            null_amount = FecContributions.select().where(FecContributions.amount.is_null()).count()
            if null_amount > 0:
                self.warnings.append(f"{null_amount} contributions missing amount")

            # Check for null dates
            null_date = FecContributions.select().where(FecContributions.date.is_null()).count()
            if null_date > 0:
                self.warnings.append(f"{null_date} contributions missing date")

            # Check for invalid amounts
            try:
                # This works for databases that support CAST in WHERE clauses
                negative_amount = (
                    FecContributions
                    .select()
                    .where(FecContributions.amount < '0')
                    .count()
                )
                if negative_amount > 0:
                    self.warnings.append(f"{negative_amount} contributions with negative amounts")
            except:
                pass  # Skip if database doesn't support this check

            self.stats["contributions_valid"] = filtered_count - null_amount

    def validate_referential_integrity(self) -> None:
        """Validate relationships between tables."""
        logger.info("Validating referential integrity...")

        contrib_count = FecContributions.select().count()
        if contrib_count == 0:
            return

        # Check if donor committees exist
        missing_donors = (
            FecContributions
            .select(FecContributions.fec_committee_id)
            .distinct()
            .where(
                FecContributions.fec_committee_id.not_in(
                    FecCommittees.select(FecCommittees.fecid)
                )
            )
            .count()
        )
        if missing_donors > 0:
            self.warnings.append(
                f"{missing_donors} unique donor committee IDs not found in committees table"
            )

        # Check if recipient committees exist
        missing_recipients = (
            FecContributions
            .select(FecContributions.other_id)
            .distinct()
            .where(
                FecContributions.other_id.not_in(
                    FecCommittees.select(FecCommittees.fecid)
                ) &
                FecContributions.other_id.not_in(
                    FecCandidates.select(FecCandidates.fecid)
                )
            )
            .count()
        )
        if missing_recipients > 0:
            self.warnings.append(
                f"{missing_recipients} unique recipient IDs not found in committees or candidates table"
            )

    def validate_data_quality(self) -> None:
        """Validate overall data quality metrics."""
        logger.info("Validating data quality...")

        contrib_count = FecContributions.select().count()
        if contrib_count == 0:
            return

        # Check date range
        try:
            date_range = (
                FecContributions
                .select(
                    fn.MIN(FecContributions.date).alias('min_date'),
                    fn.MAX(FecContributions.date).alias('max_date')
                )
                .where(FecContributions.date.is_null(False))
                .get()
            )

            if date_range.min_date and date_range.max_date:
                self.stats["date_range"] = {
                    "min": date_range.min_date.strftime("%Y-%m-%d"),
                    "max": date_range.max_date.strftime("%Y-%m-%d")
                }

                # Warn if data is old
                if date_range.max_date.year < datetime.now().year - 2:
                    self.warnings.append(
                        f"Data may be outdated (latest: {date_range.max_date.year})"
                    )

        except Exception as e:
            logger.warning(f"Could not check date range: {e}")

        # Check cycle distribution
        try:
            from peewee import fn

            cycles = list(
                FecContributions
                .select(
                    FecContributions.cycle,
                    fn.COUNT(FecContributions.id).alias('count')
                )
                .where(FecContributions.cycle.is_null(False))
                .group_by(FecContributions.cycle)
                .order_by(FecContributions.cycle)
                .dicts()
            )

            if cycles:
                self.stats["cycles"] = cycles

        except Exception as e:
            logger.warning(f"Could not check cycles: {e}")

    def print_report(self) -> None:
        """Print validation report to console."""
        print("\n" + "=" * 80)
        print("DATA VALIDATION REPORT")
        print("=" * 80)

        # Stats
        print("\n📊 Statistics:")
        for key, value in self.stats.items():
            if isinstance(value, (int, str)):
                print(f"  {key}: {value}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: {len(value)} entries")

        # Errors
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\n✅ No errors found")

        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        else:
            print("\n✅ No warnings")

        print("\n" + "=" * 80)
        print(f"Validation {'PASSED' if len(self.errors) == 0 else 'FAILED'}")
        print("=" * 80 + "\n")


def validate_data(database: Database) -> Dict[str, Any]:
    """
    Convenience function to validate data.

    Args:
        database: Peewee database instance

    Returns:
        Validation results dictionary
    """
    validator = DataValidator(database)
    results = validator.validate_all()
    validator.print_report()
    return results
