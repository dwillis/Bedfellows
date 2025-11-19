"""
Configuration management for Bedfellows.

Supports configuration from:
1. Default values (lowest priority)
2. Configuration file (.ini or config.yaml)
3. Environment variables (highest priority)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from configparser import ConfigParser
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for Bedfellows application."""

    # Default configuration values
    DEFAULTS = {
        # Database
        "database_type": "sqlite",
        "sqlite_path": "data/bedfellows.db",
        "mysql_host": "localhost",
        "mysql_port": 3306,
        "mysql_user": "root",
        "mysql_password": "",
        "mysql_database": "fec",
        "postgres_host": "localhost",
        "postgres_port": 5432,
        "postgres_user": "postgres",
        "postgres_password": "",
        "postgres_database": "fec",
        # FEC Data
        "fec_bulk_data_url": "https://www.fec.gov/files/bulk-downloads/",
        "data_dir": "data",
        # Scoring weights
        "weight_exclusivity": 1.0,
        "weight_report_type": 1.0,
        "weight_periodicity": 1.0,
        "weight_maxed_out": 1.0,
        "weight_length": 1.0,
        "weight_race_focus": 1.0,
        # Logging
        "log_level": "INFO",
        "log_file": "bedfellows.log",
        # Web
        "datasette_host": "127.0.0.1",
        "datasette_port": 8001,
    }

    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        """
        Initialize configuration.

        Args:
            config_file: Path to configuration file (.ini format)
            load_env: Whether to load from .env file and environment variables
        """
        self.config: Dict[str, Any] = self.DEFAULTS.copy()

        # Load from .env file if requested
        if load_env:
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)
                logger.debug(f"Loaded environment from {env_path}")

        # Load from config file if provided
        if config_file:
            self.load_from_file(config_file)

        # Override with environment variables
        if load_env:
            self.load_from_env()

    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from .ini file.

        Args:
            config_file: Path to configuration file
        """
        config_path = Path(config_file)
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_file}")
            return

        parser = ConfigParser()
        parser.read(config_path)

        # Database section
        if parser.has_section("database"):
            self.config["database_type"] = parser.get(
                "database", "type", fallback=self.config["database_type"]
            )
            self.config["sqlite_path"] = parser.get(
                "database", "sqlite_path", fallback=self.config["sqlite_path"]
            )
            # MySQL
            if parser.has_option("database", "mysql_host"):
                self.config["mysql_host"] = parser.get("database", "mysql_host")
            if parser.has_option("database", "mysql_port"):
                self.config["mysql_port"] = parser.getint("database", "mysql_port")
            if parser.has_option("database", "mysql_user"):
                self.config["mysql_user"] = parser.get("database", "mysql_user")
            if parser.has_option("database", "mysql_password"):
                self.config["mysql_password"] = parser.get("database", "mysql_password")
            if parser.has_option("database", "mysql_database"):
                self.config["mysql_database"] = parser.get("database", "mysql_database")
            # PostgreSQL
            if parser.has_option("database", "postgres_host"):
                self.config["postgres_host"] = parser.get("database", "postgres_host")
            if parser.has_option("database", "postgres_port"):
                self.config["postgres_port"] = parser.getint("database", "postgres_port")
            if parser.has_option("database", "postgres_user"):
                self.config["postgres_user"] = parser.get("database", "postgres_user")
            if parser.has_option("database", "postgres_password"):
                self.config["postgres_password"] = parser.get("database", "postgres_password")
            if parser.has_option("database", "postgres_database"):
                self.config["postgres_database"] = parser.get("database", "postgres_database")

        # FEC section
        if parser.has_section("fec"):
            self.config["fec_bulk_data_url"] = parser.get(
                "fec", "bulk_data_url", fallback=self.config["fec_bulk_data_url"]
            )
            self.config["data_dir"] = parser.get(
                "fec", "data_dir", fallback=self.config["data_dir"]
            )

        # Scoring section
        if parser.has_section("scoring"):
            for weight in [
                "weight_exclusivity",
                "weight_report_type",
                "weight_periodicity",
                "weight_maxed_out",
                "weight_length",
                "weight_race_focus",
            ]:
                if parser.has_option("scoring", weight):
                    self.config[weight] = parser.getfloat("scoring", weight)

        # Logging section
        if parser.has_section("logging"):
            self.config["log_level"] = parser.get(
                "logging", "level", fallback=self.config["log_level"]
            )
            self.config["log_file"] = parser.get(
                "logging", "file", fallback=self.config["log_file"]
            )

        # Web section
        if parser.has_section("web"):
            if parser.has_option("web", "host"):
                self.config["datasette_host"] = parser.get("web", "host")
            if parser.has_option("web", "port"):
                self.config["datasette_port"] = parser.getint("web", "port")

        logger.info(f"Loaded configuration from {config_file}")

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Database
        if os.getenv("DATABASE_TYPE"):
            self.config["database_type"] = os.getenv("DATABASE_TYPE")
        if os.getenv("SQLITE_PATH"):
            self.config["sqlite_path"] = os.getenv("SQLITE_PATH")

        # MySQL
        if os.getenv("MYSQL_HOST"):
            self.config["mysql_host"] = os.getenv("MYSQL_HOST")
        if os.getenv("MYSQL_PORT"):
            self.config["mysql_port"] = int(os.getenv("MYSQL_PORT"))
        if os.getenv("MYSQL_USER"):
            self.config["mysql_user"] = os.getenv("MYSQL_USER")
        if os.getenv("MYSQL_PASSWORD"):
            self.config["mysql_password"] = os.getenv("MYSQL_PASSWORD")
        if os.getenv("MYSQL_DATABASE"):
            self.config["mysql_database"] = os.getenv("MYSQL_DATABASE")

        # PostgreSQL
        if os.getenv("POSTGRES_HOST"):
            self.config["postgres_host"] = os.getenv("POSTGRES_HOST")
        if os.getenv("POSTGRES_PORT"):
            self.config["postgres_port"] = int(os.getenv("POSTGRES_PORT"))
        if os.getenv("POSTGRES_USER"):
            self.config["postgres_user"] = os.getenv("POSTGRES_USER")
        if os.getenv("POSTGRES_PASSWORD"):
            self.config["postgres_password"] = os.getenv("POSTGRES_PASSWORD")
        if os.getenv("POSTGRES_DATABASE"):
            self.config["postgres_database"] = os.getenv("POSTGRES_DATABASE")

        # FEC
        if os.getenv("FEC_BULK_DATA_URL"):
            self.config["fec_bulk_data_url"] = os.getenv("FEC_BULK_DATA_URL")
        if os.getenv("DATA_DIR"):
            self.config["data_dir"] = os.getenv("DATA_DIR")

        # Scoring weights
        for weight in [
            "WEIGHT_EXCLUSIVITY",
            "WEIGHT_REPORT_TYPE",
            "WEIGHT_PERIODICITY",
            "WEIGHT_MAXED_OUT",
            "WEIGHT_LENGTH",
            "WEIGHT_RACE_FOCUS",
        ]:
            env_val = os.getenv(weight)
            if env_val:
                self.config[weight.lower()] = float(env_val)

        # Logging
        if os.getenv("LOG_LEVEL"):
            self.config["log_level"] = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.config["log_file"] = os.getenv("LOG_FILE")

        # Web
        if os.getenv("DATASETTE_HOST"):
            self.config["datasette_host"] = os.getenv("DATASETTE_HOST")
        if os.getenv("DATASETTE_PORT"):
            self.config["datasette_port"] = int(os.getenv("DATASETTE_PORT"))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting."""
        self.config[key] = value

    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database-specific configuration.

        Returns:
            Dictionary with database connection parameters
        """
        db_type = self.config["database_type"]

        if db_type == "sqlite":
            return {
                "type": "sqlite",
                "database": self.config["sqlite_path"],
            }
        elif db_type == "mysql":
            return {
                "type": "mysql",
                "host": self.config["mysql_host"],
                "port": self.config["mysql_port"],
                "user": self.config["mysql_user"],
                "password": self.config["mysql_password"],
                "database": self.config["mysql_database"],
            }
        elif db_type == "postgresql":
            return {
                "type": "postgresql",
                "host": self.config["postgres_host"],
                "port": self.config["postgres_port"],
                "user": self.config["postgres_user"],
                "password": self.config["postgres_password"],
                "database": self.config["postgres_database"],
            }
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def get_score_weights(self) -> Dict[str, float]:
        """
        Get all scoring weights.

        Returns:
            Dictionary of score weights
        """
        return {
            "exclusivity": self.config["weight_exclusivity"],
            "report_type": self.config["weight_report_type"],
            "periodicity": self.config["weight_periodicity"],
            "maxed_out": self.config["weight_maxed_out"],
            "length": self.config["weight_length"],
            "race_focus": self.config["weight_race_focus"],
        }

    def setup_logging(self) -> None:
        """Configure logging based on settings."""
        log_level = getattr(logging, self.config["log_level"].upper())
        log_file = self.config["log_file"]

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
