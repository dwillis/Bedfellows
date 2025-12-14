"""Base class for FEC data fetchers."""

import logging
import zipfile
from pathlib import Path
from typing import Optional, List
from urllib.parse import urljoin

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


class BaseFetcher:
    """Base class for downloading FEC bulk data files."""

    def __init__(
        self,
        base_url: str = "https://www.fec.gov/files/bulk-downloads/",
        data_dir: str = "data/downloads",
    ):
        """
        Initialize fetcher.

        Args:
            base_url: Base URL for FEC bulk downloads
            data_dir: Directory to store downloaded files
        """
        self.base_url = base_url
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def download_file(
        self, url: str, output_path: Optional[Path] = None, show_progress: bool = True
    ) -> Path:
        """
        Download a file from URL.

        Args:
            url: URL to download
            output_path: Optional output path (defaults to data_dir/filename)
            show_progress: Whether to show progress bar

        Returns:
            Path to downloaded file
        """
        if output_path is None:
            filename = url.split("/")[-1]
            output_path = self.data_dir / filename

        # Skip if already downloaded
        if output_path.exists():
            logger.info(f"File already exists: {output_path}")
            return output_path

        logger.info(f"Downloading {url} to {output_path}")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with open(output_path, "wb") as f:
                if show_progress and total_size > 0:
                    with tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        desc=output_path.name,
                    ) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            logger.info(f"Downloaded to {output_path}")
            return output_path

        except requests.RequestException as e:
            logger.error(f"Error downloading {url}: {e}")
            raise

    def extract_zip(
        self, zip_path: Path, extract_dir: Optional[Path] = None
    ) -> List[Path]:
        """
        Extract ZIP file.

        Args:
            zip_path: Path to ZIP file
            extract_dir: Directory to extract to (defaults to same as ZIP)

        Returns:
            List of extracted file paths
        """
        if extract_dir is None:
            extract_dir = zip_path.parent

        logger.info(f"Extracting {zip_path} to {extract_dir}")

        extracted_files = []
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for member in zip_ref.namelist():
                zip_ref.extract(member, extract_dir)
                extracted_files.append(extract_dir / member)

        logger.info(f"Extracted {len(extracted_files)} files")
        return extracted_files

    def download_and_extract(
        self, url: str, output_dir: Optional[Path] = None, keep_zip: bool = False
    ) -> List[Path]:
        """
        Download and extract a ZIP file.

        Args:
            url: URL to download
            output_dir: Directory for extracted files
            keep_zip: Whether to keep the ZIP file after extraction

        Returns:
            List of extracted file paths
        """
        # Download
        zip_path = self.download_file(url)

        # Extract
        extracted = self.extract_zip(zip_path, output_dir or self.data_dir)

        # Clean up ZIP if requested
        if not keep_zip:
            zip_path.unlink()
            logger.debug(f"Removed ZIP file: {zip_path}")

        return extracted

    def build_url(self, *parts: str) -> str:
        """
        Build URL from base and parts.

        Args:
            parts: URL parts to join

        Returns:
            Complete URL
        """
        url = self.base_url.rstrip('/')
        for part in parts:
            part = part.lstrip('/')
            url = f"{url}/{part}"
        return url
