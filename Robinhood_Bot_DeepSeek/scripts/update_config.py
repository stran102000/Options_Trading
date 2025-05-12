#!/usr/bin/env python3
import yaml
import argparse
import os
from pathlib import Path

def update_config(key: str, value: str, config_file: str = None):
    """Update configuration file with new key-value pair"""
    config_file = config_file or os.getenv('CONFIG_PATH', 'config/live_config.yml')
    path = Path(config_file)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(path) as f:
        config = yaml.safe_load(f)
    
    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Convert value to appropriate type
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.replace('.', '', 1).isdigit():
        value = float(value) if '.' in value else int(value)
    
    current[keys[-1]] = value
    
    with open(path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    
    print(f"Updated {key} = {value} in {config_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update trading bot configuration")
    parser.add_argument('key', help="Config key path (e.g. execution.auto_place_trades)")
    parser.add_argument('value', help="New value to set")
    parser.add_argument('--file', help="Config file path", default=None)
    args = parser.parse_args()
    
    try:
        update_config(args.key, args.value, args.file)
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)