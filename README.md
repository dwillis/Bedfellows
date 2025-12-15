# Bedfellows

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Modern Python 3 tool for analyzing Federal Election Commission campaign finance relationships**

Bedfellows analyzes FEC data on political action committee contributions to calculate relationship scores between donors and recipients. It measures the strength and characteristics of these relationships across six dimensions: exclusivity, timing, periodicity, contribution limits, relationship length, and geographic focus.

Originally developed by Nikolas Iubel during an internship with the Interactive News team at The New York Times, and edited by Derek Willis. **Now modernized for Python 3** with SQLite support, multiple export formats, and a web interface.

---

## What's New in Version 2.0

🎉 **Major Modernization**:
- ✅ **Python 3.12+** - Fully modern Python with no legacy code
- ✅ **SQLite by default** - No database server required (MySQL and PostgreSQL still supported)
- ✅ **Multiple export formats** - JSON, CSV, and interactive web interface via Datasette
- ✅ **FEC data fetcher** - Automatically download data from fec.gov
- ✅ **Modern CLI** - User-friendly command-line interface with Click
- ✅ **ORM-based** - Clean, maintainable code using Peewee ORM
- ✅ **Configuration management** - Environment variables and config files
- ✅ **Better error handling** - Comprehensive logging and error messages

---

## Features

### Six Relationship Metrics

Bedfellows computes six scores for each donor-recipient pair:

1. **Exclusivity**: How much of a donor's budget goes to this recipient
2. **Report Type**: When donations occur relative to election cycles (early support indicates stronger commitment)
3. **Periodicity**: How regular and predictable the donation pattern is
4. **Maxed Out**: How close donations come to legal contribution limits
5. **Length**: Duration of the donor-recipient relationship
6. **Race Focus**: Geographic concentration of support

These are combined into a **final relationship score** (0-1 scale) that quantifies the strength of the donor-recipient relationship.

### Data Sources

- **FEC Candidate Master File** - Information about federal candidates
- **FEC Committee Master File** - Information about PACs and committees
- **Committee Contributions** - Transaction data between committees
- Built-in reference data for contribution limits, super PAC exclusions, and score weights

---

## Installation

### Requirements
- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv)
- (Optional) MySQL 8+ or PostgreSQL 13+ if not using SQLite

### Quick Start with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/dwillis/Bedfellows.git
cd Bedfellows

# Initialize uv project and install dependencies
uv sync
```

### Alternative: Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Bedfellows
pip install -e .
```

### Optional: MySQL or PostgreSQL Support

```bash
# For MySQL
uv add pymysql cryptography

# For PostgreSQL
uv add psycopg2-binary
```

---

## Quick Start Guide

### 1. Initialize Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env to customize settings (optional - defaults to SQLite)
# DATABASE_TYPE=sqlite
# SQLITE_PATH=data/bedfellows.db
```

### 2. Initialize Database

```bash
# Create database and tables
bedfellows init
```

### 3. Download FEC Data

```bash
# Download candidate data
bedfellows fetch candidates --cycle 2026

# Download committee data
bedfellows fetch committees --cycle 2026

# Download contribution data
bedfellows fetch contributions 2026
```

### 4. Load Data

```bash
# Load downloaded data into database
bedfellows load candidates data/cn.txt
bedfellows load committees data/cm.txt
bedfellows load contributions data/itpas2.txt
```

### 5. Explore with Web Interface

```bash
# Launch Datasette for interactive exploration
bedfellows serve
```

This opens your browser to an interactive interface where you can:
- Browse all tables
- Run SQL queries
- Export results
- Create custom views
- Share URLs to specific queries

---

## Usage

### Command-Line Interface

```bash
# Show all commands
bedfellows --help

# Initialize database
bedfellows init

# Download FEC data
bedfellows fetch candidates --cycle 2024
bedfellows fetch committees --all
bedfellows fetch contributions 2024

# Load data
bedfellows load candidates data/cn.txt
bedfellows load committees data/cm.txt
bedfellows load contributions data/pas2_24.txt

