
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error
import numpy as np

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_and_prep_data(filepath, date_col='Date', value_cols=None):
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
    
    if value_cols:
        for col in value_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df = df.dropna(subset=[date_col])
    return df

def train_forecast_model(df, output_path, title, value_cols):
    print(f"Forecasting for {title}...")
    # Aggregate by Month
    # We sum up the value columns to get a 'Total'
    monthly_data = df.groupby(pd.Grouper(key='Date', freq='ME'))[value_cols].sum()
    monthly_data['Total'] = monthly_data.sum(axis=1)
    
    # Check data length
    if len(monthly_data) < 12:
        print(f"WARNING: Not enough data for {title} (Rows: {len(monthly_data)}). Skipping seasonal model.")
        # We can still plot historical
        plt.figure()
        plt.plot(monthly_data.index, monthly_data['Total'], label='Historical')
        plt.title(f'{title} - Historical Data (Insufficient for Forecast)')
        plt.savefig(output_path)
        plt.close()
        return

    # Train/Test Split
    train_size = int(len(monthly_data) * 0.8)
    train, test = monthly_data['Total'].iloc[:train_size], monthly_data['Total'].iloc[train_size:]
    
    try:
        model = ExponentialSmoothing(
            train, 
            trend='add', 
            seasonal='add', 
            seasonal_periods=12,
            initialization_method="estimated" 
        ).fit()
        
        forecast_len = len(test) + 6
        predictions = model.forecast(forecast_len)
        
        # metrics
        if len(test) > 0:
            rmse = np.sqrt(mean_squared_error(test, predictions[:len(test)]))
        else:
            rmse = 0
            
        # Plot
        plt.figure()
        plt.plot(train.index, train, label='Train')
        plt.plot(test.index, test, label='Test', color='green')
        
        # Forecast Index
        pred_index = pd.date_range(start=train.index[-1] + pd.Timedelta(days=1), periods=forecast_len, freq='ME') 
        if not isinstance(predictions, pd.Series):
             predictions = pd.Series(predictions, index=pred_index)
             
        plt.plot(predictions.index, predictions, label='Forecast (6 Months)', color='red', linestyle='--')
        plt.title(f'{title} Forecast (RMSE: {rmse:.0f})')
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Saved forecast to {output_path}")
        
    except Exception as e:
        print(f"Model failed for {title}: {e}")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent.parent
    sys.path.append(str(project_root))
    
    from uidai_hackathon.src import config
    
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    
    # 1. Biometric
    if os.path.exists(config.MASTER_DATA_PATH):
        df = load_and_prep_data(config.MASTER_DATA_PATH, value_cols=['Bio_age_5_17', 'Bio_age_17+'])
        train_forecast_model(df, config.FIGURES_DIR / "forecast_biometric.png", "Biometric Updates", ['Bio_age_5_17', 'Bio_age_17+'])
        
    # 2. Enrolment
    if os.path.exists(config.MASTER_ENROLMENT_PATH):
        df_enrol = load_and_prep_data(config.MASTER_ENROLMENT_PATH, value_cols=['Total_Enrolment'])
        train_forecast_model(df_enrol, config.FIGURES_DIR / "forecast_enrolment.png", "Aadhaar Enrolments", ['Total_Enrolment'])
        
    # 3. Demographic
    if os.path.exists(config.MASTER_DEMO_PATH):
        df_demo = load_and_prep_data(config.MASTER_DEMO_PATH, value_cols=['Total_Demo_Updates'])
        train_forecast_model(df_demo, config.FIGURES_DIR / "forecast_demo.png", "Demographic Updates", ['Total_Demo_Updates'])
        
    print("All forecasts complete.")
