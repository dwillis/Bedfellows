"""Fetcher for FEC contribution data."""

import logging
from pathlib import Path
from typing import Optional, List

from bedfellows.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)


class ContributionFetcher(BaseFetcher):
    """Download FEC committee contribution files."""

    def fetch_contributions(
        self, cycle: str
    ) -> List[Path]:
        """
        Download committee-to-committee contribution file (pas2) for a cycle.

        Args:
            cycle: Election cycle (e.g., "2024", "22")

        Returns:
            List of downloaded file paths
        """
        # Format cycle as 4-digit year and 2-digit year
        if len(cycle) == 2:
            cycle_2digit = cycle
            cycle_4digit = "20" + cycle  # Convert "24" -> "2024"
        else:
            cycle_4digit = cycle
            cycle_2digit = cycle[2:]  # Convert "2024" -> "24"

        # Download pas2 (committee-to-committee contributions) file
        filename = f"pas2{cycle_2digit}.zip"
        url = self.build_url(cycle_4digit, filename)

        try:
            extracted = self.download_and_extract(url)
            logger.info(
                f"Downloaded committee contributions for cycle {cycle}"
            )
            return extracted
        except Exception as e:
            logger.error(
                f"Error downloading committee contributions for cycle {cycle}: {e}"
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
