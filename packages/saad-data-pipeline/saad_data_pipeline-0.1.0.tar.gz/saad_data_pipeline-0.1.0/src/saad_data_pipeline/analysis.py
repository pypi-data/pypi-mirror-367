import numpy as np

def describe_stats_numpy(values):
    return {
        "mean": np.mean(values),
        "std": np.std(values),
        "25%": np.percentile(values, 25),
        "75%": np.percentile(values, 75),
    }

def z_score_filter(df, column):
    z_scores = (df[column] - df[column].mean()) / df[column].std()
    return df[np.abs(z_scores) < 3]
