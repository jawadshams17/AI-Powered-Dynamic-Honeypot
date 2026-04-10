"""
Generate mock behavioral data for the AI Engine to test without live ES/Honeypot.
Creates 'training_data.csv' with realistic attack and benign patterns.
"""
import pandas as pd
import numpy as np
import random
import os

def generate_mock_data(n_samples=1000, output='../data/training_data.csv'):
    os.makedirs('../data', exist_ok=True)
    rows = []
    
    countries = ['US', 'CN', 'RU', 'GB', 'DE', 'PK', 'IN', 'FR']
    
    for _ in range(n_samples):
        is_malicious = random.random() > 0.6 # 40% malicious
        
        if is_malicious:
            # Malicious patterns: high failed logins, specific commands, high entropy
            row = {
                'session_duration': random.uniform(10, 300),
                'num_commands': random.randint(3, 50),
                'num_failed_logins': random.randint(5, 50),
                'num_success_logins': random.choice([0, 1]),
                'unique_usernames': random.randint(1, 5),
                'unique_passwords': random.randint(3, 20),
                'has_download': random.choice([0, 1, 1, 1]), # High prob
                'num_downloads': random.randint(0, 5),
                'avg_inter_cmd_time': random.uniform(0.1, 2.0),
                'cmd_entropy': random.uniform(3.5, 5.0),
                'has_wget_curl': random.choice([0, 1, 1]),
                'has_chmod_exec': random.choice([0, 1, 1]),
                'geo_country': random.choice(['CN', 'RU', 'US', 'PK']),
                'hour_of_day': random.randint(0, 23),
                'src_ip_reputation': random.uniform(0, 40), # Low reputation
                'label': 1
            }
        else:
            # Benign patterns: few commands, few failed logins, low entropy
            row = {
                'session_duration': random.uniform(60, 1800),
                'num_commands': random.randint(1, 10),
                'num_failed_logins': random.randint(0, 2),
                'num_success_logins': 1,
                'unique_usernames': 1,
                'unique_passwords': 1,
                'has_download': random.choice([0, 0, 0, 1]),
                'num_downloads': 0,
                'avg_inter_cmd_time': random.uniform(2.0, 10.0),
                'cmd_entropy': random.uniform(1.0, 3.0),
                'has_wget_curl': 0,
                'has_chmod_exec': 0,
                'geo_country': random.choice(['US', 'GB', 'DE', 'PK']),
                'hour_of_day': random.randint(8, 20),
                'src_ip_reputation': random.uniform(70, 100), # High reputation
                'label': 0
            }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output, index=False)
    print(f"Mock data generated: {n_samples} samples saved to {output}")

if __name__ == '__main__':
    generate_mock_data()
