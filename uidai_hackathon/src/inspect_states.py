
import pandas as pd
import os

base_dir = r"c:\Users\hites\Downloads\aadhaar_biometric"
input_csv = os.path.join(base_dir, "aadhaar_biometric.csv")

try:
    df = pd.read_csv(input_csv)
    states = sorted(df['State'].dropna().unique().tolist())
    
    with open("unique_states_list.txt", "w", encoding="utf-8") as f:
        for state in states:
            f.write(f"'{state}'\n")
            
    print(f"Dumped {len(states)} unique states to unique_states_list.txt")
except Exception as e:
    print(f"Error: {e}")
