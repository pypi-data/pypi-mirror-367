from collections import defaultdict

def compute_aggregates(df):
    grouped = df.groupby(["country_code", "product_category"]).agg({
        "purchase_amount": ["sum", "mean"],
        "customer_id": "nunique"
    }).reset_index()
    grouped.columns = ["country", "category", "total_revenue", "avg_basket", "unique_customers"]
    return grouped

def stream_total_revenue_by_country(chunks):
    revenue_map = defaultdict(float)
    for chunk in chunks:
        chunk = chunk[chunk["purchase_amount"] >= 0]
        chunk_revenue = chunk.groupby("country_code")["purchase_amount"].sum()
        for country, rev in chunk_revenue.items():
            revenue_map[country] += rev
    return dict(revenue_map)
