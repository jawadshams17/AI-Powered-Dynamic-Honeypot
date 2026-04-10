"""
Generate real SHAP (SHapley Additive exPlanations) visuals for model interpretability.
Shows precisely which features drive the AI Engine's classification decisions.
"""
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
from xgboost import XGBClassifier

def generate_correlation_analysis(data_path='../data/', plot_dir=None):
    print("[+] Initiating Statistical Correlation Analysis...")
    if plot_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plot_dir = os.path.join(base_dir, 'logs', 'plots')
    
    # 1. Load data
    df = pd.read_csv(os.path.join(data_path, 'training_data.csv'))
    
    # 2. Select numeric features for correlation
    features = [
        'session_duration', 'num_commands', 'num_failed_logins',
        'num_success_logins', 'unique_usernames', 'unique_passwords',
        'has_download', 'num_downloads', 'avg_inter_cmd_time',
        'cmd_entropy', 'has_wget_curl', 'has_chmod_exec',
        'hour_of_day', 'src_ip_reputation', 'label'
    ]
    
    corr_matrix = df[features].corr()
    
    # 3. Plot Heatmap
    plt.figure(figsize=(14, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title("AI Engine: Feature Correlation Matrix (Multicollinearity Audit)")
    
    corr_path = os.path.join(plot_dir, 'correlation_matrix.png')
    plt.savefig(corr_path, bbox_inches='tight')
    print(f"[SUCCESS] Correlation Matrix generated: {corr_path}")
    plt.close()

def generate_shap_visuals(model_path=None, data_path=None):
    print("[+] Initiating SHAP Interpretability Pipeline...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if model_path is None: model_path = os.path.join(base_dir, 'models')
    if data_path is None: data_path = os.path.join(base_dir, 'data')
    plot_dir = os.path.join(base_dir, 'logs', 'plots')
    
    os.makedirs(plot_dir, exist_ok=True)
    
    # 1. Load best model and data
    model = joblib.load(os.path.join(model_path, 'threat_model.pkl'))
    scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
    df = pd.read_csv(os.path.join(data_path, 'training_data.csv'))
    
    # 2. Get features used in training
    # Note: Ensure this matches the list in ml_pipeline.py
    features = [
        'session_duration', 'num_commands', 'num_failed_logins',
        'num_success_logins', 'unique_usernames', 'unique_passwords',
        'has_download', 'num_downloads', 'avg_inter_cmd_time',
        'cmd_entropy', 'has_wget_curl', 'has_chmod_exec',
        'hour_of_day', 'src_ip_reputation', 'geo_country_enc'
    ]
    
    # Pre-process data (encode geo_country if not already done in csv)
    if 'geo_country_enc' not in df.columns:
        from sklearn.preprocessing import LabelEncoder
        le = LabelEncoder()
        df['geo_country_enc'] = le.fit_transform(df['geo_country'].fillna('Unknown'))

    X = df[features].fillna(0)
    X_scaled = scaler.transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=features)
    
    # 3. Initialize SHAP Explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_scaled_df)
    
    # 4. Generate Summary Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_scaled_df, show=False)
    plt.title("AI Engine: SHAP Global Feature Importance")
    summary_path = os.path.join(plot_dir, 'shap_summary.png')
    plt.savefig(summary_path, bbox_inches='tight')
    print(f"[SUCCESS] Summary Plot generated: {summary_path}")
    plt.close()
    
    # 5. Generate Waterfall Plot for a malicious example
    malicious_idx = df[df['label'] == 1].index[0]
    plt.figure(figsize=(10, 6))
    
    # Handle array vs scalar expected value for binary/multi-output models
    exp_val = explainer.expected_value
    if isinstance(exp_val, (list, np.ndarray)) and len(exp_val) > 1:
        exp_val = exp_val[1] # Choose malicious class for binary
    elif isinstance(exp_val, (list, np.ndarray)) and len(exp_val) == 1:
        exp_val = exp_val[0]
        
    vals = shap_values[malicious_idx]
    if isinstance(vals, (list, np.ndarray)) and len(np.shape(vals)) > 1:
        vals = vals[:, 1] # Choose malicious class values
        
    shap.plots._waterfall.waterfall_legacy(exp_val, vals, feature_names=features, show=False)
    plt.title("Tactical Transparency: Why was this IP blocked?")
    waterfall_path = os.path.join(plot_dir, 'shap_waterfall_attack.png')
    plt.savefig(waterfall_path, bbox_inches='tight')
    print(f"[SUCCESS] Waterfall Plot generated: {waterfall_path}")
    plt.close()

if __name__ == '__main__':
    try:
        generate_shap_visuals()
        generate_correlation_analysis()
    except Exception as e:
        print(f"[!] Error in SHAP pipeline: {e}")
        import traceback
        traceback.print_exc()
