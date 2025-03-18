import faiss
import numpy as np
import pickle

# Load FAISS index and metadata
INDEX_PATH = "faiss_index.bin"
METADATA_PATH = "faiss_metadata.pkl"

# Load FAISS index
faiss_index = faiss.read_index(INDEX_PATH)

# Load metadata (maps vector positions to document text)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

def query_faiss(query_text, top_k=5):
    """
    Queries FAISS index to find the most relevant documents.
    :param query_text: User query
    :param top_k: Number of documents to return
    :return: List of relevant documents
    """
    # Convert query to embedding (Assuming OpenAI embeddings)
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")  # Example embedding model
    query_vector = model.encode([query_text]).astype(np.float32)

    # Search in FAISS
    D, I = faiss_index.search(query_vector, top_k)

    # Retrieve documents based on indices
    retrieved_docs = [metadata[i] for i in I[0] if i != -1]
    return retrieved_docs
