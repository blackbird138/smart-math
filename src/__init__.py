"""Smart math package."""

from pathlib import Path
import sys

# Ensure the project root is in sys.path when imported via tests
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
