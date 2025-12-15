"""
Database models for Bedfellows FEC campaign finance analysis.

All models use Peewee ORM with configurable database backend (SQLite, MySQL, PostgreSQL).
"""

import logging
from csv import DictReader
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from peewee import (
    Model,
    CharField,
    IntegerField,
    FloatField,
    DateTimeField,
    DateField,
    BooleanField,
    Database,
)
from tqdm import tqdm

logger = logging.getLogger(__name__)

# Global database instance - will be set by init_database()
database_proxy: Optional[Database] = None


def chunked(iterable, n):
    """Yield successive n-sized chunks from iterable."""
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


class BaseModel(Model):
    """Base model for all Bedfellows models."""

    class Meta:
        legacy_table_names = False

    @classmethod
    def set_database(cls, db: Database):
        """Set the database for this model and all subclasses."""
        cls._meta.database = db

    @classmethod
    def create_tables_safe(cls):
        """Create tables if they don't exist."""
        if cls._meta.database:
            cls._meta.database.create_tables([cls], safe=True)
            logger.debug(f"Created table: {cls._meta.table_name}")


# ============================================================================
# Core FEC Data Models
# ============================================================================


class FecCommitteeContributions(BaseModel):
    """Raw FEC committee contribution data."""

    fec_committee_id = CharField(null=True, max_length=10, index=True)
    amendment = CharField(null=True)
    report_type = CharField(null=True, index=True)
    pgi = CharField(null=True)
    microfilm = CharField(null=True)
    transaction_type = CharField(null=True, index=True)
    entity_type = CharField(null=True, index=True)
    contributor_name = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True, max_length=2)
    zipcode = CharField(null=True, max_length=10)
    employer = CharField(null=True)
    occupation = CharField(null=True)
    date = DateTimeField(null=True, index=True)
    amount = IntegerField(null=True)
    other_id = CharField(null=True, max_length=10, index=True)
    recipient_name = CharField(null=True)
    recipient_state = CharField(null=True, max_length=2)
    recipient_party = CharField(null=True)
    cycle = CharField(null=True, max_length=5)
    transaction_id = CharField(null=True)
    filing_id = CharField(null=True)
    memo_code = CharField(null=True)
    memo_text = CharField(null=True)
    fec_record_number = CharField(null=True)

    class Meta:
        indexes = (
            (
                (
                    "transaction_type",
                    "entity_type",
                    "date",
                    "fec_committee_id",
                    "other_id",
                ),
                False,
            ),
        )

    @classmethod
    def load_from_csv(cls, csv_path: str, batch_size: int = 1000) -> int:
        """
        Load data from pipe-delimited FEC file.

        Args:
            csv_path: Path to FEC file
            batch_size: Number of records per batch

        Returns:
            Number of records loaded
        """
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # FEC committee contributions file column names
        fieldnames = [
            "fec_committee_id",
            "amendment",
            "report_type",
            "pgi",
            "microfilm",
            "transaction_type",
            "entity_type",
            "contributor_name",
            "city",
            "state",
            "zipcode",
            "employer",
            "occupation",
            "date",
            "amount",
            "other_id",
            "recipient_name",
            "transaction_id",
            "filing_id",
            "memo_code",
            "memo_text",
            "fec_record_number",
        ]

        count = 0
        with open(csv_file) as f, cls._meta.database.atomic():
            rows = DictReader(f, fieldnames=fieldnames, delimiter="|")
            logger.info(f"Loading {cls._meta.table_name} from {csv_path}")

            for batch in tqdm(chunked(rows, batch_size), desc="Loading batches"):
                src_data = []
                for row in batch:
                    # Parse date field (FEC format: MMDDYYYY)
                    if row.get("date") and row["date"] != "" and len(row["date"]) == 8:
                        try:
                            row["date"] = datetime.strptime(row["date"], "%m%d%Y")
                        except ValueError:
                            row["date"] = None
                    else:
                        row["date"] = None

                    # Parse amount field
                    if row.get("amount"):
                        try:
                            row["amount"] = int(row["amount"])
                        except (ValueError, TypeError):
                            row["amount"] = None

                    # Set fields not in FEC file
                    row["cycle"] = None  # To be calculated from date or set externally
                    row["recipient_state"] = None
                    row["recipient_party"] = None

                    src_data.append(row)

                if src_data:
                    cls.insert_many(src_data).execute()
                    count += len(src_data)

        logger.info(f"Loaded {count} records into {cls._meta.table_name}")
        return count


