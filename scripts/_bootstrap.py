"""Make ``vast_s3`` importable when scripts are run directly from the repo."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