# Export results
bedfellows export json results.json --table final_scores
bedfellows export csv results.csv --table final_scores --limit 1000

# Launch web interface
bedfellows serve --port 8001

# Check database status
bedfellows status

# View configuration
bedfellows info
```

### Python API

```python
from bedfellows import Config, DatabaseManager
from bedfellows.models import init_models, FinalScores
from bedfellows.exporters import JSONExporter

# Load configuration
config = Config()

# Initialize database
db_manager = DatabaseManager(config)
db = db_manager.get_database()
init_models(db)

# Query results
top_scores = FinalScores.select().order_by(FinalScores.final_score.desc()).limit(10)

for score in top_scores:
    print(f"{score.contributor_name} → {score.recipient_name}: {score.final_score:.3f}")

# Export to JSON
exporter = JSONExporter("top_scores.json")
exporter.export_model(FinalScores, limit=100)
```

---

## Configuration

### Environment Variables

Create a `.env` file (or set environment variables):

```bash
# Database Configuration
DATABASE_TYPE=sqlite              # sqlite, mysql, or postgresql
SQLITE_PATH=data/bedfellows.db

# MySQL (if used)
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=password
# MYSQL_DATABASE=fec

# PostgreSQL (if used)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=password
# POSTGRES_DATABASE=fec

# FEC Data
FEC_BULK_DATA_URL=https://www.fec.gov/files/bulk-downloads/
DATA_DIR=data

# Score Weights (optional - defaults to 1.0 for all)
WEIGHT_EXCLUSIVITY=1.0
WEIGHT_REPORT_TYPE=1.0
WEIGHT_PERIODICITY=1.0
WEIGHT_MAXED_OUT=1.0
WEIGHT_LENGTH=1.0
WEIGHT_RACE_FOCUS=1.0

# Web Interface
DATASETTE_PORT=8001
DATASETTE_HOST=127.0.0.1

# Logging
LOG_LEVEL=INFO
LOG_FILE=bedfellows.log
```

### Configuration File

Alternatively, use `config.ini`:

```ini
[database]
type = sqlite
sqlite_path = data/bedfellows.db

[fec]
bulk_data_url = https://www.fec.gov/files/bulk-downloads/
data_dir = data

[scoring]
weight_exclusivity = 1.0
weight_report_type = 1.0
weight_periodicity = 1.0
weight_maxed_out = 1.0
weight_length = 1.0
weight_race_focus = 1.0

[logging]
level = INFO
file = bedfellows.log

[web]
port = 8001
host = 127.0.0.1
```

---

## FEC Data Sources

### Bulk Data Downloads

Bedfellows can automatically download data from the FEC:
- **Bulk Data URL**: https://www.fec.gov/files/bulk-downloads/
- **Browse Data**: https://www.fec.gov/data/browse-data/?tab=bulk-data

### Data Dictionaries

- **Candidates**: https://www.fec.gov/campaign-finance-data/candidate-master-file-description/
- **Committees**: https://www.fec.gov/campaign-finance-data/committee-master-file-description/
- **Contributions**: https://www.fec.gov/campaign-finance-data/contributions-committees-candidates-file-description/

### Pre-processed Data (Legacy)

If you prefer, you can use pre-processed CSV files for cycles 2006-2018:
- [fec_candidates](https://pp-data.s3.amazonaws.com/fec_candidates.csv.zip) (zipped)
- [fec_committees](https://pp-data.s3.amazonaws.com/fec_committees.csv.zip) (zipped)
- [fec_committee_contributions](https://pp-data.s3.amazonaws.com/fec_committee_contributions.csv.zip) (zipped)

---

## Export Formats

### JSON

```bash
# Export to JSON
bedfellows export json results.json --table final_scores

