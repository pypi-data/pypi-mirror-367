import platform
import sys
from pathlib import Path

# Handle tomllib import for Python 3.10 compatibility
try:
    import tomllib
except ImportError:
    import tomli as tomllib

def _find_pyproject_toml(start_path: Path) -> Path | None:
    """Search for pyproject.toml in current and parent directories."""
    for parent in [start_path, *start_path.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None

# Read version from pyproject.toml
try:
    pyproject_path = _find_pyproject_toml(Path(__file__).resolve().parent)
    if pyproject_path is not None:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        __version__ = pyproject_data["project"]["version"]
    else:
        __version__ = "unknown"
except Exception:
    __version__ = "unknown"

class HeadersMixin:
    """Mixin class for handling authorization headers"""
    _api_key: str = ""

    def get_api_key(self) -> str:
        """Get the API key"""
        if not hasattr(self, "_api_key") or not self._api_key:
            raise ValueError("API key not set")
        return self._api_key

    def _headers(self) -> dict:
        """Generate authorization headers and version information"""
        user_agent = f"chunkr-ai/{__version__} (Python/{sys.version.split()[0]}; {platform.system()}/{platform.release()})"
        return {
            "Authorization": self.get_api_key(),
            "User-Agent": user_agent
        }
