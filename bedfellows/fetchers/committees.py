"""Fetcher for FEC committee data."""

import logging
from pathlib import Path
from typing import Optional, List

from bedfellows.fetchers.base import BaseFetcher

logger = logging.getLogger(__name__)


class CommitteeFetcher(BaseFetcher):
    """Download FEC committee master files."""

    def fetch_committees(
        self, cycle: Optional[str] = None, all_cycles: bool = False
    ) -> List[Path]:
        """
        Download committee master file(s).

        The FEC committee master file contains information about all political committees.
        File format: cm.txt (all cycles) or cm{YY}.zip (specific cycle)

        Args:
            cycle: Specific cycle to download (e.g., "2024", "22")
            all_cycles: Download all cycles file (cm.txt)

        Returns:
            List of downloaded file paths
        """
        files = []

        if all_cycles:
            # Download all cycles file
            url = self.build_url("cm.txt")
            output_path = self.data_dir / "cm.txt"
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
            filename = f"cm{cycle_2digit}.zip"
            url = self.build_url(cycle_4digit, filename)

            try:
                extracted = self.download_and_extract(url, output_dir=self.data_dir)
                files.extend(extracted)
            except Exception as e:
                logger.error(f"Error downloading committee data for cycle {cycle}: {e}")
                raise

        else:
            raise ValueError("Must specify either cycle or all_cycles=True")

        logger.info(f"Downloaded {len(files)} committee file(s)")
        return files
