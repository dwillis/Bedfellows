"""
Database abstraction layer for Bedfellows.

Provides unified interface for SQLite, MySQL, and PostgreSQL databases
using Peewee ORM.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from peewee import (
    Database,
    SqliteDatabase,
    MySQLDatabase,
    PostgresqlDatabase,
    Model,
)

from bedfellows.config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and initialization."""

    def __init__(self, config: Config):
        """
        Initialize database manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self._database: Optional[Database] = None

    def get_database(self) -> Database:
        """
        Get database instance.

        Returns:
            Peewee database instance

        Raises:
            ValueError: If database type is unsupported
        """
        if self._database is not None:
            return self._database

        db_config = self.config.get_database_config()
        db_type = db_config["type"]

        if db_type == "sqlite":
            # Ensure directory exists
            db_path = Path(db_config["database"])
            db_path.parent.mkdir(parents=True, exist_ok=True)

            self._database = SqliteDatabase(
                db_config["database"],
                pragmas={
                    "journal_mode": "wal",  # Write-Ahead Logging for better concurrency
                    "cache_size": -1024 * 64,  # 64MB cache
                    "foreign_keys": 1,  # Enable foreign key constraints
                    "ignore_check_constraints": 0,
                    "synchronous": 0,  # Faster writes (safe with WAL)
                },
            )
            logger.info(f"Initialized SQLite database: {db_config['database']}")

        elif db_type == "mysql":
            self._database = MySQLDatabase(
                db_config["database"],
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
                charset="utf8mb4",
            )
            logger.info(
                f"Initialized MySQL database: {db_config['user']}@{db_config['host']}/{db_config['database']}"
            )

        elif db_type == "postgresql":
            self._database = PostgresqlDatabase(
                db_config["database"],
                host=db_config["host"],
                port=db_config["port"],
                user=db_config["user"],
                password=db_config["password"],
            )
            logger.info(
                f"Initialized PostgreSQL database: {db_config['user']}@{db_config['host']}/{db_config['database']}"
            )

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        return self._database

    def init_tables(self, models: list) -> None:
        """
        Initialize database tables for given models.

        Args:
            models: List of Peewee model classes
        """
        db = self.get_database()
        db.connect(reuse_if_open=True)

        try:
            # Create tables
            db.create_tables(models, safe=True)
            logger.info(f"Initialized {len(models)} tables")

            # Log table names
            table_names = [model._meta.table_name for model in models]
            logger.debug(f"Tables: {', '.join(table_names)}")

        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
            raise
        finally:
            if not db.is_closed():
                db.close()

    def drop_tables(self, models: list, safe: bool = True) -> None:
        """
        Drop database tables for given models.

        Args:
            models: List of Peewee model classes
            safe: If True, don't raise error if table doesn't exist
        """
        db = self.get_database()
        db.connect(reuse_if_open=True)

        try:
            db.drop_tables(models, safe=safe)
            logger.info(f"Dropped {len(models)} tables")
        except Exception as e:
            logger.error(f"Error dropping tables: {e}")
            raise
        finally:
            if not db.is_closed():
                db.close()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        db = self.get_database()
        db_type = self.config["database_type"]

        stats = {
            "type": db_type,
            "connected": not db.is_closed(),
        }

        if db_type == "sqlite":
            stats["path"] = self.config["sqlite_path"]
            # Get file size if it exists
            db_path = Path(self.config["sqlite_path"])
            if db_path.exists():
                stats["size_bytes"] = db_path.stat().st_size
                stats["size_mb"] = round(db_path.stat().st_size / (1024 * 1024), 2)
        elif db_type == "mysql":
            stats["host"] = self.config["mysql_host"]
            stats["database"] = self.config["mysql_database"]
        elif db_type == "postgresql":
            stats["host"] = self.config["postgres_host"]
            stats["database"] = self.config["postgres_database"]

        return stats

    def execute_sql(self, sql: str, params: Optional[tuple] = None) -> Any:
        """
        Execute raw SQL query.

        Args:
            sql: SQL query string
            params: Query parameters

        Returns:
            Query cursor
        """
        db = self.get_database()
        db.connect(reuse_if_open=True)

        try:
            cursor = db.execute_sql(sql, params)
            return cursor
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            logger.debug(f"SQL: {sql}")
            raise

    def close(self) -> None:
        """Close database connection."""
        if self._database and not self._database.is_closed():
            self._database.close()
            logger.debug("Closed database connection")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()


# Singleton database instance (will be initialized by models)
_database_instance: Optional[Database] = None


def init_database(config: Config) -> Database:
    """
    Initialize global database instance.

    Args:
        config: Configuration object

    Returns:
        Database instance
    """
    global _database_instance

    if _database_instance is None:
        manager = DatabaseManager(config)
        _database_instance = manager.get_database()
        logger.info("Initialized global database instance")

    return _database_instance


def get_database_instance() -> Database:
    """
    Get global database instance.

    Returns:
        Database instance

    Raises:
        RuntimeError: If database not initialized
    """
    if _database_instance is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")

    return _database_instance
