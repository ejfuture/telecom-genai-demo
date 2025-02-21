import json
import chromadb
from langchain_community.embeddings import OllamaEmbeddings
import os

# Ensure the data directory exists
os.makedirs("data/chromadb", exist_ok=True)

# Initialize ChromaDB persistent client
client = chromadb.PersistentClient(path="data/chromadb")

# Check if collection exists, create it if not
try:
    client.get_collection("telecom_data")
    print("Collection 'telecom_data' already exists, resetting it...")
    client.delete_collection("telecom_data")
except ValueError:
    print("Creating new 'telecom_data' collection...")

# Create the collection
collection = client.create_collection("telecom_data")

# Initialize embeddings
try:
    embeddings = OllamaEmbeddings(model="llama3.1:8b")
except Exception as e:
    print(f"Error initializing Ollama embeddings: {e}. Ensure 'ollama serve' is running and 'my-llama3.1:8b' is pulled.")
    exit(1)

# Load schema
try:
    with open("data/schema.graphql", "r") as f:
        schema = f.read()
except FileNotFoundError:
    print("Error: 'data/schema.graphql' not found. Please ensure it exists.")
    exit(1)

# Load data
try:
    with open("data/customers.json", "r") as f:
        customers = json.load(f)
    with open("data/plans.json", "r") as f:
        plans = json.load(f)
except FileNotFoundError as e:
    print(f"Error: {e}. Please ensure 'data/customers.json' and 'data/plans.json' exist.")
    exit(1)

# Add schema to vector DB
collection.add(
    documents=[schema],
    metadatas=[{"type": "schema"}],
    ids=["schema"]
)

# Add customer data
for customer in customers:
    doc = json.dumps(customer)
    collection.add(
        documents=[doc],
        metadatas=[{"type": "customer"}],
        ids=[f"customer_{customer['id']}"]
    )

# Add plan data
for plan in plans:
    doc = json.dumps(plan)
    collection.add(
        documents=[doc],
        metadatas=[{"type": "plan"}],
        ids=[f"plan_{plan['name']}"]
    )

print("Vector database setup complete! Collection 'telecom_data' created and populated in 'data/chromadb'.")
