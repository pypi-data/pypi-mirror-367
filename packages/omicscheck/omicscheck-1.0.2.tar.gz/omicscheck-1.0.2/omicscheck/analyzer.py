import pandas as pd

def analyze_expression_matrix(df: pd.DataFrame) -> dict:
    """
    Analyze the expression matrix and extract summary statistics.
    Returns a dictionary with key metrics.
    """
    result = {
        "genes": df.shape[0],
        "samples": df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "has_missing": df.isna().any().any(),
        "value_range": (float(df.min().min()), float(df.max().max())),
        "suggested_log_transform": df.max().max() > 100,  # heuristic
        "genes_as_rows": df.shape[0] > df.shape[1],
    }
    return result