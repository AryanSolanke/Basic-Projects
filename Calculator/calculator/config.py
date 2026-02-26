"""
Central configuration for calculator.
"""

from pathlib import Path
from typing import Final
import tempfile

# Directories
REPO_ROOT: Final = Path(__file__).resolve().parents[1]

def _get_safe_history_dir() -> Path:
    """
    Get history directory with security validation.

    Ensures the history directory stays within project root and falls back
    to a temp directory if validation fails.
    """
    try:
        base_dir = REPO_ROOT
        history_dir = (base_dir / "history").resolve()

        if not str(history_dir).startswith(str(base_dir)):
            raise ValueError("History directory outside project root")

        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir
    except (ValueError, OSError, PermissionError) as e:
        print(f"Warning: Using temp directory for history - {e}")
        fallback_dir = Path(tempfile.gettempdir()) / "calculator_history"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir


HISTORY_DIR: Final = _get_safe_history_dir()

# History files
STD_HISTORY_FILE: Final = HISTORY_DIR / "standard_history.txt"
SCI_HISTORY_FILE: Final = HISTORY_DIR / "scientific_history.txt"
ANGLE_HISTORY_FILE: Final = HISTORY_DIR / "angle_history.txt"
TEMP_HISTORY_FILE: Final = HISTORY_DIR / "temperature_history.txt"
PRESSURE_HISTORY_FILE: Final = HISTORY_DIR / "pressure_history.txt"
WEIGHT_HISTORY_FILE: Final = HISTORY_DIR / "weight_history.txt"
DATA_HISTORY_FILE: Final = HISTORY_DIR / "data_history.txt"

# Precision settings
DECIMAL_PRECISION: Final = 14
DISPLAY_PRECISION: Final = 9
INTERNAL_PRECISION: Final = 60

# UI settings
ENABLE_EMOJIS: Final = True
MENU_WIDTH: Final = 50
