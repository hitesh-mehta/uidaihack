"""
Test script to verify RAG migration to processed folder
"""

import sys
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

print("=" * 80)
print("RAG Migration Verification Test")
print("=" * 80)

# Test 1: Config paths
print("\n[Test 1] Verifying config paths...")
try:
    from uidai_hackathon.src import config
    import os
    
    print(f"✓ RAG_BIOMETRIC_PATH: {config.RAG_BIOMETRIC_PATH}")
    print(f"  Exists: {os.path.exists(config.RAG_BIOMETRIC_PATH)}")
    
    print(f"✓ RAG_DEMO_PATH: {config.RAG_DEMO_PATH}")
    print(f"  Exists: {os.path.exists(config.RAG_DEMO_PATH)}")
    
    print(f"✓ RAG_ENROLMENT_PATH: {config.RAG_ENROLMENT_PATH}")
    print(f"  Exists: {os.path.exists(config.RAG_ENROLMENT_PATH)}")
    
    # Verify paths point to processed folder
    assert "processed" in str(config.RAG_BIOMETRIC_PATH), "RAG_BIOMETRIC_PATH should point to processed folder"
    assert "processed" in str(config.RAG_DEMO_PATH), "RAG_DEMO_PATH should point to processed folder"
    assert "processed" in str(config.RAG_ENROLMENT_PATH), "RAG_ENROLMENT_PATH should point to processed folder"
    
    print("\n✅ Test 1 PASSED: All RAG paths point to processed folder")
    
except Exception as e:
    print(f"\n❌ Test 1 FAILED: {e}")
    sys.exit(1)

# Test 2: Data Processor can load files
print("\n[Test 2] Testing data processor...")
try:
    from uidai_hackathon.src.rag.data_processor import AadhaarDataProcessor
    
    processor = AadhaarDataProcessor(chunk_size=500)
    
    # Check csv_map uses correct keys
    expected_keys = {"master_enrolment.csv", "master_biometric.csv", "master_demo.csv"}
    actual_keys = set(processor.csv_map.keys())
    
    assert expected_keys == actual_keys, f"CSV map keys don't match. Expected: {expected_keys}, Got: {actual_keys}"
    
    print(f"✓ CSV map keys are correct: {list(processor.csv_map.keys())}")
    
    # Try loading files (if they exist)
    dataframes = processor.load_csv_files()
    
    if dataframes:
        print(f"✓ Loaded {len(dataframes)} CSV files successfully")
        for name, df in dataframes.items():
            print(f"  - {name}: {len(df)} rows")
        print("\n✅ Test 2 PASSED: Data processor works with processed files")
    else:
        print("⚠ No files loaded (processed files may not exist yet)")
        print("  This is expected if preprocessor hasn't been run")
        print("\n✅ Test 2 PASSED: Data processor configured correctly")
    
except Exception as e:
    print(f"\n❌ Test 2 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Verify old RAG_DATA_DIR is removed
print("\n[Test 3] Verifying RAG_DATA_DIR removal...")
try:
    from uidai_hackathon.src import config
    
    # This should fail now
    try:
        _ = config.RAG_DATA_DIR
        print("❌ RAG_DATA_DIR still exists in config - should be removed!")
        sys.exit(1)
    except AttributeError:
        print("✓ RAG_DATA_DIR successfully removed from config")
        print("\n✅ Test 3 PASSED: Old RAG_DATA_DIR removed")
        
except Exception as e:
    print(f"\n❌ Test 3 FAILED: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED! ✅")
print("=" * 80)
print("\nMigration Summary:")
print("- RAG paths now point to processed folder")
print("- Data processor uses master_*.csv files")
print("- Old RAG_DATA_DIR constant removed")
print("\nNext steps:")
print("1. Run preprocessor if processed files don't exist:")
print("   python uidai_hackathon/src/preprocessor.py")
print("2. Test full RAG pipeline (vector store + chatbot)")
print("3. After verification, remove rag_data directory")
print("=" * 80)
