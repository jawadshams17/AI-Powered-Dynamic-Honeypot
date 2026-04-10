"""
Master Orchestration TUI for the AI Honeypot System.
Provides a unified dashboard to monitor AI logs, block list, and system health.
"""
import os
import time
import json
import subprocess
from datetime import datetime

class MasterDashboard:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'configs', 'config.json')
        
        with open(config_path) as f:
            self.config = json.load(f)
        self.log_file = '../logs/threat_engine.log'

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_log_tail(self, lines=10):
        if not os.path.exists(self.log_file):
            return ["No logs found. Start the threat engine."]
        with open(self.log_file, 'r') as f:
            return f.readlines()[-lines:]

    def show_metrics(self):
        print(f"=== AI HONEYPOT MASTER DASHBOARD | {datetime.now().strftime('%H:%M:%S')} ===")
        print(f"Engine IP:  {self.config['engine']['whitelist_ips'][1]}")
        print(f"Honeypot:   {self.config['pfsense']['url']}")
        print(f"Poll Rate:  {self.config['engine']['poll_interval_seconds']}s")
        print("-" * 50)
        
        print("\n[RECENT ACTIVITY]")
        for line in self.get_log_tail():
            print(f"  {line.strip()}")
        
        print("-" * 50)
        print("[ACTIONS] (1) Restart Engine  (2) View Blocks  (3) Run Tests  (0) Exit")

    def run(self):
        while True:
            self.clear()
            self.show_metrics()
            time.sleep(2)
            # Input handling would be interactive here

if __name__ == '__main__':
    dash = MasterDashboard()
    dash.run()
