"""Base exporter class."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, List
from peewee import Model, ModelSelect

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Base class for all exporters."""

    def __init__(self, output_path: str):
        """
        Initialize exporter.

        Args:
            output_path: Path to output file or directory
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(
        self,
        data: Any,
        model: Optional[type] = None,
        query: Optional[ModelSelect] = None,
    ) -> None:
        """
        Export data to the specified format.

        Args:
            data: Data to export (can be list of dicts, query, etc.)
            model: Model class (if exporting from model)
            query: Peewee query (if exporting query results)
        """
        pass

    def export_model(
        self,
        model: type,
        query: Optional[ModelSelect] = None,
        limit: Optional[int] = None,
    ) -> None:
        """
        Export data from a Peewee model.

        Args:
            model: Model class to export
            query: Optional query to filter results
            limit: Maximum number of records to export
        """
        if query is None:
            query = model.select()

        if limit:
            query = query.limit(limit)

        data = list(query.dicts())
        logger.info(f"Exporting {len(data)} records from {model._meta.table_name}")

        self.export(data, model=model, query=query)

    def validate_path(self, extension: str) -> None:
        """
        Validate output path has correct extension.

        Args:
            extension: Expected file extension (e.g., '.json', '.csv')
        """
        if not str(self.output_path).endswith(extension):
            self.output_path = self.output_path.with_suffix(extension)
            logger.debug(f"Adjusted output path to: {self.output_path}")
