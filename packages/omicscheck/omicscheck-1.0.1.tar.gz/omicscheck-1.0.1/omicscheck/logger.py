import logging
from pathlib import Path

def setup_logger(log_path: Path):
    """
    Initializes and returns a logger that writes to the given path.
    """
    logger = logging.getLogger("OmicsCheckLogger")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if logger is reused
    if not logger.handlers:
        fh = logging.FileHandler(log_path)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
