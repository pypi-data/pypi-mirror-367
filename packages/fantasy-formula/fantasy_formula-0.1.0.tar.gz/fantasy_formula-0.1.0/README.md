# Fantasy Formula

A comprehensive Python library for calculating Fantasy Formula 1 points based on real F1 race data using the FastF1 API and the official 2025 scoring rules.

## Features

- 🏎️ **Complete 2025 Fantasy F1 Scoring**: Implements all driver and constructor scoring rules
- 📊 **Real Data Integration**: Uses FastF1 API for authentic race data
- 🔧 **Modular Architecture**: Easy to extend and modify for future rule changes
- 🧮 **Advanced Calculations**: Handles overtakes, pitstop bonuses, penalties, and special cases
- 🎯 **Simple Interface**: Easy-to-use API for quick integration
- 🔍 **CLI Support**: Command-line interface for testing and analysis

## Quick Start

```python
from fantasy_formula import FantasyScorer

# Calculate points for a specific race weekend
scorer = FantasyScorer(season=2025, round_num=10)
results = scorer.calculate_full_event()

# Access driver and constructor points
print(f"Verstappen total: {results['drivers']['VER']['total']}")
print(f"Red Bull total: {results['constructors']['Red Bull']['total']}")
```

## Installation

```bash
pip install fantasy-formula
```

Or for development:

```bash
git clone https://github.com/JoshCBruce/fantasy-formula.git
cd fantasy-formula
pip install -e ".[dev]"
```

## CLI Usage

```bash
# Calculate points for a specific race
fantasy-calc --year 2025 --round 12 --format json

# Get help
fantasy-calc --help
```

## Scoring Rules

This library implements the complete 2025 Fantasy Formula scoring system including:

- **Qualifying**: Position-based points, Q2/Q3 progression bonuses
- **Sprint**: Position changes, overtakes, fastest lap bonuses
- **Race**: Full F1 points system, DOTD bonus, pitstop bonuses
- **Penalties**: DSQ handling, transfer penalties
- **Special Cases**: Pit lane starts, unclassified drivers, world record bonuses

For complete scoring details, see [scoring-docs.md](scoring-docs.md).

## Architecture

```
fantasy_formula/
├── scoring/           # Scoring logic for drivers and constructors
├── data/             # Data fetching and preprocessing
├── utils/            # Utility functions for calculations
├── cli/              # Command-line interface
└── tests/            # Comprehensive test suite
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black fantasy_formula/
isort fantasy_formula/

# Type checking
mypy fantasy_formula/
```

## Author

Created by **Josh Bruce** ([@JoshCBruce](https://github.com/JoshCBruce))

## License

MIT License - see [LICENSE](LICENSE) for details.