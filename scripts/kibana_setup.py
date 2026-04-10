"""
Automated Kibana setup script.
Creates index patterns and visual objects via Kibana Saved Objects API.
"""
import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KibanaSetup')

class KibanaSetup:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'configs', 'config.json')
            
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.kb_url = f"http://{self.config['elasticsearch']['host']}:5601/api"
        self.headers = {
            "kbn-xsrf": "true",
            "Content-Type": "application/json"
        }
        self.es_user = self.config['elasticsearch']['user']
        self.es_pass = self.config['elasticsearch']['password']

    def create_index_pattern(self):
        """Create the cowrie-logs-* index pattern in Kibana."""
        pattern_id = "cowrie-index-pattern"
        data = {
            "attributes": {
                "title": self.config['elasticsearch']['index_pattern'],
                "timeFieldName": "@timestamp"
            }
        }
        
        try:
            r = requests.post(
                f"{self.kb_url}/saved_objects/index-pattern/{pattern_id}",
                headers=self.headers,
                auth=(self.es_user, self.es_pass),
                json=data
            )
            if r.status_code in (200, 409): # 409 means already exists
                logger.info("Kibana Index Pattern created/verified.")
            else:
                logger.error(f"Failed to create index pattern: {r.text}")
        except Exception as e:
            logger.error(f"Error connecting to Kibana: {e}")

    def create_dashboards(self):
        """Placeholder for importing dashboard JSON."""
        # Standard FYP Dashboard JSON would be loaded here
        logger.info("Kibana Dashboard templates ready for import.")

if __name__ == '__main__':
    setup = KibanaSetup()
    # setup.create_index_pattern() # Uncomment during Phase 3 integration
