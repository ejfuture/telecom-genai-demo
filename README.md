**Telecom GenAI Demo**
This a work in progress.
A demo that translates NL queries into GraphQL requests using local Ollama and ChromaDB vector database.

**Architecture Diagram**
[User NL Query] --> [Python App] --> [Ollama Local Model (LLaMA 3)]
                        |                   |
                        v                   v
[ChromaDB Vector Store] <--> [GraphQL Schema + Customer/Plan Data]
                        |
                        v
[Generated GraphQL Query] --> [Execute Against Local Data] --> [Response]


Solution Explanation

1. Schema Adherence: Validate generated GraphQL queries against a predefined schema using a GraphQL parser and reject invalid operations.
2. Hallucination Prevention: RAG retrieves the schema and sample data, ensuring the model generates queries grounded in real context.
3. Chunking Strategy: Schema and data are stored as small, structured chunks (e.g., per type/field) in the vector DB for precise retrieval.
4. Foundation Model: We'll use LLaMA 3 (8B) via Ollama locally because it's lightweight, performs well on structured tasks, and runs efficiently on my M2 laptop.

----

**Step-by-Step Setup and Running Instructions**
Homebrew (install with: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)")
Python 3.11+ (if not already installed, install with: brew install python)
Ollama (install with: brew install ollama, then start it with "ollama serve" or from Homebrew "brew services start ollama"")
Git (install with: brew install git)

# Create a project directory
mkdir telecom-genai-demo
cd telecom-genai-demo
git init # if using git

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install chromadb graphql-core langchain ollama

# Install dependencies
pip install chromadb graphql-core langchain ollama

# Pull LLaMA 3 (8B) model
ollama pull llama3

# Verify it's running
ollama list

telecom-genai-demo/
|-- data/
|   |-- customers.json      # Customer data
|   |-- plans.json          # Plan data
|   |-- schema.graphql      # GraphQL schema
|-- main.py                 # Main application
|-- setup_db.py             # Vector DB setup
|-- README.md               # Instructions
|-- requirements.txt        # Dependencies

Define the GraphQL Schema
File: data/schema.graphql

type Customer {
  id: ID!
  name: String!
  status: String!
  plan: String!
}

type Plan {
  name: String!
  price: Float!
}

type Query {
  customers(status: String): [Customer!]!
  plans: [Plan!]!
  lowestPricedPlan: Plan!
}


Adding Some Data
File: data/customers.json

[
  {"id": "1", "name": "John Doe", "status": "active", "plan": "Basic"},
  {"id": "2", "name": "Jane Smith", "status": "inactive", "plan": "Premium"},
  {"id": "3", "name": "Bob Johnson", "status": "active", "plan": "Pro"},
  {"id": "4", "name": "Alice Brown", "status": "active", "plan": "Basic"},
  {"id": "5", "name": "Charlie Wilson", "status": "inactive", "plan": "Pro"},
  {"id": "6", "name": "David Lee", "status": "active", "plan": "Premium"},
  {"id": "7", "name": "Emma Davis", "status": "active", "plan": "Basic"},
  {"id": "8", "name": "Frank Miller", "status": "inactive", "plan": "Pro"},
  {"id": "9", "name": "Grace Taylor", "status": "active", "plan": "Premium"},
  {"id": "10", "name": "Henry White", "status": "inactive", "plan": "Basic"}
]

File: data/plans.json
[
  {"name": "Basic", "price": 10.99},
  {"name": "Pro", "price": 19.99},
  {"name": "Premium", "price": 29.99}
]

Set Up the Vector Database
File: setup_db.py

import json
from chromadb import Client
from langchain.embeddings import OllamaEmbeddings

# Initialize ChromaDB and embeddings
client = Client()
collection = client.create_collection("telecom_data")
embeddings = OllamaEmbeddings(model="llama3")

# Load schema
with open("data/schema.graphql", "r") as f:
    schema = f.read()

# Load data
with open("data/customers.json", "r") as f:
    customers = json.load(f)
with open("data/plans.json", "r") as f:
    plans = json.load(f)

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

print("Vector database setup complete!")


Now run the Vector DB setup
    python setup_db.py

For the main.py see file main.py

Requirements File
File: requirements.txt

chromadb==0.4.24
graphql-core==3.2.3
langchain==0.1.0
ollama==0.1.7

Try running the main.py program
    python main.py
