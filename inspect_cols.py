
import pandas as pd
import os

base_dir = r"c:\Users\hites\Downloads\aadhaar_biometric"
enrol_path = os.path.join(base_dir, "aadhaar_enrolment.csv")
demo_path = os.path.join(base_dir, "aadhaar_demo_monthly_update.csv")

try:
    print("--- ENROLMENT COLUMNS ---")
    if os.path.exists(enrol_path):
        print(pd.read_csv(enrol_path, nrows=0).columns.tolist())
    else:
        print("File not found.")

    print("\n--- DEMO COLUMNS ---")
    if os.path.exists(demo_path):
        print(pd.read_csv(demo_path, nrows=0).columns.tolist())
    else:
        print("File not found.")
except Exception as e:
    print(e)
