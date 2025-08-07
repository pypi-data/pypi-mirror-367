# src/loader.py
import json5
from importlib import resources

def load_json5_data(filename: str) -> dict | list | None:
    """
    Loads and parses data from a JSON5 file located within the 'src.data' package.
    This method is safe for use with packaged applications.
    """
    try:
        # The package path 'src.data' is now hardcoded here, as this loader's
        # specific job is to load data from that location.
        file_content = resources.files("src.data").joinpath(filename).read_text(encoding="utf-8")
        return json5.loads(file_content)
    except FileNotFoundError:
        print(f"Error: Data file not found in package at 'src/data/{filename}'")
        return None
    except Exception as e:
        print(f"Error: Failed to parse data file '{filename}': {e}")
        return None