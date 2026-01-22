
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.ensemble import IsolationForest
import numpy as np

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    
    cols_to_numeric = ['Bio_age_5_17', 'Bio_age_17+']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df = df.dropna(subset=['Date'])
    
    # Create Total column
    df['Total_Updates'] = df['Bio_age_5_17'] + df['Bio_age_17+']
    return df

def detect_anomalies(df, output_dir):
    print("Preparing data for anomaly detection...")
    
    # We will look for anomalies at District level over time
    # Aggregating by District and Month
    # This gives us a time series for each district
    
    district_monthly = df.groupby(['State', 'District', pd.Grouper(key='Date', freq='ME')])['Total_Updates'].sum().reset_index()
    
    # Feature for Anomaly Detection: Total Updates
    # In a real scenario, we'd add rolling means, std dev, etc.
    # For now, let's use Total Updates and maybe 'Month' cyclicity if possible, 
    # but univariate Isolation Forest on 'Total_Updates' per district is a good start to find "spikes"
    
    # To make it fair across districts of different sizes, we might need Z-score?
    # Or we run Isolation Forest on the whole set?
    # A huge city will naturally have high updates. We want to find *unusual* updates for *that* district.
    # So Z-score Standardization per district is better.
    
    print("Calculating Z-scores per district...")
    district_monthly['Mean'] = district_monthly.groupby('District')['Total_Updates'].transform('mean')
    district_monthly['Std'] = district_monthly.groupby('District')['Total_Updates'].transform('std')
    
    # Avoid division by zero
    district_monthly['Z_Score'] = (district_monthly['Total_Updates'] - district_monthly['Mean']) / (district_monthly['Std'] + 1e-5)
    district_monthly['Z_Score'] = district_monthly['Z_Score'].fillna(0)
    
    print("Training Isolation Forest...")
    # Reshape for sklearn
    X = district_monthly[['Z_Score', 'Total_Updates']]
    
    clf = IsolationForest(contamination=0.05, random_state=42) # 5% anomalies
    district_monthly['Anomaly'] = clf.fit_predict(X)
    
    # Anomaly = -1
    anomalies = district_monthly[district_monthly['Anomaly'] == -1]
    
    print(f"Detected {len(anomalies)} anomalies out of {len(district_monthly)} records.")
    
    # Save Anomalies to CSV
    anomalies.to_csv(os.path.join(output_dir, 'anomalies_detected.csv'), index=False)
    
    # Plotting Top Anomalies
    # Let's plot the Z-score distribution and highlight anomalies
    plt.figure()
    sns.scatterplot(data=district_monthly, x='Total_Updates', y='Z_Score', hue='Anomaly', palette={1: 'blue', -1: 'red'}, alpha=0.6)
    plt.title('Anomaly Detection: Total Updates vs Z-Score')
    plt.xlabel('Total Monthly Updates')
    plt.ylabel('Z-Score (Deviation from District Mean)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'anomaly_scatter.png'))
    plt.close()
    
    print("Anomaly detection complete. Check output CSV/PNG.")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    sys.path.append(str(project_root))
    
    from uidai_hackathon.src import config
    
    if os.path.exists(config.MASTER_DATA_PATH):
        df = load_data(config.MASTER_DATA_PATH)
        detect_anomalies(df, config.FIGURES_DIR)
    else:
        print(f"Data file not found at {config.MASTER_DATA_PATH}")
