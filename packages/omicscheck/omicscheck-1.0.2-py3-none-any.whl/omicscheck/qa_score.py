# qa_score.py
import numpy as np
import pandas as pd

def evaluate_study(df: pd.DataFrame) -> dict:
    result = {}

    result['num_genes'] = df.shape[0]
    result['num_samples'] = df.shape[1]

    total = df.size
    missing = df.isna().sum().sum()
    missing_rate = missing / total if total > 0 else 0
    result['missing_rate'] = round(missing_rate, 4)

    flat_vals = df.values.flatten()
    finite_vals = flat_vals[np.isfinite(flat_vals)]
    if len(finite_vals) > 0:
        result['max_value'] = float(np.nanmax(finite_vals))
        result['min_value'] = float(np.nanmin(finite_vals))
        result['skewness'] = float(pd.Series(finite_vals).skew(skipna=True))
    else:
        result['max_value'] = None
        result['min_value'] = None
        result['skewness'] = None

    result['needs_log2'] = result['max_value'] is not None and result['max_value'] > 1000

    result['orientation'] = 'genes_as_rows' if df.shape[0] > df.shape[1] else 'genes_as_columns'

    score = 5
    if missing_rate > 0.05:
        score -= 1
    if result['num_samples'] < 5:
        score -= 1
    if result['skewness'] is not None and abs(result['skewness']) > 2:
        score -= 1
    if result['needs_log2']:
        score -= 0.5
    result['qa_score'] = round(max(score, 0), 2)

    if score >= 4.5:
        rating = 'Excellent'
    elif score >= 3.5:
        rating = 'Good'
    elif score >= 2.5:
        rating = 'Fair'
    else:
        rating = 'Poor'
    result['rating'] = rating

    result = {
        "QA Score": result['qa_score'],
        "Rating": result['rating'],
        "Missing Rate": result['missing_rate'],
        "Skewness": result['skewness'],
        "Needs Log2": result['needs_log2'],
        "Orientation": result['orientation'],
        "Num Genes": result['num_genes'],
        "Num Samples": result['num_samples'],
        "Max Value": result['max_value'],
        "Min Value": result['min_value'],
    }

    return result
