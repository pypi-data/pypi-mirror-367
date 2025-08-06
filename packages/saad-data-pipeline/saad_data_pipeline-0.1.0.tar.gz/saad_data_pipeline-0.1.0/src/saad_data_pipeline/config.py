import os
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = os.getenv("DATA_PATH", "data/customer_purchases.csv")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 100_000))
REPORTS_DIR = os.getenv("REPORTS_DIR", "reports")
