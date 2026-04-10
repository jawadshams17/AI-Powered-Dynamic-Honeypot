"""
Build labeled training dataset from Cowrie Elasticsearch sessions.
Primary: real honeypot data. Supplement with CICIDS-2017 if < 500 sessions.
"""
import json
import logging
import pandas as pd
from feature_extractor import CowrieFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetBuilder:
    def __init__(self, config_path='../configs/config.json'):
        with open(config_path) as f:
            self.config = json.load(f)
        self.extractor = CowrieFeatureExtractor(self.config)

    def auto_label(self, features):
        """Rule-based labeling for Cowrie sessions."""
        if features['num_failed_logins'] >= 5: return 1
        if features['has_download'] == 1: return 1
        if features['has_wget_curl'] and features['has_chmod_exec']: return 1
        if features['unique_passwords'] >= 3: return 1
        if features['session_duration'] < 2.0 and features['num_failed_logins'] >= 1: return 1
        return 0  # benign

    def build_dataset(self, days=60, output='../data/training_data.csv'):
        import os; os.makedirs('../data', exist_ok=True)

        logger.info(f"Fetching sessions (last {days} days)...")
        session_ids = self.extractor.get_all_sessions(days)
        logger.info(f"Found {len(session_ids)} sessions")

        rows = []
        for i, sid in enumerate(session_ids):
            if i % 50 == 0: logger.info(f"  {i}/{len(session_ids)} sessions processed...")
            events  = self.extractor.get_session_events(sid)
            feats   = self.extractor.extract_features(events)
            if feats is None: continue
            feats['label']      = self.auto_label(feats)
            feats['session_id'] = sid
            rows.append(feats)

        df = pd.DataFrame(rows)
        df.to_csv(output, index=False)

        mal = df['label'].sum()
        logger.info(f"Dataset saved: {len(df)} sessions | {mal} malicious | {len(df)-mal} benign")

        if len(df) < 500:
            logger.warning("< 500 sessions collected. Consider supplementing with CICIDS-2017 data.")

        return df

if __name__ == '__main__':
    builder = DatasetBuilder()
    df = builder.build_dataset(days=60)
    print(f"\nLabel distribution:\n{df['label'].value_counts()}")
