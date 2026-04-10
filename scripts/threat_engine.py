"""
Real-time threat detection engine daemon.
Periodically polls Elasticsearch for new Cowrie sessions, 
extracts features, classifies threat level, and triggers pfSense blocking.
"""
import json
import time
import logging
import os
import joblib
from datetime import datetime, timezone
from elasticsearch import Elasticsearch
from feature_extractor import CowrieFeatureExtractor
from pfsense_client import PfSenseClient

# Setup Logging
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_path = os.path.join(base_dir, 'logs', 'threat_engine.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ThreatEngine')

class ThreatEngine:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'configs', 'config.json')
            
        logger.info(f"Initializing Threat Engine with config: {config_path}")
        
        # 1. Load Configuration
        if not os.path.exists(config_path):
            # Fallback to template if production config missing
            template_path = config_path + ".template"
            if os.path.exists(template_path):
                import shutil
                shutil.copy(template_path, config_path)
                logger.info(f"Created config from template: {config_path}")
            else:
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path) as f:
            self.config = json.load(f)
            
        # 2. Initialize Components
        self.extractor = CowrieFeatureExtractor(self.config)
        self.pfsense = PfSenseClient(self.config)
        
        # 3. Load ML Model
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, 'models')
        logger.info(f"Loading models from {model_dir}...")
        
        self.model = joblib.load(os.path.join(model_dir, 'threat_model.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
        self.label_encoder = joblib.load(os.path.join(model_dir, 'label_encoder.pkl'))
        
        self.poll_interval = self.config['engine']['poll_interval_seconds']
        self.threat_threshold = self.config['engine']['threat_threshold']
        self.block_threshold = self.config['engine']['block_threshold']
        self.whitelist = self.config['engine']['whitelist_ips']
        
        # Track last processed session timestamp
        self.last_check = datetime.now(timezone.utc).isoformat()
        logger.info(f"Engine ready. Polling every {self.poll_interval}s")

    def run(self):
        logger.info("Threat Engine Daemon Started.")
        while True:
            try:
                self.process_new_sessions()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
            
            time.sleep(self.poll_interval)

    def process_new_sessions(self):
        """Fetch completed sessions since last check and classify them."""
        # Note: In a real implementation, get_completed_sessions_since would query ES
        # for 'cowrie.session.closed' events after self.last_check
        new_sessions = self.extractor.get_completed_sessions_since(self.last_check)
        
        if not new_sessions:
            return

        for sess in new_sessions:
            sid = sess['session_id']
            src_ip = sess['src_ip']
            
            if src_ip in self.whitelist:
                continue

            logger.info(f"Processing session {sid} from {src_ip}...")
            
            events = self.extractor.get_session_events(sid)
            features = self.extractor.extract_features(events)
            
            if not features:
                continue

            # Predict
            threat_score = self.predict_threat(features)
            logger.info(f"Session {sid} | Score: {threat_score:.4f}")

            # Act
            if threat_score >= self.block_threshold:
                logger.warning(f"HIGH THREAT detected from {src_ip} ({threat_score:.4f}). triggering pfSense block.")
                self.pfsense.block_ip(src_ip, reason=f"AI Threat Score: {threat_score:.4f}")
            elif threat_score >= self.threat_threshold:
                logger.info(f"MEDIUM THREAT from {src_ip} ({threat_score:.4f}). Logging alert.")

            # Update last check to latest session timestamp
            self.last_check = sess['timestamp']

    def predict_threat(self, features_dict):
        """Prepare features and run through the model."""
        # Encode geo_country
        try:
            country_enc = self.label_encoder.transform([features_dict.get('geo_country', 'Unknown')])[0]
        except ValueError:
            country_enc = 0 # Default to First if unknown

        # Build feature vector in exact order
        # Assuming NUMERIC_FEATURES order from ml_pipeline.py
        vals = [
            features_dict.get('session_duration', 0),
            features_dict.get('num_commands', 0),
            features_dict.get('num_failed_logins', 0),
            features_dict.get('num_success_logins', 0),
            features_dict.get('unique_usernames', 0),
            features_dict.get('unique_passwords', 0),
            features_dict.get('has_download', 0),
            features_dict.get('num_downloads', 0),
            features_dict.get('avg_inter_cmd_time', 0),
            features_dict.get('cmd_entropy', 0),
            features_dict.get('has_wget_curl', 0),
            features_dict.get('has_chmod_exec', 0),
            features_dict.get('hour_of_day', 0),
            features_dict.get('src_ip_reputation', 50.0),
            country_enc
        ]
        
        X = [vals]
        X_scaled = self.scaler.transform(X)
        
        # Probability of class 1 (malicious)
        prob = self.model.predict_proba(X_scaled)[0][1]
        return prob

if __name__ == '__main__':
    # Ensure logs directory exists
    os.makedirs('../logs', exist_ok=True)
    
    try:
        engine = ThreatEngine()
        engine.run()
    except Exception as e:
        logger.critical(f"Engine failed to start: {e}")
