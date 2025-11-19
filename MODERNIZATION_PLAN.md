# Bedfellows Modernization Plan

## Overview
This document outlines the modernization strategy for the Bedfellows FEC campaign finance analysis tool, transforming it into a robust, Python 3-only, object-oriented application with multiple output formats and database backend support.

## Goals

### 1. Python 3 Only
- Remove all Python 2 compatibility code
- Update all dependencies to modern, actively maintained versions
- Use modern Python 3 features (type hints, f-strings, pathlib, etc.)

### 2. Robust & Object-Oriented Architecture
- Complete ORM migration from raw SQL to Peewee
- Implement proper separation of concerns
- Add comprehensive error handling and logging
- Configuration management via environment variables and config files
- Modular design with clear class responsibilities

### 3. Flexible Database Backend
- **Primary**: SQLite (zero-configuration, portable, perfect for local analysis)
- **Optional**: MySQL, PostgreSQL (for production deployments)
- Database-agnostic code using Peewee ORM
- Connection pooling and proper resource management

### 4. Multiple Output Formats
- **JSON**: Machine-readable, API-friendly
- **CSV**: Spreadsheet-compatible, data journalism standard
- **Web Interface**: Interactive data exploration via Datasette
- Exporters as pluggable modules

### 5. FEC Data Integration
- Automated data fetcher from fec.gov bulk data
- Support for candidate, committee, and contribution files
- Data validation against FEC data dictionaries
- Incremental updates

## Architecture

### New Directory Structure
```
bedfellows/
├── bedfellows/              # Main package
│   ├── __init__.py
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection & backend abstraction
│   ├── models.py            # ORM models (refactored)
│   ├── fetchers/            # FEC data downloaders
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── candidates.py
│   │   ├── committees.py
│   │   └── contributions.py
│   ├── calculators/         # Score calculation engines
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── overall.py
│   │   └── by_cycle.py
│   ├── exporters/           # Output format handlers
│   │   ├── __init__.py
│   │   ├── json.py
│   │   ├── csv.py
│   │   └── datasette.py
│   ├── web/                 # Web interface
│   │   ├── __init__.py
│   │   └── app.py
│   └── cli.py               # Command-line interface
├── data/                    # Data directory
│   ├── csv/                 # Reference CSV files
│   └── downloads/           # Downloaded FEC data
├── tests/                   # Test suite
├── config.example.ini       # Example configuration
├── .env.example             # Example environment variables
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── setup.py                 # Package setup
└── README.md               # Updated documentation
```

### Key Components

#### 1. Configuration System (`config.py`)
```python
class Config:
    - Database settings (type, connection params)
    - FEC data sources
    - Export options
    - Score calculation weights
    - Logging configuration

    Load order:
    1. Default values
    2. Config file (.ini or .yaml)
    3. Environment variables (highest priority)
```

#### 2. Database Abstraction (`database.py`)
```python
class DatabaseManager:
    - get_database() -> Database
    - init_tables()
    - migrate_schema()
    - get_stats()

Supported backends:
    - SQLite (default)
    - MySQL
    - PostgreSQL
```

#### 3. Data Fetchers (`fetchers/`)
```python
class BaseFetcher:
    - download()
    - validate()
    - import_to_db()

class CandidateFetcher(BaseFetcher):
class CommitteeFetcher(BaseFetcher):
class ContributionFetcher(BaseFetcher):
```

#### 4. Score Calculators (`calculators/`)
```python
class BaseCalculator:
    - setup()
    - compute_scores()
    - get_results()

class OverallCalculator(BaseCalculator):
    - Analyzes across all cycles

class ByCycleCalculator(BaseCalculator):
    - Analyzes individual cycles
```

#### 5. Exporters (`exporters/`)
```python
class BaseExporter:
    - export(results, output_path)

class JSONExporter(BaseExporter):
class CSVExporter(BaseExporter):
class DatasetteExporter(BaseExporter):
    - Generates Datasette-compatible SQLite
    - Creates metadata.json
    - Optional: launches Datasette server
```

