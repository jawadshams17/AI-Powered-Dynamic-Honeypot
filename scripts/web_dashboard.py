import os
import json
import pandas as pd
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Resolve Paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(base_dir, 'configs', 'config.json')
data_path = os.path.join(base_dir, 'data', 'training_data.csv')
log_path = os.path.join(base_dir, 'logs', 'threat_engine.log')

def get_stats():
    try:
        df = pd.read_csv(data_path)
        total_attacks = len(df)
        high_threat = len(df[df['label'] == 1]) # Assuming 1 is malicious
        return {
            "total_attacks": total_attacks,
            "high_threat": high_threat,
            "uptime": "99.9%",
            "status": "Operational"
        }
    except:
        return {"total_attacks": 0, "high_threat": 0, "uptime": "0%", "status": "Initializing"}

@app.route('/')
def index():
    stats = get_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    return jsonify(get_stats())

@app.route('/api/logs')
def api_logs():
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return jsonify(f.readlines()[-10:])
    return jsonify(["Waiting for engine logs..."])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
