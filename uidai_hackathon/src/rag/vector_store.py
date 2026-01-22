"""
Vector Store Manager using Qdrant
Handles embedding creation and vector storage
"""

import os
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
from .data_processor import AadhaarDataProcessor

load_dotenv()


class VectorStoreManager:
    """Manage vector embeddings and Qdrant storage"""
    
    def __init__(self):
        # Load configuration
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("COLLECTION_NAME", "aadhaar_data")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize Qdrant client with timeout settings
        if self.qdrant_url:
            print(f"Connecting to Qdrant at {self.qdrant_url}...")
            self.client = QdrantClient(
                url=self.qdrant_url,
                api_key=self.qdrant_api_key,
                timeout=60  # 60 second timeout
            )
        else:
            print("QDRANT_URL not set. Vector store functionality will be limited.")
            self.client = None
        
        # Initialize embedding model
        print(f"Loading embedding model: {self.embedding_model_name}...")
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            print(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            self.embedding_model = None
            self.embedding_dim = 0
        
    def create_collection(self, recreate: bool = False):
        """Create or recreate the Qdrant collection"""
        if not self.client: return
        
        # Check if collection exists
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if collection_exists:
                if recreate:
                    print(f"Deleting existing collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    print(f"Collection {self.collection_name} already exists")
                    return
            
            # Create new collection
            print(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
            print("Collection created successfully!")
        except Exception as e:
            print(f"Error creating collection: {e}")
        
    def create_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Create embeddings for a list of texts"""
        if not self.embedding_model: return np.array([])
        
        print(f"Creating embeddings for {len(texts)} texts...")
        
        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Encoding batches"):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch, show_progress_bar=False)
            embeddings.append(batch_embeddings)
        
        if embeddings:
            all_embeddings = np.vstack(embeddings)
            print(f"Created {len(all_embeddings)} embeddings")
            return all_embeddings
        return np.array([])
    
    def upload_chunks(self, chunks: List[Dict[str, str]], batch_size: int = 50):
        """Upload text chunks with their embeddings to Qdrant"""
        if not self.client: return

        print("\n" + "=" * 80)
        print("Starting Vector Upload Process")
        print("=" * 80)
        
        # Extract texts
        texts = [chunk["text"] for chunk in chunks]
        
        # Create embeddings
        embeddings = self.create_embeddings(texts)
        if len(embeddings) == 0: return
        
        # Prepare points for upload
        print("\nPreparing points for upload...")
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload={
                    "text": chunk["text"],
                    "metadata": chunk["metadata"]
                }
            )
            points.append(point)
        
        # Upload in batches
        print(f"\nUploading {len(points)} points to Qdrant...")
        try:
            for i in tqdm(range(0, len(points), batch_size), desc="Uploading batches"):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )
            
            print("\n" + "=" * 80)
            print("Upload Complete!")
            print("=" * 80)
            
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            print(f"Total vectors in collection: {collection_info.points_count}")
        except Exception as e:
            print(f"Error uploading to Qdrant: {e}")
        
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar chunks given a query"""
        if not self.client or not self.embedding_model:
            print("Vector store client or embedding model not initialized.")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Try to search using different methods based on client version/type
            search_results = []
            
            # Method 1: Standard search
            if hasattr(self.client, 'search'):
                search_results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k
                )
            # Method 2: query_points (newer versions)
            elif hasattr(self.client, 'query_points'):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=top_k
                )
                search_results = response.points
            # Method 3: query (unified API)
            elif hasattr(self.client, 'query'):
                response = self.client.query(
                    collection_name=self.collection_name,
                    query_vector=query_embedding,
                    limit=top_k
                )
                search_results = response
            else:
                print(f"Error: Qdrant client {type(self.client)} has no recognized search or query method.")
                print(f"Available methods: {[m for m in dir(self.client) if not m.startswith('_')]}")
                return []
            
            # Format results
            results = []
            for result in search_results:
                # Handle different result formats (ScoredPoint vs dict)
                payload = result.payload if hasattr(result, 'payload') else result.get('payload', {})
                score = result.score if hasattr(result, 'score') else result.get('score', 0.0)
                
                results.append({
                    "text": payload.get("text", ""),
                    "metadata": payload.get("metadata", {}),
                    "score": score
                })
            
            return results
        except Exception as e:
            print(f"Error searching vector store: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if not self.client:
            return {"error": "Qdrant client not initialized"}
            
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            return {"error": str(e)}
    
    def populate_from_csv(self, chunk_size: int = 1000, recreate_collection: bool = False):
        """Populate vector database from CSV files
        
        This method integrates data processing and vector upload:
        1. Uses AadhaarDataProcessor to load and process CSV files
        2. Creates the Qdrant collection (if needed)
        3. Uploads all processed chunks to the vector database
        
        Args:
            chunk_size: Number of rows per text chunk
            recreate_collection: Whether to delete and recreate the collection
        """
        print("\n" + "=" * 80)
        print("Populating Vector Database from CSV Files")
        print("=" * 80)
        
        # Step 1: Process CSV files into chunks
        processor = AadhaarDataProcessor(chunk_size=chunk_size)
        chunks = processor.process_all()
        
        if not chunks:
            print("\n⚠ No chunks created. Please ensure processed CSV files exist.")
            print("   Run: python -m uidai_hackathon.src.preprocessor")
            return
        
        # Step 2: Create collection
        self.create_collection(recreate=recreate_collection)
        
        # Step 3: Upload chunks to Qdrant
        self.upload_chunks(chunks)
        
        # Step 4: Display final statistics
        print("\n" + "=" * 80)
        print("Vector Database Population Complete!")
        print("=" * 80)
        stats = self.get_collection_stats()
        if "error" not in stats:
            print(f"✓ Total vectors in collection: {stats['points_count']}")
            print(f"✓ Collection status: {stats['status']}")
        else:
            print(f"⚠ Could not retrieve stats: {stats['error']}")


if __name__ == "__main__":
    # Populate the vector database from CSV files
    vsm = VectorStoreManager()
    
    # Populate from CSV files (set recreate_collection=True to start fresh)
    vsm.populate_from_csv(chunk_size=1000, recreate_collection=False)
