import os
import pandas as pd
from .ingestion import load_data_in_chunks, optimize_dtypes
from .cleaning import clean_data
from .transformation import compute_aggregates, stream_total_revenue_by_country
from .analysis import describe_stats_numpy, z_score_filter
from .utils import log_summary
from .config import DATA_PATH, CHUNK_SIZE, REPORTS_DIR

def main():
    print("🚀 Starting customer analytics pipeline...")

    all_chunks = []

    # Step 1: Load, optimize, clean, and collect chunks
    for chunk in load_data_in_chunks(path=DATA_PATH, chunk_size=CHUNK_SIZE):
        chunk = optimize_dtypes(chunk)
        chunk = clean_data(chunk)
        log_summary(chunk, "Chunk Summary")
        all_chunks.append(chunk)

    # Step 2: Concatenate and log full cleaned dataset
    full_df = pd.concat(all_chunks, ignore_index=True)
    log_summary(full_df, "Full Dataset Summary")

    # Step 3: Save cleaned dataset
    cleaned_path = os.path.join(REPORTS_DIR, "cleaned_customer_purchases.csv")
    full_df.to_csv(cleaned_path, index=False)
    print(f"🧼 Cleaned dataset saved to {cleaned_path}")

    # Step 4: Compute and print aggregates
    aggregates = compute_aggregates(full_df)
    print("\n🔢 Aggregates by country and product category:\n", aggregates.head())

    # Step 5: Describe stats using NumPy
    stats = describe_stats_numpy(full_df["purchase_amount"])
    print("\n📊 NumPy Summary of Purchase Amounts:\n", stats)

    # Step 6: Z-score filtering (for insight, not saving)
    filtered_df = z_score_filter(full_df, "purchase_amount")
    print(f"📉 Outliers filtered (not saved): {len(full_df) - len(filtered_df)} rows removed")

    # Step 7: Stream total revenue per country while loading in chunks
    streamed_chunks = load_data_in_chunks(path=DATA_PATH, chunk_size=CHUNK_SIZE)
    total_revenue_map = stream_total_revenue_by_country(streamed_chunks)
    print("\n💰 Total revenue per country (streamed):\n", total_revenue_map)

    # Step 8: Save final aggregates report
    report_path = os.path.join(REPORTS_DIR, "summary_report.csv")
    aggregates.to_csv(report_path, index=False)
    print(f"📄 Report saved to {report_path}")

if __name__ == "__main__":
    main()