class FecCommittees(BaseModel):
    """FEC committee master file."""

    fecid = CharField(null=True, index=True, max_length=10)
    name = CharField(null=True)
    treasurer = CharField(null=True)
    address_one = CharField(null=True)
    address_two = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True, max_length=2)
    zip = CharField(null=True, max_length=10)
    designation = CharField(null=True)
    committee_type = CharField(null=True, index=True)
    party = CharField(null=True, max_length=3)
    filing_frequency = CharField(null=True)
    interest_group = CharField(null=True)
    organization = CharField(null=True)
    fec_candidate_id = CharField(null=True, max_length=10, index=True)
    cycle = CharField(null=True, index=True, max_length=5)
    is_leadership = BooleanField(default=False)
    is_super_pac = BooleanField(default=False, index=True)

    class Meta:
        indexes = ((("fec_candidate_id", "fecid"), False),)

    @classmethod
    def load_from_csv(cls, csv_path: str, batch_size: int = 1000) -> int:
        """Load committee data from pipe-delimited FEC file."""
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # FEC committee file column names
        fieldnames = [
            "fecid",
            "name",
            "treasurer",
            "address_one",
            "address_two",
            "city",
            "state",
            "zip",
            "designation",
            "committee_type",
            "party",
            "filing_frequency",
            "interest_group",
            "organization",
            "fec_candidate_id",
        ]

        count = 0
        with open(csv_file) as f, cls._meta.database.atomic():
            rows = DictReader(f, fieldnames=fieldnames, delimiter="|")
            logger.info(f"Loading {cls._meta.table_name} from {csv_path}")

            for batch in tqdm(chunked(rows, batch_size), desc="Loading batches"):
                src_data = []
                for row in batch:
                    # Set default values for fields not in FEC file
                    row["cycle"] = None  # To be set externally or calculated
                    row["is_leadership"] = False
                    # Detect Super PACs by committee type 'O' (independent expenditure-only)
                    row["is_super_pac"] = row.get("committee_type") == "O"
                    src_data.append(row)

                if src_data:
                    cls.insert_many(src_data).execute()
                    count += len(src_data)

        logger.info(f"Loaded {count} records into {cls._meta.table_name}")
        return count


class FecCandidates(BaseModel):
    """FEC candidate master file."""

    fecid = CharField(null=True, max_length=10, index=True)
    name = CharField(null=True, index=True)
    party = CharField(null=True, max_length=3)
    status = CharField(null=True)
    address_one = CharField(null=True)
    address_two = CharField(null=True)
    city = CharField(null=True)
    state = CharField(null=True, max_length=2)
    zip = CharField(null=True, max_length=10)
    fec_committee_id = CharField(null=True, max_length=10)
    cycle = CharField(null=True, max_length=5, index=True)
    district = CharField(null=True, max_length=4, index=True)
    office_state = CharField(null=True, max_length=2, index=True)
    cand_status = CharField(null=True)
    branch = CharField(null=True, max_length=1, index=True)

    class Meta:
        indexes = (
            (("fecid", "name", "district", "office_state", "branch", "cycle"), False),
        )

    @classmethod
    def load_from_csv(cls, csv_path: str, batch_size: int = 1000) -> int:
        """Load candidate data from pipe-delimited FEC file."""
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        # FEC candidate file column names
        fieldnames = [
            "fecid",
            "name",
            "party",
            "cycle",
            "office_state",
            "branch",
            "district",
            "status",
            "cand_status",
            "fec_committee_id",
            "address_one",
            "address_two",
            "city",
            "state",
            "zip",
        ]

        count = 0
        with open(csv_file) as f:
            rows = DictReader(f, fieldnames=fieldnames, delimiter="|")
            src_data = list(rows)

        logger.info(f"Loading {len(src_data)} records into {cls._meta.table_name}")

        for batch in tqdm(chunked(src_data, batch_size), desc="Loading batches"):
            if batch:
                cls.insert_many(batch).execute()
                count += len(batch)

        logger.info(f"Loaded {count} records into {cls._meta.table_name}")
        return count