## Implementation Phases

### Phase 1: Foundation (Current Focus)
- [x] Analyze existing codebase
- [ ] Update dependencies
- [ ] Create configuration system
- [ ] Refactor database connection management
- [ ] Add logging infrastructure

### Phase 2: ORM Migration
- [ ] Complete models.py refactoring
- [ ] Convert overall.py to ORM
- [ ] Convert groupedbycycle.py to ORM
- [ ] Remove raw SQL queries
- [ ] Add database migration support

### Phase 3: Data Integration
- [ ] Implement FEC data fetchers
- [ ] Add data validation
- [ ] Support incremental updates
- [ ] Document data refresh process

### Phase 4: Export Functionality
- [ ] JSON exporter
- [ ] CSV exporter
- [ ] Datasette integration
- [ ] Export API in CLI

### Phase 5: Web Interface
- [ ] Set up Datasette
- [ ] Custom metadata configuration
- [ ] Optional Flask/FastAPI dashboard
- [ ] Visualization templates

### Phase 6: Testing & Documentation
- [ ] Unit tests for all modules
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] User documentation
- [ ] Developer documentation

## Technology Stack

### Core Dependencies
- **Python**: 3.8+ (for type hints, walrus operator, etc.)
- **ORM**: Peewee 3.17+ (lightweight, supports all backends)
- **Database**: SQLite 3 (primary), MySQL 8+, PostgreSQL 13+ (optional)
- **CLI**: Click 8.0+ (modern argument parsing)
- **Config**: python-dotenv, configparser
- **Logging**: Python standard logging with optional Rich for pretty output
- **Progress**: tqdm or Rich
- **HTTP**: requests or httpx for FEC data downloads

### Data Analysis
- **pandas**: 2.0+ (modern data manipulation)
- **numpy**: 1.24+
- **scipy**: 1.10+

### Web & Export
- **Datasette**: Latest (for web interface)
- **datasette-export**: For additional export formats
- **Flask** or **FastAPI**: (optional, for custom endpoints)

### Development
- **pytest**: Testing
- **black**: Code formatting
- **mypy**: Type checking
- **ruff**: Linting

## Migration Strategy

### Backward Compatibility
- Keep existing CLI commands working
- Support existing MySQL databases (don't force migration)
- Provide migration script: `python -m bedfellows migrate`

### Data Migration
```bash
# Export from MySQL
python -m bedfellows export --from mysql://localhost/fec --to data/fec.db

# Import to SQLite
python -m bedfellows import --from data/fec.db
```

### Configuration Migration
```bash
# Generate config from current hardcoded values
python -m bedfellows init-config
```

## Success Criteria

1. ✅ **Python 3 Only**: No Python 2 compatibility code remains
2. ✅ **ORM Complete**: No raw SQL queries in calculation code
3. ✅ **SQLite Works**: Can run full analysis on SQLite database
4. ✅ **Export Formats**: Can export to JSON, CSV, and Datasette
5. ✅ **Configuration**: Database and options configurable via env vars or config file
6. ✅ **Documentation**: Updated README with new features
7. ✅ **FEC Integration**: Can download and import current FEC data
8. ✅ **Web Interface**: Datasette running with custom metadata
9. ✅ **Robust**: Comprehensive error handling and logging
10. ✅ **Tested**: Core functionality has test coverage

## Timeline Estimate
- Foundation: 2-4 hours
- ORM Migration: 4-6 hours
- Data Integration: 3-4 hours
- Export & Web: 2-3 hours
- Testing & Documentation: 2-3 hours

**Total**: 13-20 hours of development

## Notes
- Maintain git history for all changes
- Use feature branches for major refactoring
- Document breaking changes in CHANGELOG.md
- Keep original code as reference during migration
