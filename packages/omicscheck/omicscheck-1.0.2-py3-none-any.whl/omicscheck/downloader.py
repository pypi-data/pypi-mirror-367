import requests
from io import BytesIO


def download_series_matrix(gse_id: str) -> BytesIO:
    """
    Downloads the series_matrix.txt.gz file from GEO into memory.
    Returns a BytesIO object containing the file content.
    """
    base = gse_id[:-3] + "nnn"
    url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{base}/{gse_id}/matrix/{gse_id}_series_matrix.txt.gz"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch matrix file for {gse_id}. Status code: {response.status_code}")
    return BytesIO(response.content)