class FecContributions(BaseModel):
    """Filtered FEC contributions (excludes Super PACs)."""

    fec_committee_id = CharField(null=True, max_length=10, index=True)
    report_type = CharField(null=True, index=True)
    contributor_name = CharField(null=True)
    date = DateTimeField(null=True, index=True)
    amount = CharField(null=True)
    other_id = CharField(null=True, index=True, max_length=10)
    recipient_name = CharField(null=True)
    cycle = CharField(null=True, max_length=5, index=True)

    class Meta:
        indexes = (
            (("fec_committee_id", "other_id", "report_type"), False),
            (("cycle", "fec_committee_id", "other_id"), False),
            (
                (
                    "fec_committee_id",
                    "cycle",
                    "other_id",
                    "contributor_name",
                    "recipient_name",
                    "date",
                    "amount",
                ),
                False,
            ),
        )

    @classmethod
    def load_from_committee_contributions(cls) -> int:
        """
        Load filtered contributions from FecCommitteeContributions.

        Excludes Super PACs and applies filtering criteria.

        Returns:
            Number of records loaded
        """
        # Get Super PAC IDs
        super_pac_query = FecCommittees.select(FecCommittees.fecid).where(
            FecCommittees.is_super_pac == True
        )
        super_pac_ids = [c.fecid for c in super_pac_query]

        logger.info(f"Found {len(super_pac_ids)} Super PACs to exclude")

        # Get field mapping
        keys = cls._meta.sorted_field_names
        keys.remove(cls._meta.primary_key.name)

        from_fields = [
            v
            for k, v in FecCommitteeContributions._meta.fields.items()
            if k in keys
        ]
        to_fields = [v for k, v in cls._meta.fields.items() if k in keys]

        # Insert filtered data
        query = cls.insert_from(
            FecCommitteeContributions.select(*from_fields)
            .where(FecCommitteeContributions.fec_committee_id.not_in(super_pac_ids))
            .where(FecCommitteeContributions.other_id.not_in(super_pac_ids)),
            fields=to_fields,
        )

        count = query.execute()
        logger.info(f"Loaded {count} filtered contributions")
        return count


# ============================================================================
# Score Calculation Models
# ============================================================================


class TotalDonatedByContributor(BaseModel):
    """Total donations by each contributor."""

    fec_committee_id = CharField(null=True, max_length=9, index=True)
    contributor_name = CharField(null=True, max_length=200)
    total_by_PAC = FloatField(null=True)

    class Meta:
        indexes = (
            (("fec_committee_id", "contributor_name", "total_by_PAC"), False),
        )


class ExclusivityScores(BaseModel):
    """Exclusivity scores for donor-recipient pairs."""

    fec_committee_id = CharField(null=True, max_length=9, index=True)
    contributor_name = CharField(null=True, max_length=200)
    total_by_pac = CharField(null=True, max_length=10)
    other_id = CharField(null=True, max_length=9, index=True)
    recipient_name = CharField(null=True, max_length=200)
    amount = CharField(null=True, max_length=10)

    class Meta:
        indexes = ((("fec_committee_id", "other_id", "contributor_name"), False),)


class ReportTypeWeights(BaseModel):
    """Weights for different report types."""

    report_type = CharField(null=True, max_length=5, index=True)
    year_parity = CharField(null=True, max_length=5, index=True)
    weight = IntegerField()

    class Meta:
        indexes = ((("report_type", "year_parity", "weight"), False),)


class ReportTypeCountByPair(BaseModel):
    """Report type counts for each donor-recipient pair."""

    fec_committee_id = CharField(null=True, max_length=9, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    report_type = CharField(max_length=4)
    year_parity = CharField(max_length=5)
    d_date = DateTimeField()
    count = IntegerField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id"), False),)


class PairsCount(BaseModel):
    """Total transaction count for each donor-recipient pair."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    other_id = CharField(max_length=9, null=False, index=True)
    count = IntegerField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id", "count"), False),)


class ReportTypeFrequency(BaseModel):
    """Report type frequency for pairs."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    report_type = CharField(max_length=4)
    year_parity = CharField(max_length=5)
    d_date = DateTimeField()
    report_type_count_by_pair = CharField(max_length=10)
    pairs_count = IntegerField()
    report_type_frequency = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "report_type",
                    "year_parity",
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "report_type_frequency",
                ),
                False,
            ),
        )


class UnnormalizedReportTypeScores(BaseModel):
    """Unnormalized report type scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    report_type_score = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "report_type_score",
                ),
                False,
            ),
        )


class MaxReportTypeScore(BaseModel):
    """Maximum report type score for normalization."""

    max_report_type_score = FloatField()


class ReportTypeScores(BaseModel):
    """Normalized report type scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    report_type_score = FloatField()

    class Meta:
        indexes = (
            (("fec_committee_id", "other_id"), False),
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "report_type_score",
                ),
                False,
            ),
        )


