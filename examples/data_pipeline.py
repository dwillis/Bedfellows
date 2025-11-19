#!/usr/bin/env python3
"""
Complete data pipeline example.

This script demonstrates a complete workflow:
1. Download FEC data
2. Load into database
3. Validate data quality
4. Compute scores
5. Export results
"""

import sys
from pathlib import Path

from bedfellows import Config, DatabaseManager
from bedfellows.models import init_models, create_all_tables, FinalScores
from bedfellows.fetchers import CandidateFetcher, CommitteeFetcher, ContributionFetcher
from bedfellows.validation import validate_data
from bedfellows.calculators import OverallCalculator
from bedfellows.exporters import JSONExporter, CSVExporter, DatasetteExporter


def main():
    """Run complete data pipeline."""
    print("=" * 80)
    print("BEDFELLOWS DATA PIPELINE EXAMPLE")
    print("=" * 80)

    # Configuration
    cycle = "24"  # 2024 cycle
    config = Config()

    # Step 1: Download FEC data
    print(f"\n📥 Step 1: Downloading FEC data for cycle 20{cycle}...")
    data_dir = config["data_dir"]

    # Download candidates
    print("   Downloading candidates...")
    candidate_fetcher = CandidateFetcher(data_dir=data_dir)
    try:
        candidate_files = candidate_fetcher.fetch_candidates(cycle=cycle)
        print(f"   ✓ Downloaded {len(candidate_files)} candidate file(s)")
    except Exception as e:
        print(f"   ⚠️  Could not download candidates: {e}")
        candidate_files = []

    # Download committees
    print("   Downloading committees...")
    committee_fetcher = CommitteeFetcher(data_dir=data_dir)
    try:
        committee_files = committee_fetcher.fetch_committees(cycle=cycle)
        print(f"   ✓ Downloaded {len(committee_files)} committee file(s)")
    except Exception as e:
        print(f"   ⚠️  Could not download committees: {e}")
        committee_files = []

    # Download contributions
    print("   Downloading contributions...")
    contrib_fetcher = ContributionFetcher(data_dir=data_dir)
    try:
        contrib_files = contrib_fetcher.fetch_contributions(cycle)
        print(f"   ✓ Downloaded {len(contrib_files)} contribution file(s)")
    except Exception as e:
        print(f"   ⚠️  Could not download contributions: {e}")
        contrib_files = []

    # Step 2: Initialize database
    print("\n🗄️  Step 2: Initializing database...")
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()
    init_models(db)
    create_all_tables()
    print("   ✓ Database initialized")

    # Step 3: Load data (if files were downloaded)
    print("\n📊 Step 3: Loading data into database...")
    if candidate_files or committee_files or contrib_files:
        print("   Note: Use 'bedfellows load' commands to import downloaded files")
        print("   Example:")
        for f in (candidate_files + committee_files + contrib_files)[:3]:
            print(f"     bedfellows load ... {f}")
    else:
        print("   ⚠️  No new files to load (download may have failed or files already exist)")

    # Step 4: Validate data
    print("\n✅ Step 4: Validating data quality...")
    validation_results = validate_data(db)

    if not validation_results["valid"]:
        print("   ⚠️  Data validation found errors!")
        print("   Please review the validation report above")

        # Ask if we should continue
        if input("\n   Continue anyway? (y/n): ").lower() != "y":
            print("   Stopping pipeline")
            return

    # Step 5: Compute scores
    print("\n🔢 Step 5: Computing relationship scores...")
    score_count = FinalScores.select().count()

    if score_count > 0:
        print(f"   Found {score_count:,} existing scores")
        recalculate = input("   Recalculate? (y/n): ").lower() == "y"
        if not recalculate:
            print("   Skipping calculation")
        else:
            print("   Recalculating scores...")
            calculator = OverallCalculator(db, {"weights": config.get_score_weights()})
            calculator.compute_scores()
    else:
        print("   Computing scores for the first time...")
        calculator = OverallCalculator(db, {"weights": config.get_score_weights()})
        calculator.compute_scores()

    # Step 6: Export results
    print("\n📤 Step 6: Exporting results...")

    # Create output directory
    output_dir = Path("examples/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export top 1000 to JSON
    print("   Exporting to JSON...")
    json_exporter = JSONExporter(output_dir / "results.json")
    top_results = list(
        FinalScores.select()
        .order_by(FinalScores.final_score.desc())
        .limit(1000)
        .dicts()
    )
    json_exporter.export(top_results)
    print(f"   ✓ Exported {len(top_results)} records to results.json")

    # Export to CSV
    print("   Exporting to CSV...")
    csv_exporter = CSVExporter(output_dir / "results.csv")
    csv_exporter.export(top_results)
    print(f"   ✓ Exported {len(top_results)} records to results.csv")

    # Step 7: Launch web interface (optional)
    print("\n🌐 Step 7: Web interface...")
    print("   To explore data interactively, run:")
    print("   bedfellows serve")
    print()
    print("   Or launch now? (y/n):", end=" ")
    if input().lower() == "y":
        print("   Launching Datasette...")
        try:
            datasette_exporter = DatasetteExporter(config["sqlite_path"])
            datasette_exporter.create_metadata()
            datasette_exporter.launch_datasette(open_browser=True)
        except Exception as e:
            print(f"   ⚠️  Could not launch Datasette: {e}")

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
