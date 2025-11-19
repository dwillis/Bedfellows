# Bedfellows Examples

This directory contains example scripts demonstrating various Bedfellows features.

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates fundamental operations:
- Initializing the database
- Checking data status
- Computing relationship scores
- Querying results
- Exporting to JSON and CSV

```bash
python examples/basic_usage.py
```

**Prerequisites**: Data must be loaded into the database first.

### 2. Complete Data Pipeline (`data_pipeline.py`)

Shows a complete end-to-end workflow:
- Downloading FEC data from fec.gov
- Loading data into database
- Validating data quality
- Computing relationship scores
- Exporting results in multiple formats
- (Optional) Launching web interface

```bash
python examples/data_pipeline.py
```

**Note**: This script will attempt to download data from the FEC, which may take some time.

## Output

Both examples create an `output/` subdirectory with exported results:
- `top_scores.json` - Top relationship scores in JSON format
- `top_scores.csv` - Top relationship scores in CSV format
- `results.json` - Full results set in JSON format
- `results.csv` - Full results set in CSV format

## Running Examples

1. **Set up your environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Bedfellows
   pip install -e .
   ```

2. **Run an example**:
   ```bash
   python examples/basic_usage.py
   ```

3. **Customize examples**:
   - Modify the search terms
   - Change export limits
   - Adjust score weights in configuration
   - Use different database backends

## Troubleshooting

### "No data loaded"
If you see this message, you need to load FEC data first:
```bash
bedfellows init
bedfellows fetch candidates --cycle 2024
bedfellows fetch committees --cycle 2024
bedfellows fetch contributions 2024

# Then load the downloaded files
bedfellows load candidates data/downloads/cn.txt
bedfellows load committees data/downloads/cm.txt
bedfellows load contributions data/downloads/itpas2_24.txt
```

### "No scores found"
Compute scores first:
```bash
bedfellows compute
```

### Database locked errors
If using SQLite with multiple processes, you may encounter database locked errors. Use MySQL or PostgreSQL for concurrent access, or run operations sequentially.

## Further Reading

- See `README.md` in the project root for complete documentation
- See `MODERNIZATION_PLAN.md` for architecture details
- See `introduction.md` for methodology details
