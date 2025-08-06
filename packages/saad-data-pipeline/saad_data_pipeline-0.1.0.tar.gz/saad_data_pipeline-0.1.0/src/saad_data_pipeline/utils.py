import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_summary(df, label="Data Summary"):
    logging.info(f"{label}:\n{df.describe(include='all')}")
