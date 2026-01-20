
import os
import shutil
from pathlib import Path

BASE_DIR = Path(r"c:\Users\hites\Downloads\aadhaar_biometric")
SOURCE_DIR = BASE_DIR / "AADHAAR-HACKATHON"
TARGET_DIR = BASE_DIR / "uidai_hackathon"

# Define destination mappings
DESTINATIONS = {
    ".html": TARGET_DIR / "outputs" / "reports",
    ".ipynb": TARGET_DIR / "notebooks",
    ".geojson": TARGET_DIR / "data" / "geojson",
    ".json": TARGET_DIR / "data" / "mappings",
    ".png": TARGET_DIR / "outputs" / "figures" / "legacy", # Move static images to legacy
}

# Specific folders
DIRECTORIES_TO_MOVE = {
    "monthly_heatmaps": TARGET_DIR / "outputs" / "figures" / "monthly_heatmaps"
}

def move_files():
    print(f"Starting merge from {SOURCE_DIR} to {TARGET_DIR}")
    
    if not SOURCE_DIR.exists():
        print("Source directory not found. Already merged?")
        return

    # Create directories
    for dest in DESTINATIONS.values():
        os.makedirs(dest, exist_ok=True)
        
    for item in os.listdir(SOURCE_DIR):
        s = SOURCE_DIR / item
        
        if s.is_file():
            ext = s.suffix.lower()
            if ext in DESTINATIONS:
                d = DESTINATIONS[ext] / item
                shutil.move(str(s), str(d))
                print(f"Moved {item} -> {DESTINATIONS[ext]}")
            else:
                print(f"Skipped {item} (unknown extension)")
                
        elif s.is_dir():
            if item in DIRECTORIES_TO_MOVE:
                d = DIRECTORIES_TO_MOVE[item]
                if d.exists():
                    shutil.rmtree(d) # Replace if exists
                shutil.move(str(s), str(d))
                print(f"Moved directory {item} -> {d}")
            elif item != ".git": # Ignore git
                # Move generic folders to notebooks or data?
                # Let's leave them if they are unknown
                print(f"Skipped directory {item}")

    print("Merge complete.")

if __name__ == "__main__":
    move_files()
