import pandas as pd
from .config import DATA_PATH, CHUNK_SIZE

def load_data_in_chunks(path=DATA_PATH, chunk_size=CHUNK_SIZE, dtype_map=None):
    chunks = pd.read_csv(path, chunksize=chunk_size, dtype=dtype_map, parse_dates=["purchase_date"])
    for chunk in chunks:
        yield chunk

def optimize_dtypes(df):
    df["purchase_amount"] = pd.to_numeric(df["purchase_amount"], downcast="float")
    df["customer_age"] = pd.to_numeric(df["customer_age"], downcast="integer")
    return df
