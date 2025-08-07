from .api.chunkr import Chunkr
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

# Read version from pyproject.toml
try:
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    __version__ = pyproject_data["project"]["version"]
except Exception:
    __version__ = "unknown"

__all__ = ["Chunkr", "__version__"]
