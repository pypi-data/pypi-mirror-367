import gzip
import pandas as pd
from io import BytesIO

def parse_series_matrix(buffer: BytesIO) -> pd.DataFrame:
    """
    Parses a GEO .gz matrix file and extracts the gene expression matrix
    between the !series_matrix_table_begin and _end markers.
    """
    with gzip.open(buffer, 'rt') as f:
        lines = f.readlines()

    # Locate table markers
    start = next(i for i, line in enumerate(lines) if line.startswith("!series_matrix_table_begin")) + 1
    end = next(i for i, line in enumerate(lines) if line.startswith("!series_matrix_table_end"))
    data_lines = lines[start:end]

    # Create a temporary buffer to read with pandas
    from io import StringIO
    data_str = "".join(data_lines)
    df = pd.read_csv(StringIO(data_str), sep='\t')

    # Set ID_REF as index
    df.set_index(df.columns[0], inplace=True)

    # Convert all other columns to numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # Drop rows and columns that are completely empty
    df.dropna(axis=0, how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    return df
