import os
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

def get_theme_dir():
    """Return the directory containing the theme files."""
    return os.path.dirname(os.path.realpath(__file__))

def get_version():
    """Get version from pyproject.toml."""
    try:
        # Get the path to pyproject.toml (two levels up from __init__.py)
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except (FileNotFoundError, KeyError):
        return "0.0.1"  # Fallback

# Theme metadata
__version__ = get_version()
__theme_name__ = "IDM Material Theme"