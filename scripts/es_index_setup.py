"""
Setup Elasticsearch Index Mappings for Cowrie logs.
Ensures numeric fields are typed correctly for the AI Engine.
"""
import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ES-Setup')

class ESIndexSetup:
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, 'configs', 'config.json')
            
        with open(config_path) as f:
            self.config = json.load(f)
        self.es_url = f"http://{self.config['elasticsearch']['host']}:9200"
        self.user = self.config['elasticsearch']['user']
        self.password = self.config['elasticsearch']['password']

    def apply_mapping(self):
        # Index Template for cowrie-logs-*
        template = {
            "index_patterns": ["cowrie-logs-*"],
            "template": {
                "mappings": {
                    "properties": {
                        "cowrie.session": {"type": "keyword"},
                        "cowrie.src_ip": {"type": "ip"},
                        "cowrie.duration": {"type": "float"},
                        "cowrie.input": {"type": "text"},
                        "cowrie.timestamp": {"type": "date"},
                        "cowrie.eventid": {"type": "keyword"}
                    }
                }
            }
        }
        
        try:
            r = requests.put(
                f"{self.es_url}/_index_template/cowrie_template",
                auth=(self.user, self.password),
                json=template,
                headers={"Content-Type": "application/json"}
            )
            if r.status_code == 200:
                logger.info("ES Index Template applied successfully.")
            else:
                logger.error(f"Failed to apply template: {r.text}")
        except Exception as e:
            logger.error(f"Could not connect to Elasticsearch: {e}")

if __name__ == '__main__':
    setup = ESIndexSetup()
    # setup.apply_mapping()
