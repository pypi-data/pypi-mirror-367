from pathlib import Path

def get_output_path(gse_id: str) -> Path:
    """
    Returns a Path object pointing to the output directory for the given GEO ID.
    Creates the directory if it doesn't exist under ~/Desktop/OmicsCheckReports/<GSE_ID>
    """
    desktop = Path.home() / "Desktop"
    output_dir = desktop / "OmicsCheckReports" / gse_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir
