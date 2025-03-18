import os
import faiss
import pickle
import uuid
import numpy as np
from sentence_transformers import SentenceTransformer

# Paths for FAISS index and metadata
FAISS_INDEX_PATH = "faiss_index.bin"
METADATA_PATH = "faiss_metadata.pkl"

# Load embedding model (can replace with OpenAI or other models)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index (or load existing one)
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
else:
    index = faiss.IndexFlatL2(model.get_sentence_embedding_dimension())
    metadata = {}  # Dictionary to store document texts

def embed_document(file_path):
    """ Reads a text file, generates embedding, and stores it in FAISS """
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Generate embedding
    embedding = model.encode([text]).astype(np.float32)

    # Assign a unique document ID
    doc_id = str(uuid.uuid4())
    
    # Add to FAISS index
    index.add(embedding)

    # Store text metadata
    metadata[len(metadata)] = text

    # Save updated FAISS index and metadata
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"✅ Successfully embedded '{file_path}' into FAISS.")

# Example Usage
if __name__ == "__main__":
    file_path = "docs/d1.txt"  # Change to your document name
    embed_document(file_path)
