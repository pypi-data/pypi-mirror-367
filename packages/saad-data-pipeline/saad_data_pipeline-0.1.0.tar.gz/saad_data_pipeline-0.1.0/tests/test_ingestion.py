import pandas as pd
from src.saad_data_pipeline.ingestion import optimize_dtypes

def test_optimize_dtypes():
    df = pd.DataFrame({
        "purchase_amount": [100.5, 200.3, 150.0],
        "customer_age": [25, 35, 45]
    })
    optimized = optimize_dtypes(df)

    assert optimized["purchase_amount"].dtype == "float32"
    assert str(optimized["customer_age"].dtype).startswith("int")

