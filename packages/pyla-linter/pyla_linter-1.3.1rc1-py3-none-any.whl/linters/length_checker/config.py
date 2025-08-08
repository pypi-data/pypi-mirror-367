"""Configuration handling for the length checker plugin."""

from pathlib import Path
from typing import Any, Dict, Optional

try:
    import tomllib
except ImportError:
    # Python < 3.11 compatibility
    import tomli as tomllib  # type: ignore


class LengthCheckerConfig:
    """Configuration for the length checker plugin."""

    DEFAULT_FUNCTION_LENGTH = 40
    DEFAULT_CLASS_LENGTH = 200

    def __init__(
        self,
        max_function_length: int = DEFAULT_FUNCTION_LENGTH,
        max_class_length: int = DEFAULT_CLASS_LENGTH,
    ):
        """Initialize configuration with defaults.

        Args:
            max_function_length: Maximum allowed function length
            max_class_length: Maximum allowed class length
        """
        self.max_function_length = max_function_length
        self.max_class_length = max_class_length

    @classmethod
    def from_pyproject_toml(cls, path: Optional[Path] = None) -> "LengthCheckerConfig":
        """Load configuration from pyproject.toml.

        Args:
            path: Path to pyproject.toml. If None, searches from current directory.

        Returns:
            LengthCheckerConfig instance
        """
        if path is None:
            path = cls._find_pyproject_toml()

        if path is None or not path.exists():
            return cls()

        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)

            config_data = data.get("tool", {}).get("pyla-linters", {})
            return cls.from_dict(config_data)
        except Exception:
            # If any error occurs, return default config
            return cls()

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "LengthCheckerConfig":
        """Create configuration from a dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            LengthCheckerConfig instance
        """
        return cls(
            max_function_length=config.get("max_function_length", cls.DEFAULT_FUNCTION_LENGTH),
            max_class_length=config.get("max_class_length", cls.DEFAULT_CLASS_LENGTH),
        )

    @staticmethod
    def _find_pyproject_toml() -> Optional[Path]:
        """Find pyproject.toml in current or parent directories.

        Returns:
            Path to pyproject.toml or None if not found
        """
        current = Path.cwd()
        for directory in [current] + list(current.parents):
            candidate = directory / "pyproject.toml"
            if candidate.exists():
                return candidate
        return None
