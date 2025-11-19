"""Fetcher for FEC contribution data."""

import logging
from pathlib import Path
from typing import Optional, List

from bedfellows.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)


class ContributionFetcher(BaseFetcher):
    """Download FEC committee contribution files."""

    def fetch_contributions(
        self, cycle: str, contribution_type: str = "committee"
    ) -> List[Path]:
        """
        Download committee-to-committee contribution file for a cycle.

        The FEC provides several types of contribution files:
        - Committee contributions: pas2{YY}.zip (our primary focus)
        - Individual contributions: indiv{YY}.zip
        - Candidate contributions: oth{YY}.zip

        Args:
            cycle: Election cycle (e.g., "2024", "22")
            contribution_type: Type of contributions ("committee", "individual", "other")

        Returns:
            List of downloaded file paths
        """
        # Format cycle as 2-digit year
        if len(cycle) == 4:
            cycle = cycle[2:]  # Convert "2024" -> "24"

        # Determine filename based on type
        if contribution_type == "committee":
            filename = f"pas2{cycle}.zip"
        elif contribution_type == "individual":
            filename = f"indiv{cycle}.zip"
        elif contribution_type == "other":
            filename = f"oth{cycle}.zip"
        else:
            raise ValueError(
                f"Invalid contribution_type: {contribution_type}. "
                "Must be 'committee', 'individual', or 'other'"
            )

        # Download and extract
        url = self.build_url("bulk-downloads", cycle, filename)

        try:
            extracted = self.download_and_extract(url)
            logger.info(
                f"Downloaded {contribution_type} contributions for cycle {cycle}"
            )
            return extracted
        except Exception as e:
            logger.error(
                f"Error downloading {contribution_type} contributions for cycle {cycle}: {e}"
            )
            raise

    def fetch_all_cycles(
        self, start_cycle: str, end_cycle: Optional[str] = None
    ) -> List[Path]:
        """
        Download committee contributions for multiple cycles.

        Args:
            start_cycle: Starting cycle (e.g., "2004")
            end_cycle: Ending cycle (defaults to current cycle)

        Returns:
            List of all downloaded file paths
        """
        if end_cycle is None:
            import datetime

            current_year = datetime.datetime.now().year
            end_cycle = str(current_year if current_year % 2 == 0 else current_year - 1)

        # Convert to integers for range
        start_year = int(start_cycle) if len(start_cycle) == 4 else 2000 + int(start_cycle)
        end_year = int(end_cycle) if len(end_cycle) == 4 else 2000 + int(end_cycle)

        all_files = []

        # Download each even-numbered year (election cycles)
        for year in range(start_year, end_year + 1, 2):
            cycle = str(year)[2:]  # Get 2-digit year
            try:
                files = self.fetch_contributions(cycle)
                all_files.extend(files)
            except Exception as e:
                logger.warning(f"Skipping cycle {year}: {e}")
                continue

        logger.info(
            f"Downloaded contributions for {len(all_files)} cycles from {start_cycle} to {end_cycle}"
        )
        return all_files
