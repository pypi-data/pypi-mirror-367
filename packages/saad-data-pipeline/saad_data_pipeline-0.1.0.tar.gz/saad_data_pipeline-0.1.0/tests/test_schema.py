import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

schema = DataFrameSchema({
    "customer_id": Column(int, Check.gt(0)),
    "purchase_id": Column(str),
    "product_category": Column(str),
    "purchase_amount": Column(float, Check.ge(0)),
    "purchase_date": Column(pa.DateTime),
    "country_code": Column(str, Check.isin(["US", "FR", "DE", "MA", "ES", "UK", "IN", "JP"])),
    "customer_age": Column(int, Check.ge(10)),
    "payment_type": Column(str),
})

def test_schema_validates(sample_df):
    schema.validate(sample_df)
