
import sys
import os
from pathlib import Path

# Add project root to path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.append(str(project_root))

print(f"Project root: {project_root}")

try:
    from uidai_hackathon.src import config
    print("✅ Config imported successfully")
    
    # Verify processed files exist for RAG
    processed_files = [
        ("Biometric (RAG)", config.RAG_BIOMETRIC_PATH),
        ("Demo (RAG)", config.RAG_DEMO_PATH),
        ("Enrolment (RAG)", config.RAG_ENROLMENT_PATH)
    ]
    
    print("\nChecking processed files for RAG:")
    all_exist = True
    for name, path in processed_files:
        if os.path.exists(path):
            print(f"  ✓ {name}: Found at {path}")
        else:
            print(f"  ✗ {name}: Missing at {path}")
            all_exist = False
    
    if not all_exist:
        print("\n⚠ Some processed files are missing!")
        print("   → Run: python uidai_hackathon/src/preprocessor.py")
        print("   This will generate the required files from raw data.")
        
except Exception as e:
    print(f"❌ Config import failed: {e}")

try:
    from uidai_hackathon.src.rag.data_processor import AadhaarDataProcessor
    print("\n✅ DataProcessor imported successfully")
except Exception as e:
    print(f"\n❌ DataProcessor import failed: {e}")

try:
    from uidai_hackathon.src.rag.vector_store import VectorStoreManager
    print("✅ VectorStoreManager imported successfully")
except Exception as e:
    print(f"❌ VectorStoreManager import failed: {e}")

try:
    from uidai_hackathon.src.rag.rag_chatbot import RAGChatbot
    print("✅ RAGChatbot imported successfully")
except Exception as e:
    print(f"❌ RAGChatbot import failed: {e}")

print("\n" + "="*60)
print("Import verification complete.")
print("="*60)
