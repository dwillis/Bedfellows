"""Datasette export and web interface functionality."""

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from peewee import Database, SqliteDatabase

from bedfellows.exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class DatasetteExporter(BaseExporter):
    """Export database to Datasette-compatible SQLite and launch web interface."""

    def __init__(
        self, output_path: str, metadata_path: Optional[str] = None, port: int = 8001
    ):
        """
        Initialize Datasette exporter.

        Args:
            output_path: Path to output SQLite database
            metadata_path: Optional path to metadata.json file
            port: Port for Datasette server
        """
        super().__init__(output_path)
        self.validate_path(".db")
        self.metadata_path = (
            Path(metadata_path) if metadata_path else self.output_path.with_suffix(".json")
        )
        self.port = port

    def export(
        self,
        data: Any,
        model: Optional[type] = None,
        query: Optional[type] = None,
    ) -> None:
        """
        Export is not used for Datasette - use copy_database instead.

        Args:
            data: Ignored
            model: Ignored
            query: Ignored
        """
        raise NotImplementedError(
            "Use copy_database() method for Datasette export instead"
        )

    def copy_database(self, source_db: Database) -> None:
        """
        Copy database to Datasette-compatible SQLite file.

        Args:
            source_db: Source database to copy
        """
        if isinstance(source_db, SqliteDatabase):
            # If already SQLite, just copy the file
            source_path = Path(source_db.database)
            if source_path != self.output_path:
                shutil.copy2(source_path, self.output_path)
                logger.info(f"Copied SQLite database to {self.output_path}")
            else:
                logger.info("Database already at target location")
        else:
            # For MySQL/PostgreSQL, need to export to SQLite
            # This is more complex - would need to iterate through all tables
            logger.error("Direct export from MySQL/PostgreSQL to SQLite not yet implemented")
            logger.info("Please use SQLite as your primary database for Datasette integration")
            raise NotImplementedError(
                "Export from MySQL/PostgreSQL to SQLite not yet implemented. "
                "Use SQLite as your database backend for Datasette support."
            )

    def create_metadata(self, title: str = "Bedfellows FEC Analysis") -> None:
        """
        Create Datasette metadata.json file.

        Args:
            title: Title for the Datasette instance
        """
        metadata = {
            "title": title,
            "description": "Federal Election Commission campaign finance relationship analysis",
            "license": "Public Domain",
            "license_url": "https://www.fec.gov/",
            "source": "FEC",
            "source_url": "https://www.fec.gov/data/browse-data/?tab=bulk-data",
            "databases": {
                self.output_path.stem: {
                    "tables": {
                        "final_scores": {
                            "title": "Final Relationship Scores",
                            "description": "Computed relationship scores between PAC donors and recipients",
                            "sort_desc": "final_score",
                            "facets": ["contributor_name", "recipient_name"],
                        },
                        "fec_candidates": {
                            "title": "FEC Candidates",
                            "description": "Federal Election Commission candidate master file",
                            "facets": ["party", "state", "branch", "cycle"],
                        },
                        "fec_committees": {
                            "title": "FEC Committees",
                            "description": "Federal Election Commission committee master file",
                            "facets": ["committee_type", "party", "state", "cycle"],
                        },
                        "fec_contributions": {
                            "title": "FEC Contributions",
                            "description": "Filtered committee-to-committee contributions (excludes Super PACs)",
                            "facets": ["report_type", "cycle"],
                        },
                    }
                }
            },
        }

        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Created Datasette metadata at {self.metadata_path}")

    def launch_datasette(
        self,
        open_browser: bool = True,
        host: str = "127.0.0.1",
        extra_args: Optional[list] = None,
    ) -> subprocess.Popen:
        """
        Launch Datasette server.

        Args:
            open_browser: Whether to open browser automatically
            host: Host to bind to
            extra_args: Additional command-line arguments

        Returns:
            Subprocess handle for the Datasette server
        """
        cmd = [
            "datasette",
            str(self.output_path),
            "--port",
            str(self.port),
            "--host",
            host,
        ]

        if self.metadata_path.exists():
            cmd.extend(["--metadata", str(self.metadata_path)])

        if open_browser:
            cmd.append("--open")

        if extra_args:
            cmd.extend(extra_args)

        logger.info(f"Launching Datasette: {' '.join(cmd)}")
        logger.info(f"Datasette will be available at http://{host}:{self.port}")

        try:
            process = subprocess.Popen(cmd)
            return process
        except FileNotFoundError:
            logger.error(
                "Datasette not found. Install with: pip install datasette"
            )
            raise

    def serve(
        self,
        source_db: Database,
        open_browser: bool = True,
        host: str = "127.0.0.1",
    ) -> subprocess.Popen:
        """
        One-step method to copy database, create metadata, and launch Datasette.

        Args:
            source_db: Source database
            open_browser: Whether to open browser
            host: Host to bind to

        Returns:
            Subprocess handle for the Datasette server
        """
        # Copy database
        self.copy_database(source_db)

        # Create metadata
        self.create_metadata()

        # Launch server
        return self.launch_datasette(open_browser=open_browser, host=host)