class UnnormalizedPeriodicityScores(BaseModel):
    """Unnormalized periodicity scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    stddev_pop = FloatField()
    day_diff = IntegerField()
    periodicity_score = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "periodicity_score",
                ),
                False,
            ),
        )


class CapUnnormalizedScore(BaseModel):
    """Cap for unnormalized scores."""

    cap_unnormalized_score = FloatField()


class PeriodicityScores(BaseModel):
    """Normalized periodicity scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    periodicity_score = FloatField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id"), False),)


class ContributorTypes(BaseModel):
    """Contributor type classification."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    cycle = CharField(max_length=5, index=True)
    contributor_type = CharField(max_length=15)

    class Meta:
        indexes = ((("fec_committee_id", "cycle"), False),)


class RecipientTypes(BaseModel):
    """Recipient type classification."""

    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    cycle = CharField(max_length=5, index=True)
    recipient_type = CharField(max_length=15)


class ContributionLimits(BaseModel):
    """Contribution limits by type and cycle."""

    contributor_type = CharField(max_length=15, null=False)
    recipient_type = CharField(max_length=15, null=False)
    cycle = CharField(max_length=5)
    contribution_limit = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "contributor_type",
                    "recipient_type",
                    "cycle",
                    "contribution_limit",
                ),
                False,
            ),
        )


class JoinedContrRecptTypes(BaseModel):
    """Joined contributor and recipient types with contributions."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    contributor_type = CharField(max_length=15)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    recipient_type = CharField(max_length=15)
    cycle = CharField(max_length=5, index=True)
    date = DateTimeField()
    amount = FloatField()

    class Meta:
        indexes = ((("contributor_type", "recipient_type", "cycle"), False),)


class MaxedOutSubscores(BaseModel):
    """Maxed out subscores for individual contributions."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    contributor_type = CharField(max_length=15)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    recipient_type = CharField(max_length=15)
    cycle = CharField(max_length=5, index=True)
    date = DateField()
    amount = FloatField()
    contribution_limit = FloatField()
    maxed_out_subscore = FloatField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id", "cycle"), False),)


class InboundMaxedOutSubscores(MaxedOutSubscores):
    """Inbound maxed out subscores (inherits from MaxedOutSubscores)."""

    pass


class UnnormalizedMaxedOutScores(BaseModel):
    """Unnormalized maxed out scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    contributor_type = CharField(max_length=15)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    recipient_type = CharField(max_length=18)
    maxed_out_score = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "contributor_type",
                    "other_id",
                    "recipient_name",
                    "recipient_type",
                    "maxed_out_score",
                ),
                False,
            ),
        )


class MaxMaxedOutScore(BaseModel):
    """Maximum maxed out score for normalization."""

    max_maxed_out_score = FloatField()


class MaxedOutScores(BaseModel):
    """Normalized maxed out scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    contributor_type = CharField(max_length=15)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    recipient_type = CharField(max_length=18)
    maxed_out_score = FloatField()

    class Meta:
        indexes = (
            (("fec_committee_id", "other_id"), False),
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "contributor_type",
                    "other_id",
                    "recipient_name",
                    "recipient_type",
                    "maxed_out_score",
                ),
                False,
            ),
        )


class UnnormalizedLengthScores(BaseModel):
    """Unnormalized length scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    max_date = DateTimeField()
    min_date = DateTimeField()
    length_score = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "max_date",
                    "min_date",
                    "length_score",
                ),
                False,
            ),
        )


class MaxLengthScore(BaseModel):
    """Maximum length score for normalization."""

    max_length_score = FloatField()


class LengthScores(BaseModel):
    """Normalized length scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    max_date = DateTimeField()
    min_date = DateTimeField()
    length_score = FloatField()

    class Meta:
        indexes = (
            (("fec_committee_id", "other_id"), False),
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "max_date",
                    "min_date",
                    "length_score",
                ),
                False,
            ),
        )


class RacesList(BaseModel):
    """List of races for race focus calculation."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    fec_candidate_id = CharField(max_length=9, null=False)
    candidate_name = CharField(max_length=200)
    district = CharField(max_length=3)
    office_state = CharField(max_length=3)
    branch = CharField(max_length=2)
    cycle = CharField(max_length=5, index=True)

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "cycle",
                    "district",
                    "office_state",
                    "branch",
                    "contributor_name",
                ),
                False,
            ),
        )


