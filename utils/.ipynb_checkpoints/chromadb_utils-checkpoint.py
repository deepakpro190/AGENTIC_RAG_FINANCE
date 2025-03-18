import chromadb
import requests
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="finance_docs")

def query_chromadb(user_query):
    results = collection.query(query_texts=[user_query], n_results=3)
    return results['documents'][0] if results['documents'] else []
