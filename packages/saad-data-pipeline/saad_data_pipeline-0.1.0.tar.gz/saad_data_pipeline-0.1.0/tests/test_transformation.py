import pandas as pd
from src.saad_data_pipeline.transformation import compute_aggregates

def test_compute_aggregates():
    df = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "product_category": ["books", "books", "tech", "tech"],
        "purchase_amount": [100.0, 150.0, 200.0, 300.0],
        "country_code": ["US", "US", "FR", "FR"]
    })

    result = compute_aggregates(df)
    assert "total_revenue" in result.columns
    assert "avg_basket" in result.columns
    assert "unique_customers" in result.columns
    assert result.shape[0] == 2  # one per country/product combo
