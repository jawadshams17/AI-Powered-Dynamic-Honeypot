"""
Unit tests for core project components.
To be used for technical verification and methodology defense.
"""
import unittest
from feature_extractor import CowrieFeatureExtractor

class TestFeatureExtractor(unittest.TestCase):
    def setUp(self):
        # Mock config
        self.config = {
            "elasticsearch": {"host": "localhost", "port": 9200, "user": "u", "password": "p", "index_pattern": "i"}
        }
        # We don't initialize the connection, just the logic
        self.extractor = CowrieFeatureExtractor.__new__(CowrieFeatureExtractor)

    def test_duration_calculation(self):
        events = [
            {'timestamp': '2026-04-08T00:00:00Z'},
            {'timestamp': '2026-04-08T00:01:40Z'}
        ]
        feats = self.extractor.extract_features(events)
        self.assertEqual(feats['session_duration'], 100.0)

    def test_command_counting(self):
        events = [
            {'eventid': 'cowrie.command.input', 'input': 'ls'},
            {'eventid': 'cowrie.command.input', 'input': 'whoami'},
            {'eventid': 'cowrie.login.success'}
        ]
        feats = self.extractor.extract_features(events)
        self.assertEqual(feats['num_commands'], 2)

    def test_entropy_calculation(self):
        # Simple patterns should have low entropy, complex high.
        events_low = [{'eventid': 'cowrie.command.input', 'input': 'aaaaa'}]
        events_high = [{'eventid': 'cowrie.command.input', 'input': 'aB#1z'}]
        f_low = self.extractor.extract_features(events_low)
        f_high = self.extractor.extract_features(events_high)
        self.assertGreater(f_high['cmd_entropy'], f_low['cmd_entropy'])

if __name__ == '__main__':
    unittest.main()