# Result structure:
{
  "metadata": {
    "exported_at": "2024-01-15T10:30:00",
    "record_count": 1000,
    "table_name": "final_scores"
  },
  "data": [
    {
      "fec_committee_id": "C00401224",
      "contributor_name": "ACTBLUE",
      "other_id": "H0CA53197",
      "recipient_name": "PETERS, SCOTT FOR CONGRESS",
      "final_score": 0.87,
      ...
    }
  ]
}
```

### CSV

```bash
# Export to CSV
bedfellows export csv results.csv --table final_scores --limit 5000
```

### Datasette Web Interface

```bash
# Launch interactive web interface
bedfellows serve

# Then visit http://localhost:8001 in your browser
```

Features:
- Browse all tables
- Run SQL queries
- Filter and sort data
- Export query results
- Create shareable URLs
- JSON API endpoints

---

## Architecture

### Database Backends

| Backend | When to Use | Pros | Cons |
|---------|-------------|------|------|
| **SQLite** (default) | Local analysis, single user | No setup, portable, fast for small datasets | Not for concurrent writes |
| **MySQL** | Production, multi-user | Robust, proven, good tooling | Requires server setup |
| **PostgreSQL** | Advanced queries, JSON support | Most features, best for complex analytics | Requires server setup |

### Project Structure

```
bedfellows/
├── bedfellows/              # Main package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── database.py         # Database abstraction
│   ├── models.py           # ORM models (Peewee)
│   ├── calculators/        # Score calculation (future)
│   ├── exporters/          # Export modules
│   │   ├── json_exporter.py
│   │   ├── csv_exporter.py
│   │   └── datasette_exporter.py
│   └── fetchers/           # FEC data downloaders
│       ├── candidates.py
│       ├── committees.py
│       └── contributions.py
├── data/                   # Data directory
│   ├── csv/               # Reference CSV files
│   └── downloads/         # Downloaded FEC data
├── tests/                 # Test suite
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md            # This file
```

---

## Development

### Running Tests

```bash
# Install development dependencies
uv add --dev pytest pytest-cov pytest-mock black ruff mypy

# Run tests
uv run pytest

# With coverage
pytest --cov=bedfellows
```

### Code Quality

```bash
# Format code
uv run black bedfellows/

# Lint
uv run ruff bedfellows/

# Type check
uv run mypy bedfellows/
```

---

## Migration from Version 1.x

If you're upgrading from the original Bedfellows:

### Key Changes

1. **Database**: MySQL is optional now; SQLite is the default
2. **Python**: Requires Python 3.12+ (no Python 2 support)
3. **CLI**: New command structure (see Usage above)
4. **Configuration**: Use `.env` or `config.ini` instead of hardcoded values

### Migration Steps

```bash
# 1. Back up your existing MySQL database
mysqldump fec > fec_backup.sql

# 2. Install new version
uv sync

# 3. Initialize new database (SQLite)
uv run bedfellows init

# 4. (Optional) Export existing data and reimport
# Or continue using MySQL by setting DATABASE_TYPE=mysql in .env

# 5. Update your scripts to use new CLI
# Old: python main.py overall fec
# New: bedfellows compute overall
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## License

MIT License - see LICENSE file for details

---

## Credits

### Original Development
- **Nikolas Iubel** - Original developer (NYT Interactive News internship)
- **Derek Willis** - Editor (The New York Times)

### Version 2.0 Modernization
- Python 3 migration and OOP refactoring
- SQLite and Datasette integration
- Modern CLI and export functionality

### Data Source
- **Federal Election Commission** - https://www.fec.gov/

---

## Support

- **Issues**: https://github.com/dwillis/Bedfellows/issues
- **Documentation**: See `introduction.md` for detailed methodology
- **FEC Data**: https://www.fec.gov/data/

---

## Methodology

For a detailed explanation of the scoring methodology, see [introduction.md](introduction.md).

### Quick Summary

Bedfellows identifies strong donor-recipient relationships by analyzing:
- How exclusively a donor supports a recipient
- When donations occur in the election cycle
- How regular the donation pattern is
- How close donations come to legal limits
- How long the relationship has existed
- How geographically focused the support is

These metrics are normalized and combined to produce a final score between 0 and 1, where higher scores indicate stronger relationships.
