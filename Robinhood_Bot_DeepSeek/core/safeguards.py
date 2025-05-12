import time
from getpass import getpass
from typing import Dict

class TradeConfirmation:
    def __init__(self, config: Dict):
        self.required_confirmations = config['required_confirmations']
        self.timeout = config['timeout_seconds']
        self.password = config['override_password']
        
    def verify(self, trade: Dict) -> bool:
        """Multi-factor trade verification"""
        print(f"\n=== Trade Verification ===")
        print(self._format_trade(trade))
        
        confirmations = 0
        start = time.time()
        
        while confirmations < self.required_confirmations:
            if time.time() - start > self.timeout:
                print("⌛ Confirmation timed out")
                return False
                
            res = input(f"Confirm {confirmations+1}/{self.required_confirmations} (y/n/p): ").lower()
            
            if res == 'y':
                confirmations += 1
            elif res == 'n':
                return False
            elif res == 'p':
                if self._check_password():
                    return True
                    
        return True
    
    def _check_password(self) -> bool:
        """Password override verification"""
        attempt = getpass("Enter override password: ")
        return attempt == self.password