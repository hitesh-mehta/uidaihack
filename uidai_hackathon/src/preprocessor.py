
import pandas as pd
import difflib
import os
import shutil

def generate_mapping(input_path, output_path):
    print(f"Reading data from {input_path}...")
    try:
        df = pd.read_csv(input_path, usecols=['State', 'District'])
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print("Extracting unique State-District pairs...")
    unique_pairs = df.drop_duplicates().sort_values(['State', 'District']).reset_index(drop=True)
    
    print(f"Found {len(unique_pairs)} unique pairs.")

    mappings = []
    
    # 1. State Normalization
    # Robust mapping based on inspection of unique_states_list.txt
    state_corrections = {
        '100000': None, # Drop
        'State': None, # Drop header
        'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
        'Andhra Pradesh': 'Andhra Pradesh',
        'Andra Pradesh': 'Andhra Pradesh',
        'andhra pradesh': 'Andhra Pradesh',
        'Arunachal Pradesh': 'Arunachal Pradesh',
        'Assam': 'Assam',
        'BALANAGAR': 'Telangana', # City mapping
        'Bihar': 'Bihar',
        'Chandigarh': 'Chandigarh',
        'Chhatisgarh': 'Chhattisgarh',
        'Chhattisgarh': 'Chhattisgarh',
        'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Dadra and Nagar Haveli': 'Dadra and Nagar Haveli and Daman and Diu',
        'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Darbhanga': 'Bihar', # City mapping
        'Delhi': 'Delhi',
        'GURGAON': 'Haryana', # City mapping
        'Goa': 'Goa',
        'Greater Kailash 2': 'Delhi', # Locality mapping
        'Gujarat': 'Gujarat',
        'Haryana': 'Haryana',
        'Himachal Pradesh': 'Himachal Pradesh',
        'Jaipur': 'Rajasthan', # City mapping
        'Jammu & Kashmir': 'Jammu and Kashmir',
        'Jammu and Kashmir': 'Jammu and Kashmir',
        'J&K': 'Jammu and Kashmir',
        'Zammu & Kashmir': 'Jammu and Kashmir',
        'Jharkhand': 'Jharkhand',
        'Karnataka': 'Karnataka',
        'Kerala': 'Kerala',
        'Ladakh': 'Ladakh',
        'Lakshadweep': 'Lakshadweep',
        'Madanapalle': 'Andhra Pradesh', # City mapping
        'Madhya Pradesh': 'Madhya Pradesh',
        'Maharashtra': 'Maharashtra',
        'Manipur': 'Manipur',
        'Meghalaya': 'Meghalaya',
        'Mizoram': 'Mizoram',
        'Nagaland': 'Nagaland',
        'Nagpur': 'Maharashtra', # City mapping
        'ODISHA': 'Odisha',
        'Odisha': 'Odisha',
        'odisha': 'Odisha',
        'Orissa': 'Odisha', # Old name
        'Pondicherry': 'Puducherry',
        'Puducherry': 'Puducherry',
        'Punjab': 'Punjab',
        'Puttenahalli': 'Karnataka', # Locality mapping
        'Raja Annamalai Puram': 'Tamil Nadu', # Locality mapping
        'Rajasthan': 'Rajasthan',
        'Sikkim': 'Sikkim',
        'Tamil Nadu': 'Tamil Nadu',
        'Tamilnadu': 'Tamil Nadu',
        'Telangana': 'Telangana',
        'Tripura': 'Tripura',
        'Uttar Pradesh': 'Uttar Pradesh',
        'Uttarakhand': 'Uttarakhand',
        'Uttaranchal': 'Uttarakhand',
        'WEST BENGAL': 'West Bengal',
        'WESTBENGAL': 'West Bengal',
        'West  Bengal': 'West Bengal',
        'West Bangal': 'West Bengal',
        'West Bengal': 'West Bengal',
        'west Bengal': 'West Bengal',
        'West Bengli': 'West Bengal',
        'West bengal': 'West Bengal',
        'Westbengal': 'West Bengal',
    }

    print("Applying robust state corrections...")

    # 2. District Normalization
    for index, row in unique_pairs.iterrows():
        original_state = row['State']
        original_district = row['District']
        
        # Apply state correction
        if original_state in state_corrections:
            corrected_state = state_corrections[original_state]
        else:
            # Fallback
            corrected_state = original_state.strip() if isinstance(original_state, str) else None
            
        if corrected_state is None:
            continue # Skip garbage rows
            
        corrected_district = original_district.strip() if isinstance(original_district, str) else str(original_district)
        
        mappings.append({
            'Original_State': original_state,
            'Original_District': original_district,
            'Corrected_State': corrected_state,
            'Corrected_District': corrected_district,
            'Notes': ''
        })

    mapping_df = pd.DataFrame(mappings)
    
    print("Flagging potential duplicates...")
    state_districts = mapping_df.groupby('Corrected_State')['Corrected_District'].unique().to_dict()
    
    for i, row in mapping_df.iterrows():
        state = row['Corrected_State']
        district = row['Corrected_District']
        
        if state in state_districts:
            others = state_districts[state]
            matches = difflib.get_close_matches(district, others, n=3, cutoff=0.85)
            matches = [m for m in matches if m != district]
            if matches:
                mapping_df.at[i, 'Notes'] = f"Possible duplicate of: {', '.join(matches)}"

    print(f"Saving mapping to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    mapping_df.to_csv(output_path, index=False)
    print("Done.")

def clean_data(input_path, mapping_path, output_path):
    print("Starting data cleaning process...")
    
    if not os.path.exists(mapping_path):
        print(f"Mapping file not found at {mapping_path}. Please generate it first.")
        return

    print(f"Loading mapping from {mapping_path}...")
    mapping_df = pd.read_csv(mapping_path)
    
    print(f"Reading raw data from {input_path}...")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    print("Applying mapping to normalize State and District...")
    
    print("Merging with mapping dataframe...")
    df = df.merge(mapping_df[['Original_State', 'Original_District', 'Corrected_State', 'Corrected_District']], 
                  left_on=['State', 'District'], 
                  right_on=['Original_State', 'Original_District'], 
                  how='left')
    
    # Drop rows that didn't match the mapping (garbage)
    before_len = len(df)
    df = df.dropna(subset=['Corrected_State'])
    print(f"Dropped {before_len - len(df)} garbage rows.")
    
    # Drop old columns and rename new ones
    df.drop(columns=['State', 'District', 'Original_State', 'Original_District'], inplace=True)
    df.rename(columns={'Corrected_State': 'State', 'Corrected_District': 'District'}, inplace=True)
    
    # Reorder columns
    cols = ['Date', 'State', 'District', 'Pincode'] + [c for c in df.columns if c not in ['Date', 'State', 'District', 'Pincode']]
    df = df[cols]
    
    print(f"Saving cleaned data to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print("Cleaned master dataset created successfully.")

def clean_enrolment(input_path, mapping_path, output_path):
    print(f"Cleaning Enrolment data from {input_path}...")
    df = pd.read_csv(input_path)
    mapping_df = pd.read_csv(mapping_path)
    state_map = dict(zip(mapping_df['Original_State'], mapping_df['Corrected_State']))
    district_map = dict(zip(mapping_df['Original_District'], mapping_df['Corrected_District'])) # Assuming district mapping exists or we reuse state logic if needed
    
    # Apply State Mapping
    df['State'] = df['State'].astype(str).str.strip()
    df['Corrected_State'] = df['State'].map(state_map).fillna(df['State']) 
    
    # Filter garbage
    df = df.dropna(subset=['Corrected_State'])
    df = df[df['Corrected_State'].str.len() > 2] 
    
    # Update State col
    df['State'] = df['Corrected_State']
    df.drop(columns=['Corrected_State'], inplace=True)
    
    # Numeric conversion
    cols = ['Age_0_5', 'Age_5_17', 'Age_18_greater']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
    df['Total_Enrolment'] = df[cols].sum(axis=1)
    
    # Save
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned Enrolment data to {output_path}")

def clean_demo(input_path, mapping_path, output_path):
    print(f"Cleaning Demo data from {input_path}...")
    df = pd.read_csv(input_path)
    mapping_df = pd.read_csv(mapping_path)
    state_map = dict(zip(mapping_df['Original_State'], mapping_df['Corrected_State']))
    
    # Apply State Mapping
    df['State'] = df['State'].astype(str).str.strip()
    df['Corrected_State'] = df['State'].map(state_map).fillna(df['State'])
    
    df = df.dropna(subset=['Corrected_State'])
    df = df[df['Corrected_State'].str.len() > 2]
    
    df['State'] = df['Corrected_State']
    df.drop(columns=['Corrected_State'], inplace=True)
    
    # Numeric conversion
    cols = ['Demo_age_5_17', 'Demo_age_17+']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
    df['Total_Demo_Updates'] = df[cols].sum(axis=1)
    
    # Save
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned Demo data to {output_path}")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    sys.path.append(str(project_root))
    
    from uidai_hackathon.src import config

    print("Regenerating mapping with new robust logic...")
    # generate_mapping is defined in this file
    generate_mapping(config.RAW_DATA_PATH, config.MAPPING_PATH)
    
    clean_data(config.RAW_DATA_PATH, config.MAPPING_PATH, config.MASTER_DATA_PATH)
    
    # Clean new datasets
    if os.path.exists(config.ENROLMENT_DATA_PATH):
        clean_enrolment(config.ENROLMENT_DATA_PATH, config.MAPPING_PATH, config.MASTER_ENROLMENT_PATH)
    
    if os.path.exists(config.DEMO_DATA_PATH):
        clean_demo(config.DEMO_DATA_PATH, config.MAPPING_PATH, config.MASTER_DEMO_PATH)
