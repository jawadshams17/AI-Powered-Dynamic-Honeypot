"""
Extract 15 behavioral features from Cowrie honeypot sessions stored in Elasticsearch.
"""
import math
import json
import logging
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch

logger = logging.getLogger(__name__)

class CowrieFeatureExtractor:
    FEATURE_NAMES = [
        'session_duration', 'num_commands', 'num_failed_logins',
        'num_success_logins', 'unique_usernames', 'unique_passwords',
        'has_download', 'num_downloads', 'avg_inter_cmd_time',
        'cmd_entropy', 'has_wget_curl', 'has_chmod_exec',
        'geo_country', 'hour_of_day', 'src_ip_reputation'
    ]

    def __init__(self, config):
        es_conf = config['elasticsearch']
        self.es = Elasticsearch(
            [{'host': es_conf['host'], 'port': es_conf['port'], 'scheme': 'http'}],
            basic_auth=(es_conf['user'], es_conf['password'])
        )
        self.index = es_conf['index_pattern']

    def get_completed_sessions_since(self, timestamp):
        """Query ES for sessions that closed since the last check."""
        query = {
            "size": 100,
            "query": {
                "bool": {
                    "must": [
                        {"term": {"eventid": "cowrie.session.closed"}},
                        {"range": {"timestamp": {"gt": timestamp}}}
                    ]
                }
            },
            "sort": [{"timestamp": {"order": "asc"}}]
        }
        try:
            res = self.es.search(index=self.index, body=query)
            return [hit['_source'] for hit in res['hits']['hits']]
        except Exception as e:
            logger.error(f"ES Query Error: {e}")
            return []

    def get_session_events(self, session_id):
        """Fetch all events for a specific session ID."""
        query = {
            "size": 1000,
            "query": {"term": {"session": session_id}},
            "sort": [{"timestamp": {"order": "asc"}}]
        }
        try:
            res = self.es.search(index=self.index, body=query)
            return [hit['_source'] for hit in res['hits']['hits']]
        except Exception as e:
            logger.error(f"ES Query Error: {e}")
            return []

    def extract_features(self, events):
        if not events: return None
        features = {}
        
        # 1. Duration
        ts = [datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) for e in events if e.get('timestamp')]
        features['session_duration'] = (max(ts) - min(ts)).total_seconds() if len(ts) > 1 else 0

        # 2. Commands
        cmds = [e for e in events if e.get('eventid') == 'cowrie.command.input']
        features['num_commands'] = len(cmds)

        # 3. Logins
        features['num_failed_logins'] = sum(1 for e in events if e.get('eventid') == 'cowrie.login.failed')
        features['num_success_logins'] = sum(1 for e in events if e.get('eventid') == 'cowrie.login.success')

        # 4. Credentials
        features['unique_usernames'] = len(set(e.get('username') for e in events if e.get('username')))
        features['unique_passwords'] = len(set(e.get('password') for e in events if e.get('password')))

        # 5. Downloads
        dls = [e for e in events if 'file_download' in str(e.get('eventid', ''))]
        features['has_download'] = 1 if dls else 0
        features['num_downloads'] = len(dls)

        # 6. Timing
        if len(cmds) > 1:
            cmd_ts = sorted([datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00')) for e in cmds if e.get('timestamp')])
            deltas = [(cmd_ts[i+1] - cmd_ts[i]).total_seconds() for i in range(len(cmd_ts)-1)]
            features['avg_inter_cmd_time'] = sum(deltas) / len(deltas)
        else:
            features['avg_inter_cmd_time'] = 0

        # 7. Entropy
        all_input = "".join(e.get('input', '') for e in cmds)
        if all_input:
            p = [c/len(all_input) for c in Counter(all_input).values()]
            features['cmd_entropy'] = -sum(pi * math.log2(pi) for pi in p)
        else:
            features['cmd_entropy'] = 0

        # 8. Keywords
        features['has_wget_curl'] = 1 if any(k in all_input.lower() for k in ['wget', 'curl']) else 0
        features['has_chmod_exec'] = 1 if ('chmod' in all_input.lower() and ('+x' in all_input or '777' in all_input)) else 0

        # 9. Context
        features['geo_country'] = next((e['geoip']['country_name'] for e in events if e.get('geoip', {}).get('country_name')), 'Unknown')
        features['hour_of_day'] = ts[0].hour if ts else 0
        features['src_ip_reputation'] = 50.0  # Placeholder

        return features
