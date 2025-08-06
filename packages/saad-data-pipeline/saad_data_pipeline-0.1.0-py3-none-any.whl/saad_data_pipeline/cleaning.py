import pandas as pd

def clean_data(df: pd.DataFrame):
    df = df.drop_duplicates()
    df = df.dropna()
    df = df[df["customer_age"] >= 10]
    df = df[df["purchase_amount"] >= 0]
    return df
