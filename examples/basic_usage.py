#!/usr/bin/env python3
"""
Basic usage example for Bedfellows.

This script demonstrates:
1. Setting up the database
2. Loading FEC data
3. Computing relationship scores
4. Querying results
5. Exporting data
"""

from bedfellows import Config, DatabaseManager
from bedfellows.models import (
    init_models,
    create_all_tables,
    FecCandidates,
    FecCommittees,
    FecContributions,
    FinalScores,
)
from bedfellows.calculators import OverallCalculator
from bedfellows.exporters import JSONExporter, CSVExporter


def main():
    """Run basic usage example."""
    print("=" * 80)
    print("BEDFELLOWS BASIC USAGE EXAMPLE")
    print("=" * 80)

    # 1. Configure and initialize database
    print("\n1. Initializing database...")
    config = Config()  # Uses default SQLite database
    db_manager = DatabaseManager(config)
    db = db_manager.get_database()

    # Initialize models
    init_models(db)
    create_all_tables()

    print(f"   Database: {config['database_type']}")
    if config["database_type"] == "sqlite":
        print(f"   Location: {config['sqlite_path']}")

    # 2. Check data status
    print("\n2. Checking data status...")
    candidate_count = FecCandidates.select().count()
    committee_count = FecCommittees.select().count()
    contrib_count = FecContributions.select().count()

    print(f"   Candidates: {candidate_count:,}")
    print(f"   Committees: {committee_count:,}")
    print(f"   Contributions: {contrib_count:,}")

    if contrib_count == 0:
        print("\n   ⚠️  No data loaded!")
        print("   Use 'bedfellows load' commands to import FEC data")
        return

    # 3. Compute scores (if not already computed)
    print("\n3. Computing relationship scores...")
    score_count = FinalScores.select().count()

    if score_count == 0:
        print("   Running score computation...")
        calculator = OverallCalculator(db, {"weights": config.get_score_weights()})
        calculator.compute_scores()

        score_count = FinalScores.select().count()
        print(f"   ✓ Computed {score_count:,} relationship scores")
    else:
        print(f"   ✓ Found {score_count:,} existing scores")

    # 4. Query top scores
    print("\n4. Top 10 Relationship Scores:")
    print("   " + "-" * 76)

    top_scores = (
        FinalScores.select()
        .order_by(FinalScores.final_score.desc())
        .limit(10)
    )

    for i, score in enumerate(top_scores, 1):
        donor = score.contributor_name[:28] if score.contributor_name else "N/A"
        recipient = score.recipient_name[:28] if score.recipient_name else "N/A"
        print(f"   {i:2d}. {donor:30s} → {recipient:30s} {score.final_score:.4f}")

    print("   " + "-" * 76)

    # 5. Find specific relationships
    print("\n5. Searching for specific relationships...")
    search_term = "ACTBLUE"  # Example search

    results = (
        FinalScores.select()
        .where(
            (FinalScores.contributor_name.contains(search_term)) |
            (FinalScores.recipient_name.contains(search_term))
        )
        .order_by(FinalScores.final_score.desc())
        .limit(5)
    )

    if results:
        print(f"   Top 5 scores involving '{search_term}':")
        for i, score in enumerate(results, 1):
            print(f"   {i}. {score.contributor_name[:30]} → {score.recipient_name[:30]}")
            print(f"      Score: {score.final_score:.4f}, Count: {score.count}")
    else:
        print(f"   No results found for '{search_term}'")

    # 6. Export results
    print("\n6. Exporting results...")

    # Export top 100 to JSON
    json_exporter = JSONExporter("examples/output/top_scores.json")
    top_100 = (
        FinalScores.select()
        .order_by(FinalScores.final_score.desc())
        .limit(100)
        .dicts()
    )
    json_exporter.export(list(top_100))
    print("   ✓ Exported top 100 to examples/output/top_scores.json")

    # Export top 100 to CSV
    csv_exporter = CSVExporter("examples/output/top_scores.csv")
    csv_exporter.export(list(top_100))
    print("   ✓ Exported top 100 to examples/output/top_scores.csv")

    # 7. Database statistics
    print("\n7. Database Statistics:")
    stats = db_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    import os
    os.makedirs("examples/output", exist_ok=True)
    main()
