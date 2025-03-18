import os
import chromadb
from transformers import AutoTokenizer
import uuid

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="finance_docs")

# Load Tokenizer (to check token limits)
tokenizer = AutoTokenizer.from_pretrained("facebook/opt-1.3b")
MAX_TOKENS = 1024  # Safe limit for OPT-1.3B

def embed_document(file_path):
    """ Reads a text file, chunks it, and stores it in ChromaDB """
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found.")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Truncate if needed
    tokens = tokenizer.tokenize(text)
    if len(tokens) > MAX_TOKENS:
        text = tokenizer.convert_tokens_to_string(tokens[:MAX_TOKENS])
    
    doc_id = str(uuid.uuid4())  # Unique ID for the document
    collection.add(ids=[doc_id], documents=[text])
    
    print(f"✅ Successfully embedded '{file_path}' into ChromaDB.")

# Example Usage
if __name__ == "__main__":
    file_path = "docs/d1.txt"  # Change to your document name
    embed_document(file_path)
