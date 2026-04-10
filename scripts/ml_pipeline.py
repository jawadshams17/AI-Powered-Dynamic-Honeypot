"""
Train and evaluate ensemble ML models for threat detection.
"""
import os
import json
import joblib
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, f1_score
from xgboost import XGBClassifier

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class ThreatDetectionPipeline:
    def __init__(self):
        self.models = {
            'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=15, class_weight='balanced', random_state=42),
            'XGBoost': XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, scale_pos_weight=3, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=150, max_depth=6, random_state=42)
        }
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.best_model = None
        self.best_model_name = None

    def train_and_eval(self, df):
        logger.info("Starting training and evaluation...")
        # 1. Preprocessing
        df['geo_country_enc'] = self.label_encoder.fit_transform(df['geo_country'].fillna('Unknown'))
        
        # Features exclude non-predictive columns
        features = [
            'session_duration', 'num_commands', 'num_failed_logins',
            'num_success_logins', 'unique_usernames', 'unique_passwords',
            'has_download', 'num_downloads', 'avg_inter_cmd_time',
            'cmd_entropy', 'has_wget_curl', 'has_chmod_exec',
            'hour_of_day', 'src_ip_reputation', 'geo_country_enc'
        ]
        
        X = self.scaler.fit_transform(df[features].fillna(0))
        y = df['label'].values

        # 2. Evaluation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        results = {}
        for name, model in self.models.items():
            logger.info(f"Evaluating {name}...")
            y_pred = cross_val_predict(model, X, y, cv=cv)
            f1 = f1_score(y, y_pred, average='weighted')
            results[name] = {'f1': f1, 'report': classification_report(y, y_pred)}
            logger.info(f"{name} F1-Score: {f1:.4f}")

        # 3. Select Best
        self.best_model_name = max(results, key=lambda k: results[k]['f1'])
        self.best_model = self.models[self.best_model_name]
        logger.info(f"BEST MODEL: {self.best_model_name}")
        
        # Train final version
        self.best_model.fit(X, y)
        return results

    def save(self, path='../models/'):
        os.makedirs(path, exist_ok=True)
        joblib.dump(self.best_model, os.path.join(path, "threat_model.pkl"))
        joblib.dump(self.scaler, os.path.join(path, "scaler.pkl"))
        joblib.dump(self.label_encoder, os.path.join(path, "label_encoder.pkl"))
        logger.info(f"Models saved to {path}")

if __name__ == '__main__':
    data_path = '../data/training_data.csv'
    if not os.path.exists(data_path):
        logger.error(f"Data file not found at {data_path}. Run mock_data_generator.py first.")
    else:
        df = pd.read_csv(data_path)
        pipeline = ThreatDetectionPipeline()
        pipeline.train_and_eval(df)
        pipeline.save()
