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

**Create a project directory**
mkdir telecom-genai-demo
cd telecom-genai-demo
git init # if using git

**Create a virtual environment**
python3 -m venv venv
source venv/bin/activate

**Install dependencies**
pip install chromadb graphql-core langchain ollama

# Pull LLaMA 3.1:8b (8B) model
ollama pull llama3.1:8b

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

GraphQL Schema
Files: 
data/schema.graphql
data/customers.json
data/plans.json

Set Up the Vector Database
File: setup_db.py

Requirements File
File: requirements.txt

chromadb==0.4.24
graphql-core==3.2.3
langchain==0.1.0
ollama==0.1.7

Try running the main.py program
    python main.py
