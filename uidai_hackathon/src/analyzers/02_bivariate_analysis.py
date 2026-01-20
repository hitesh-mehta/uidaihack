
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    # Ensure numeric columns are actually numeric
    cols_to_numeric = ['Bio_age_5_17', 'Bio_age_17+']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def analyze_age_vs_state(df, output_dir):
    print("Analyzing Age Distribution vs State...")
    state_df = df.groupby('State')[['Bio_age_5_17', 'Bio_age_17+']].sum()
    # Sort by total for better visualization
    state_df['Total'] = state_df['Bio_age_5_17'] + state_df['Bio_age_17+']
    state_df = state_df.sort_values('Total', ascending=False).head(15) # Top 15 states
    
    # Normalize for 100% stacked bar
    state_df_pct = state_df[['Bio_age_5_17', 'Bio_age_17+']].div(state_df['Total'], axis=0) * 100
    
    plt.figure()
    state_df_pct.plot(kind='bar', stacked=True, color=['#ff9999', '#66b3ff'])
    plt.title('Age Group Distribution by Top 15 States')
    plt.ylabel('Percentage')
    plt.xlabel('State')
    plt.legend(['Age 5-17', 'Age 17+'])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bivariate_age_vs_state_stacked.png'))
    plt.close()

def analyze_district_correlation(df, output_dir):
    print("Analyzing District-level Correlations...")
    # Scatter plot of 5-17 vs 17+ by district
    district_df = df.groupby(['State', 'District'])[['Bio_age_5_17', 'Bio_age_17+']].sum().reset_index()
    
    # Calculate Correlation
    corr = district_df[['Bio_age_5_17', 'Bio_age_17+']].corr().iloc[0,1]
    
    plt.figure()
    sns.scatterplot(data=district_df, x='Bio_age_5_17', y='Bio_age_17+', hue='State', legend=False, alpha=0.6)
    plt.title(f'District Correlation: Child vs Adult Updates (r={corr:.2f})')
    plt.xlabel('Bio Updates (Age 5-17)')
    plt.ylabel('Bio Updates (Age 17+)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'bivariate_district_scatter.png'))
    plt.close()

if __name__ == "__main__":
    base_dir = r"c:\Users\hites\Downloads\aadhaar_biometric"
    input_csv = os.path.join(base_dir, "uidai_hackathon", "data", "processed", "master_biometric.csv")
    output_dir = os.path.join(base_dir, "uidai_hackathon", "outputs", "figures")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(input_csv):
        df = load_data(input_csv)
        analyze_age_vs_state(df, output_dir)
        analyze_district_correlation(df, output_dir)
        print("Bivariate analysis complete.")
