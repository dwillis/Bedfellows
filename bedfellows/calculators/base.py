"""Base calculator class for score computation."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path

from peewee import Database
from tqdm import tqdm

logger = logging.getLogger(__name__)


class BaseCalculator(ABC):
    """Base class for score calculators."""

    def __init__(self, database: Database, config: Optional[Dict[str, Any]] = None):
        """
        Initialize calculator.

        Args:
            database: Peewee database instance
            config: Optional configuration dictionary
        """
        self.db = database
        self.config = config or {}
        self.weights = self.config.get("weights", {
            "exclusivity": 1.0,
            "report_type": 1.0,
            "periodicity": 1.0,
            "maxed_out": 1.0,
            "length": 1.0,
            "race_focus": 1.0,
        })

    @abstractmethod
    def setup(self) -> None:
        """Perform initial setup and data preparation."""
        pass

    @abstractmethod
    def compute_scores(self) -> None:
        """Compute all relationship scores."""
        pass

    def get_results(self, limit: Optional[int] = None):
        """
        Get computed results.

        Args:
            limit: Maximum number of results to return

        Returns:
            Query results
        """
        pass

    def log_progress(self, message: str, step: int, total: int):
        """
        Log progress message.

        Args:
            message: Progress message
            step: Current step number
            total: Total number of steps
        """
        logger.info(f"[{step}/{total}] {message}")
        print(f"[{step}/{total}] {message}")

    def execute_with_progress(self, func, description: str):
        """
        Execute function with progress logging.

        Args:
            func: Function to execute
            description: Description of the operation

        Returns:
            Function result
        """
        logger.info(f"Starting: {description}")
        print(f"⏳ {description}...")

        try:
            result = func()
            logger.info(f"Completed: {description}")
            print(f"✓ {description}")
            return result
        except Exception as e:
            logger.error(f"Error in {description}: {e}")
            print(f"✗ Error in {description}: {e}")
            raise
