# Robinhood Algorithmic Trading System

## 📦 Installation
```bash
git clone https://github.com/your-repo/robinhood-algo-trading.git
cd robinhood-algo-trading

# Set up environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## ⚙️ Configuration
1. Copy and edit environment file:
```bash
cp .env.example .env
nano .env  # Add your Robinhood credentials
```

2. Configure trading strategies:
```bash
nano config/live_config.yml
```

## 🚀 Usage
**Run in live mode:**
```bash
python -m core.bot --config config/live_config.yml
```

**Update configuration:**
```bash
python scripts/update_config.py execution.auto_place_trades true
```

**Run tests:**
```bash
pytest tests/ --cov=core --cov-report=html
```

## 📂 File Structure
```
config/         - YAML configuration files
core/           - Main trading logic
  strategies/   - Strategy implementations
  utils/        - Helper functions
tests/          - Unit and integration tests
scripts/        - Utility scripts
data/           - Market data storage
```

## 🔧 Development
1. Add new strategies in `core/strategies/`
2. Implement required methods:
   - `analyze()` - Generate trade signals
   - `calculate_risk()` - Determine position sizing
3. Add tests in `tests/unit/test_strategies.py`

## 🛠️ Maintenance
**Update dependencies:**
```bash
pip freeze > requirements.txt
```

**Reset environment:**
```bash
rm -rf venv/
rm -rf data/outputs/*
```