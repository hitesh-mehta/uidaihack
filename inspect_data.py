
import pandas as pd
import os

files = [
    r"f:\0_DTU\1.1_UIDAI_Hack\uidaihack\uidai_hackathon\data\processed\master_enrolment.csv",
    r"f:\0_DTU\1.1_UIDAI_Hack\uidaihack\uidai_hackathon\data\processed\master_biometric.csv",
    r"f:\0_DTU\1.1_UIDAI_Hack\uidaihack\uidai_hackathon\data\processed\master_demo.csv"
]

for f in files:
    if os.path.exists(f):
        print(f"\n--- {os.path.basename(f)} ---")
        try:
            df = pd.read_csv(f, nrows=5)
            print(df.columns.tolist())
        except Exception as e:
            print(f"Error reading: {e}")
    else:
        print(f"\n--- {os.path.basename(f)} (MISSING) ---")
