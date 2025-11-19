"""Tests for export functionality."""

import json
import csv
import tempfile
from pathlib import Path

import pytest

from bedfellows.exporters import JSONExporter, CSVExporter


def test_json_export():
    """Test JSON export."""
    data = [
        {"name": "Test 1", "score": 0.85, "count": 10},
        {"name": "Test 2", "score": 0.75, "count": 5},
    ]

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        output_path = f.name

    try:
        exporter = JSONExporter(output_path)
        exporter.export(data)

        # Read and verify
        with open(output_path) as f:
            result = json.load(f)

        assert "metadata" in result
        assert "data" in result
        assert result["metadata"]["record_count"] == 2
        assert len(result["data"]) == 2
        assert result["data"][0]["name"] == "Test 1"
    finally:
        Path(output_path).unlink()


def test_csv_export():
    """Test CSV export."""
    data = [
        {"name": "Test 1", "score": 0.85, "count": 10},
        {"name": "Test 2", "score": 0.75, "count": 5},
    ]

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
        output_path = f.name

    try:
        exporter = CSVExporter(output_path)
        exporter.export(data)

        # Read and verify
        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["name"] == "Test 1"
        assert rows[0]["score"] == "0.85"
    finally:
        Path(output_path).unlink()


def test_json_export_multiple():
    """Test exporting multiple datasets to JSON."""
    datasets = {
        "scores": [
            {"name": "A", "score": 0.9},
            {"name": "B", "score": 0.8},
        ],
        "stats": [
            {"metric": "total", "value": 100},
        ],
    }

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        output_path = f.name

    try:
        exporter = JSONExporter(output_path)
        exporter.export_multiple(datasets)

        # Read and verify
        with open(output_path) as f:
            result = json.load(f)

        assert "datasets" in result
        assert "scores" in result["datasets"]
        assert "stats" in result["datasets"]
        assert len(result["datasets"]["scores"]) == 2
    finally:
        Path(output_path).unlink()
