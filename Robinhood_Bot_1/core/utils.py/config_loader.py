import yaml
import os
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from YAML file with environment overrides"""
    default_path = os.getenv('CONFIG_PATH', 'config/live_config.yml')
    path = config_path or default_path
    
    with open(path) as f:
        config = yaml.safe_load(f)
    
    # Apply environment variable overrides
    if os.getenv('AUTO_TRADE'):
        config['execution']['auto_place_trades'] = True
    
    return config

def validate_config(config: Dict) -> bool:
    """Validate configuration structure"""
    required_sections = ['execution', 'risk', 'strategies']
    return all(section in config for section in required_sections)