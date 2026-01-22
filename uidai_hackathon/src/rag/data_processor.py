"""
Data Processor for Aadhaar CSV files
Loads, processes, and chunks the CSV data for vectorization
"""

import pandas as pd
import os
from typing import List, Dict
from tqdm import tqdm
from uidai_hackathon.src import config

class AadhaarDataProcessor:
    """Process Aadhaar CSV files into chunks suitable for RAG"""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        # Use paths from config (now pointing to processed folder)
        self.csv_map = {
            "master_enrolment.csv": config.RAG_ENROLMENT_PATH,
            "master_biometric.csv": config.RAG_BIOMETRIC_PATH,
            "master_demo.csv": config.RAG_DEMO_PATH
        }
        
    def load_csv_files(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files into DataFrames"""
        dataframes = {}
        
        for name, path in self.csv_map.items():
            if os.path.exists(path):
                print(f"Loading {name} from {path}...")
                df = pd.read_csv(path)
                dataframes[name] = df
                print(f"Loaded {len(df)} rows from {name}")
            else:
                print(f"⚠ Warning: {name} not found at {path}")
                print(f"   Please run the preprocessor first to generate processed files!")
                print(f"   Run: python uidai_hackathon/src/preprocessor.py")
                
        return dataframes
    
    def create_text_chunks(self, dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, str]]:
        """
        Convert DataFrame rows into text chunks with metadata
        Each chunk contains information from multiple rows for better context
        """
        all_chunks = []
        
        for csv_file, df in dataframes.items():
            print(f"\nProcessing {csv_file}...")
            
            # Determine the type of data based on filename
            if "biometric" in csv_file:
                data_type = "Biometric Updates"
            elif "demo" in csv_file:
                data_type = "Demographic Monthly Updates"
            else:
                data_type = "General Aadhaar Data"
            
            # Process in chunks
            total_rows = len(df)
            num_chunks = (total_rows // self.chunk_size) + 1
            
            for i in tqdm(range(num_chunks), desc=f"Creating chunks from {csv_file}"):
                start_idx = i * self.chunk_size
                end_idx = min((i + 1) * self.chunk_size, total_rows)
                
                if start_idx >= total_rows:
                    break
                    
                chunk_df = df.iloc[start_idx:end_idx]
                
                # Create a textual representation of the chunk
                text_content = self._dataframe_to_text(chunk_df, data_type, csv_file)
                
                # Create metadata
                metadata = {
                    "source": csv_file,
                    "data_type": data_type,
                    "chunk_index": i,
                    "row_range": f"{start_idx}-{end_idx}",
                    "total_rows": len(chunk_df)
                }
                
                chunk = {
                    "text": text_content,
                    "metadata": metadata
                }
                
                all_chunks.append(chunk)
        
        print(f"\nTotal chunks created: {len(all_chunks)}")
        return all_chunks
    
    def _dataframe_to_text(self, df: pd.DataFrame, data_type: str, source: str) -> str:
        """Convert a DataFrame chunk into a readable text format"""
        
        text_parts = [f"Data Type: {data_type}", f"Source: {source}", ""]
        
        # Add summary statistics
        text_parts.append("Summary Statistics:")
        for column in df.columns:
            if df[column].dtype in ['int64', 'float64']:
                text_parts.append(f"- {column}: Total={df[column].sum()}, Mean={df[column].mean():.2f}, Max={df[column].max()}, Min={df[column].min()}")
        
        text_parts.append("")
        text_parts.append("Sample Records:")
        
        # Add sample rows (first 5 rows of the chunk)
        sample_size = min(5, len(df))
        for idx, row in df.head(sample_size).iterrows():
            row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
            text_parts.append(f"Record: {row_text}")
        
        # Add unique value information for categorical columns
        text_parts.append("")
        text_parts.append("Unique Values in Chunk:")
        for column in df.columns:
            if df[column].dtype == 'object' or column in ['State', 'District', 'Pincode']:
                unique_values = df[column].unique()
                if len(unique_values) <= 20:  # Only show if not too many unique values
                    text_parts.append(f"- {column}: {', '.join(map(str, unique_values))}")
                else:
                    text_parts.append(f"- {column}: {len(unique_values)} unique values")
        
        return "\n".join(text_parts)
    
    def process_all(self) -> List[Dict[str, str]]:
        """Main processing pipeline"""
        print("=" * 80)
        print("Starting Aadhaar Data Processing Pipeline")
        print("=" * 80)
        
        # Load CSV files
        dataframes = self.load_csv_files()
        
        if not dataframes:
            # raise ValueError("No CSV files found!")
            print("No CSV files found. Returning empty chunks list.")
            return []
        
        # Create text chunks
        chunks = self.create_text_chunks(dataframes)
        
        print("\n" + "=" * 80)
        print("Data Processing Complete!")
        print("=" * 80)
        
        return chunks

if __name__ == "__main__":
    processor = AadhaarDataProcessor(chunk_size=1000)
    chunks = processor.process_all()
    
    if chunks:
        # Display a sample chunk
        print("\n" + "=" * 80)
        print("Sample Chunk:")
        print("=" * 80)
        print(chunks[0]["text"][:500] + "...")
        print("\nMetadata:", chunks[0]["metadata"])
