import pandas as pd
from src.saad_data_pipeline.cleaning import clean_data

def test_clean_data():
    df = pd.DataFrame({
        "customer_id": [1, 2, 2],
        "purchase_id": ["p1", "p2", "p2"],
        "product_category": ["books", "tech", "tech"],
        "purchase_amount": [-50.0, 100.0, 100.0],
        "purchase_date": pd.to_datetime(["2021-01-01"] * 3),
        "country_code": ["US", "US", "US"],
        "customer_age": [8, 30, 30],
        "payment_type": ["card", "paypal", "paypal"]
    })
    cleaned = clean_data(df)
    assert cleaned.shape[0] == 1
    assert cleaned["purchase_amount"].min() >= 0
    assert cleaned["customer_age"].min() >= 10
