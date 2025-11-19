"""CSV export functionality."""

import csv
import logging
from datetime import datetime, date
from typing import Any, Optional, List
from decimal import Decimal

from peewee import ModelSelect

from bedfellows.exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """Export data to CSV format."""

    def __init__(self, output_path: str):
        """
        Initialize CSV exporter.

        Args:
            output_path: Path to output CSV file
        """
        super().__init__(output_path)
        self.validate_path(".csv")

    def export(
        self,
        data: Any,
        model: Optional[type] = None,
        query: Optional[ModelSelect] = None,
    ) -> None:
        """
        Export data to CSV.

        Args:
            data: Data to export (list of dicts)
            model: Model class (optional)
            query: Query (optional)
        """
        if not data:
            logger.warning("No data to export")
            return

        # Ensure data is a list
        if not isinstance(data, list):
            data = [data]

        # Get field names from first record
        fieldnames = list(data[0].keys())

        # Write CSV
        with open(self.output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in data:
                # Convert datetime and Decimal objects to strings
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, (datetime, date)):
                        cleaned_row[key] = value.isoformat()
                    elif isinstance(value, Decimal):
                        cleaned_row[key] = float(value)
                    else:
                        cleaned_row[key] = value

                writer.writerow(cleaned_row)

        logger.info(f"Exported {len(data)} records to {self.output_path}")

    def export_multiple(self, datasets: dict, prefix: str = "") -> List[str]:
        """
        Export multiple datasets to separate CSV files.

        Args:
            datasets: Dictionary of dataset_name -> data mappings
            prefix: Prefix for output filenames

        Returns:
            List of created file paths
        """
        created_files = []

        for name, data in datasets.items():
            output_file = self.output_path.parent / f"{prefix}{name}.csv"
            exporter = CSVExporter(str(output_file))
            exporter.export(data)
            created_files.append(str(output_file))

        logger.info(f"Exported {len(datasets)} datasets to CSV files")
        return created_files
