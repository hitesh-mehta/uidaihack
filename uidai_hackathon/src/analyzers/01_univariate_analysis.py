
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Plotting Style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data(filepath):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    # Using dayfirst=True because date format seems to be dd-mm-yyyy based on header 02-01-2026
    # coerce=True will turn errors into NaT
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce') 
    
    # Ensure numeric columns are actually numeric
    cols_to_numeric = ['Bio_age_5_17', 'Bio_age_17+']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    df = df.dropna(subset=['Date']) # Drop rows where date parsing failed
    return df

def analyze_temporal_trends(df, output_dir):
    print("Analyzing Temporal Trends...")
    # Group by Month
    temporal_df = df.groupby(pd.Grouper(key='Date', freq='M')).agg({
        'Bio_age_5_17': 'sum',
        'Bio_age_17+': 'sum'
    }).reset_index()
    
    temporal_df['Total_Updates'] = temporal_df['Bio_age_5_17'] + temporal_df['Bio_age_17+']
    
    # Plot Total Updates over Time
    plt.figure()
    sns.lineplot(data=temporal_df, x='Date', y='Total_Updates', marker='o', label='Total Updates')
    plt.title('Monthly Biometric Updates Trend')
    plt.ylabel('Count')
    plt.xlabel('Date')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'temporal_trend_total.png'))
    plt.close()
    
    # Plot Split by Age Group
    plt.figure()
    plt.plot(temporal_df['Date'], temporal_df['Bio_age_5_17'], label='Age 5-17', marker='o')
    plt.plot(temporal_df['Date'], temporal_df['Bio_age_17+'], label='Age 17+', marker='o')
    plt.title('Biometric Updates by Age Group (Monthly)')
    plt.ylabel('Count')
    plt.xlabel('Date')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'temporal_trend_by_age.png'))
    plt.close()

def analyze_geographic_distribution(df, output_dir):
    print("Analyzing Geographic Distribution...")
    # State-wise Aggregation
    state_df = df.groupby('State')[['Bio_age_5_17', 'Bio_age_17+']].sum()
    state_df['Total'] = state_df['Bio_age_5_17'] + state_df['Bio_age_17+']
    state_df = state_df.sort_values('Total', ascending=False)
    
    # Top 10 States
    top_10 = state_df.head(10)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_10['Total'], y=top_10.index, palette='viridis')
    plt.title('Top 10 States by Biometric Updates')
    plt.xlabel('Total Updates')
    plt.ylabel('State')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'geo_top_10_states.png'))
    plt.close()
    
    # Save State Statistics CSV
    state_df.to_csv(os.path.join(output_dir, 'state_wise_stats.csv'))

def analyze_age_distribution(df, output_dir):
    print("Analyzing Age Distribution...")
    total_5_17 = df['Bio_age_5_17'].sum()
    total_17_plus = df['Bio_age_17+'].sum()
    
    plt.figure(figsize=(8, 8))
    plt.pie([total_5_17, total_17_plus], labels=['Age 5-17', 'Age 17+'], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
    plt.title('Overall Age Distribution of Biometric Updates')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'age_distribution_pie.png'))
    plt.close()

if __name__ == "__main__":
    base_dir = r"c:\Users\hites\Downloads\aadhaar_biometric"
    input_csv = os.path.join(base_dir, "uidai_hackathon", "data", "processed", "master_biometric.csv")
    output_dir = os.path.join(base_dir, "uidai_hackathon", "outputs", "figures")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_csv):
        print(f"File not found: {input_csv}")
    else:
        df = load_data(input_csv)
        analyze_temporal_trends(df, output_dir)
        analyze_geographic_distribution(df, output_dir)
        analyze_age_distribution(df, output_dir)
        print("Univariate analysis complete. Check inputs in outputs/figures/")
