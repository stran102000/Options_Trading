"""
Data package initialization
Handles all data storage and retrieval operations
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd

# Initialize directories
DATA_DIR = Path(__file__).parent
HISTORICAL_DIR = DATA_DIR / "historical"
OUTPUTS_DIR = DATA_DIR / "outputs"

# Create directories if they don't exist
os.makedirs(HISTORICAL_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def get_historical_path(symbol: str) -> Path:
    """Get path for historical data file"""
    return HISTORICAL_DIR / f"{symbol.upper()}.csv"

def save_historical_data(symbol: str, data: pd.DataFrame) -> None:
    """Save historical data to CSV"""
    path = get_historical_path(symbol)
    data.to_csv(path, index=False)
    print(f"Saved historical data to {path}")

def load_historical_data(symbol: str) -> Optional[pd.DataFrame]:
    """Load historical data from CSV"""
    path = get_historical_path(symbol)
    if path.exists():
        return pd.read_csv(path)
    return None

def save_backtest_results(strategy: str, results: Dict[str, Any]) -> Path:
    """Save backtest results to JSON"""
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUTS_DIR / f"backtest_{strategy}_{timestamp}.json"
    pd.DataFrame(results).to_json(path, indent=2)
    return path

def cleanup_old_files(max_files: int = 100) -> None:
    """Maintain directory size limits"""
    for directory in [HISTORICAL_DIR, OUTPUTS_DIR]:
        files = sorted(directory.glob("*"), key=os.path.getmtime)
        for file in files[:-max_files]:
            file.unlink()

__all__ = [
    'get_historical_path',
    'save_historical_data',
    'load_historical_data',
    'save_backtest_results'
]