"""Configuration settings for Fantasy Formula."""

import os
from pathlib import Path

# FastF1 cache directory
CACHE_DIR = Path(os.getenv("FASTF1_CACHE_DIR", "~/.cache/fastf1")).expanduser()

# FastF1 settings
FASTF1_REQUEST_TIMEOUT = 30
FASTF1_CACHE_ENABLED = True

# API endpoints
F1_DRIVER_OF_THE_DAY_URL = "https://www.formula1.com/en/results.html"

# Default settings
DEFAULT_SEASON = 2025
DEFAULT_FORMAT = "json"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")