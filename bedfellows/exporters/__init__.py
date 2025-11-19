"""
Export functionality for Bedfellows results.

Supports multiple output formats:
- JSON: Machine-readable, API-friendly
- CSV: Spreadsheet-compatible
- Excel: Spreadsheet with formatting
- Datasette: Interactive web exploration
"""

from bedfellows.exporters.base import BaseExporter
from bedfellows.exporters.json_exporter import JSONExporter
from bedfellows.exporters.csv_exporter import CSVExporter
from bedfellows.exporters.datasette_exporter import DatasetteExporter

# Excel exporter requires openpyxl, so make it optional
try:
    from bedfellows.exporters.excel_exporter import ExcelExporter
    __all__ = ["BaseExporter", "JSONExporter", "CSVExporter", "ExcelExporter", "DatasetteExporter"]
except ImportError:
    __all__ = ["BaseExporter", "JSONExporter", "CSVExporter", "DatasetteExporter"]
