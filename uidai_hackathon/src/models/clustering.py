
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

sns.set_style("whitegrid")

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    cols_to_numeric = ['Bio_age_5_17', 'Bio_age_17+']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Total_Updates'] = df['Bio_age_5_17'] + df['Bio_age_17+']
    return df

def perform_clustering(df, output_dir):
    print("Preparing data for clustering...")
    # Aggregate by District
    district_profile = df.groupby(['State', 'District'])[['Bio_age_5_17', 'Bio_age_17+', 'Total_Updates']].sum().reset_index()
    
    # Feature Engineering
    # 1. Volume (we will log transform this or just standardize, heavily skewed)
    district_profile['Child_Share'] = district_profile['Bio_age_5_17'] / district_profile['Total_Updates']
    district_profile['Adult_Share'] = district_profile['Bio_age_17+'] / district_profile['Total_Updates']
    
    # Handle districts with 0 updates (unlikely given cleaning, but safe to check)
    district_profile = district_profile.fillna(0)
    
    # Features for Clustering
    # We use Child_Share and Total_Updates. 
    # Total Updates tells us size (Metro vs Village), Child Share tells us demographic intent.
    
    features = ['Total_Updates', 'Child_Share']
    X = district_profile[features].copy()
    
    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("Running K-Means Clustering...")
    # 4 Clusters: e.g., High Vol/High Child, High Vol/Low Child, Low Vol/High Child, Low Vol/Low Child
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    district_profile['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Analyzing Clusters
    print("Cluster Centers (Scaled):")
    print(kmeans.cluster_centers_)
    
    cluster_summary = district_profile.groupby('Cluster')[['Total_Updates', 'Child_Share']].mean()
    print("\nCluster Summary (Original Scale):")
    print(cluster_summary)
    
    # Labeling Clusters (Automated naming based on logic is hard, we will just use ID in chart)
    # But let's try to give them descriptive names based on the summary
    # Sort by Total Updates to define "High Volume" vs "Low Volume"
    
    # Save Results
    district_profile.to_csv(os.path.join(output_dir, 'district_clusters.csv'), index=False)
    
    # Visualization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=district_profile, x='Total_Updates', y='Child_Share', hue='Cluster', palette='viridis', alpha=0.7)
    plt.xscale('log') # Log scale for Volume usually looks better
    plt.title('District Clustering: Volume vs Child Update Share')
    plt.xlabel('Total Updates (Log Scale)')
    plt.ylabel('Share of Child Updates (5-17)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cluster_scatter.png'))
    plt.close()
    
    print("Clustering complete. Saved to district_clusters.csv and cluster_scatter.png")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    sys.path.append(str(project_root))
    
    from uidai_hackathon.src import config
    
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    
    if os.path.exists(config.MASTER_DATA_PATH):
        df = load_data(config.MASTER_DATA_PATH)
        perform_clustering(df, config.FIGURES_DIR)