class RaceFocusScores(BaseModel):
    """Race focus scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    race_focus_score = FloatField()

    class Meta:
        indexes = ((("fec_committee_id", "race_focus_score"), False),)


class ScoreWeights(BaseModel):
    """Weights for combining scores."""

    score_type = CharField(max_length=30, null=False, index=True)
    weight = FloatField()


class FiveScores(BaseModel):
    """Five component scores (without race focus)."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    exclusivity_score = FloatField()
    report_type_score = FloatField()
    periodicity_score = FloatField()
    maxed_out_score = FloatField()
    length_score = FloatField()
    five_score = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "five_score",
                ),
                False,
            ),
        )


class FinalScores(BaseModel):
    """Final combined scores."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    committee_name = CharField(max_length=200, null=True)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    count = IntegerField()
    exclusivity_score = FloatField()
    report_type_score = FloatField()
    periodicity_score = FloatField()
    maxed_out_score = FloatField()
    length_score = FloatField()
    race_focus_score = FloatField()
    final_score = FloatField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id"), False),)


class FiveSum(BaseModel):
    """Sum of five scores (for normalization)."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    exclusivity_score = FloatField()
    report_type_score = FloatField()
    periodicity_score = FloatField()
    maxed_out_score = FloatField()
    length_score = FloatField()
    five_sum = FloatField()

    class Meta:
        indexes = (
            (
                (
                    "fec_committee_id",
                    "contributor_name",
                    "other_id",
                    "recipient_name",
                    "five_sum",
                ),
                False,
            ),
        )


class FinalSum(BaseModel):
    """Sum of all scores (for normalization)."""

    fec_committee_id = CharField(max_length=9, null=False, index=True)
    contributor_name = CharField(max_length=200)
    other_id = CharField(max_length=9, null=False, index=True)
    recipient_name = CharField(max_length=200)
    count = IntegerField()
    exclusivity_score = FloatField()
    report_type_score = FloatField()
    periodicity_score = FloatField()
    maxed_out_score = FloatField()
    length_score = FloatField()
    race_focus_score = FloatField()
    final_sum = FloatField()

    class Meta:
        indexes = ((("fec_committee_id", "other_id"), False),)


# ============================================================================
# Model Collections
# ============================================================================

# All models for easy reference
ALL_MODELS = [
    # Core FEC data
    FecCommitteeContributions,
    FecCommittees,
    FecCandidates,
    FecContributions,
    # Score calculation
    TotalDonatedByContributor,
    ExclusivityScores,
    ReportTypeWeights,
    ReportTypeCountByPair,
    PairsCount,
    ReportTypeFrequency,
    UnnormalizedReportTypeScores,
    MaxReportTypeScore,
    ReportTypeScores,
    UnnormalizedPeriodicityScores,
    CapUnnormalizedScore,
    PeriodicityScores,
    ContributorTypes,
    RecipientTypes,
    ContributionLimits,
    JoinedContrRecptTypes,
    MaxedOutSubscores,
    InboundMaxedOutSubscores,
    UnnormalizedMaxedOutScores,
    MaxMaxedOutScore,
    MaxedOutScores,
    UnnormalizedLengthScores,
    MaxLengthScore,
    LengthScores,
    RacesList,
    RaceFocusScores,
    ScoreWeights,
    FiveScores,
    FinalScores,
    FiveSum,
    FinalSum,
]

# Core FEC data models
FEC_CORE_MODELS = [
    FecCommitteeContributions,
    FecCommittees,
    FecCandidates,
    FecContributions,
]

# Score calculation models
SCORE_MODELS = [m for m in ALL_MODELS if m not in FEC_CORE_MODELS]


def init_models(database: Database) -> None:
    """
    Initialize all models with the given database.

    Args:
        database: Peewee database instance
    """
    global database_proxy
    database_proxy = database

    for model in ALL_MODELS:
        model._meta.database = database

    logger.info(f"Initialized {len(ALL_MODELS)} models with database")


def create_all_tables() -> None:
    """Create all tables in the database."""
    if database_proxy is None:
        raise RuntimeError("Models not initialized. Call init_models() first.")

    database_proxy.create_tables(ALL_MODELS, safe=True)
    logger.info(f"Created {len(ALL_MODELS)} tables")


def get_all_models() -> List[type]:
    """Get list of all model classes."""
    return ALL_MODELS.copy()
