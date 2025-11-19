"""JSON export functionality."""

import json
import logging
from datetime import datetime, date
from typing import Any, Optional
from decimal import Decimal

from peewee import ModelSelect

from bedfellows.exporters.base import BaseExporter

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and Decimal objects."""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class JSONExporter(BaseExporter):
    """Export data to JSON format."""

    def __init__(self, output_path: str, pretty: bool = True):
        """
        Initialize JSON exporter.

        Args:
            output_path: Path to output JSON file
            pretty: Whether to format JSON with indentation
        """
        super().__init__(output_path)
        self.pretty = pretty
        self.validate_path(".json")

    def export(
        self,
        data: Any,
        model: Optional[type] = None,
        query: Optional[ModelSelect] = None,
    ) -> None:
        """
        Export data to JSON.

        Args:
            data: Data to export (list of dicts or dict)
            model: Model class (optional)
            query: Query (optional)
        """
        # Prepare metadata
        metadata = {
            "exported_at": datetime.now().isoformat(),
            "record_count": len(data) if isinstance(data, list) else 1,
        }

        if model:
            metadata["table_name"] = model._meta.table_name
            metadata["model"] = model.__name__

        # Prepare output
        output = {"metadata": metadata, "data": data}

        # Write to file
        with open(self.output_path, "w") as f:
            if self.pretty:
                json.dump(output, f, indent=2, cls=JSONEncoder)
            else:
                json.dump(output, f, cls=JSONEncoder)

        logger.info(
            f"Exported {metadata['record_count']} records to {self.output_path}"
        )

    def export_multiple(self, datasets: dict) -> None:
        """
        Export multiple datasets to a single JSON file.

        Args:
            datasets: Dictionary of dataset_name -> data mappings
        """
        metadata = {
            "exported_at": datetime.now().isoformat(),
            "datasets": {
                name: len(data) if isinstance(data, list) else 1
                for name, data in datasets.items()
            },
        }

        output = {"metadata": metadata, "datasets": datasets}

        with open(self.output_path, "w") as f:
            if self.pretty:
                json.dump(output, f, indent=2, cls=JSONEncoder)
            else:
                json.dump(output, f, cls=JSONEncoder)

        total_records = sum(metadata["datasets"].values())
        logger.info(
            f"Exported {total_records} total records across {len(datasets)} datasets to {self.output_path}"
        )
