"""Fetcher for FEC candidate data."""

import logging
from pathlib import Path
from typing import Optional, List

from bedfellows.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)


class CandidateFetcher(BaseFetcher):
    """Download FEC candidate master files."""

    def fetch_candidates(
        self, cycle: Optional[str] = None, all_cycles: bool = False
    ) -> List[Path]:
        """
        Download candidate master file(s).

        The FEC candidate master file contains information about all federal candidates.
        File format: cn.txt (all cycles) or cn{YY}.zip (specific cycle)

        Args:
            cycle: Specific cycle to download (e.g., "2024", "22")
            all_cycles: Download all cycles file (cn.txt)

        Returns:
            List of downloaded file paths
        """
        files = []

        if all_cycles:
            # Download all cycles file
            url = self.build_url("cn.txt")
            output_path = self.data_dir / "cn.txt"
            files.append(self.download_file(url, output_path))

        elif cycle:
            # Format cycle as 4-digit year and 2-digit year
            if len(cycle) == 2:
                cycle_2digit = cycle
                cycle_4digit = "20" + cycle  # Convert "24" -> "2024"
            else:
                cycle_4digit = cycle
                cycle_2digit = cycle[2:]  # Convert "2024" -> "24"

            # Download specific cycle ZIP to data/downloads
            filename = f"cn{cycle_2digit}.zip"
            url = self.build_url(cycle_4digit, filename)

            try:
                extracted = self.download_and_extract(url, output_dir=self.data_dir)
                files.extend(extracted)
            except Exception as e:
                logger.error(f"Error downloading candidate data for cycle {cycle}: {e}")
                raise

        else:
            raise ValueError("Must specify either cycle or all_cycles=True")

        logger.info(f"Downloaded {len(files)} candidate file(s)")
        return files

    def get_latest_cycle(self) -> str:
        """
        Get the latest available election cycle.

        Returns:
            Latest cycle as 2-digit year string
        """
        import datetime

        current_year = datetime.datetime.now().year
        # Election cycles are even years
        if current_year % 2 == 0:
            return str(current_year)[2:]
        else:
            return str(current_year - 1)[2:]
