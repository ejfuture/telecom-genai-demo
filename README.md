# Telecom GenAI Demo
This a work in progress.
A demo that translates NL queries into GraphQL requests using local Ollama and ChromaDB vector database.

The action: Come up with a demo/PoC that meets the following criteria. Read on for the details.

**Problem Statement**
Develop a GenAI-powered system that accurately translates natural language (NL) queries into GraphQL requests by dynamically retrieving the GraphQL schema and parameters.

The solution must ensure that generated queries strictly adhere to the schema, preventing hallucinations by leveraging Retrieval-Augmented Generation (RAG) or structured context injection.

**Challenges**
1. How do we ensure that a GenAI system is only responding to the GraphQL operations that are validated and can be executed against the schema verses a non existing operation that does not exist in the ingested schema. For example if the schema does not contain "listUsers" and an attempt to call it is made, then it would be rejected.
2. How do we avoid generating false positives and false negatives, hallucinations?
3. What kind of chunking can help here?
4. What Foundation models and why?

**Deliverable**
- Architectrure Diagram
- Explanation of functionality
- Develop a schema to go along with it
- Example data



**Architecture Diagram**
```
[User NL Query] --> [Python App] --> [Ollama Local Model (LLaMA 3)]
                        |                   |
                        v                   v
[ChromaDB Vector Store] <--> [GraphQL Schema + Customer/Plan Data]
                        |
                        v
[Generated GraphQL Query] --> [Execute Against Local Data] --> [Response]
```

Solution Explanation

1. Schema Adherence: Validate generated GraphQL queries against a predefined schema using a GraphQL parser and reject invalid operations.
2. Hallucination Prevention: RAG retrieves the schema and sample data, ensuring the model generates queries grounded in real context.
3. Chunking Strategy: Schema and data are stored as small, structured chunks (e.g., per type/field) in the vector DB for precise retrieval.
4. Foundation Model: We'll use llama3.1:8b via Ollama locally because it's reasonably lightweight, performs well on structured tasks, and runs efficiently.

This runs on my MacBook Pro M2 laptop.

---

## Step-by-Step Setup and Running Instructions
Homebrew install: 

  ```/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"```


Python 3.11+ (if not already installed:
```
brew install python)
```

Ollama install: 
```
  brew install ollama
```

You may start it with
```
"ollama serve" or from Homebrew "brew services start ollama""
```

Git install: 
```
  brew install git
```

---

**Project folder structure**
```
telecom-genai-demo/
|-- data/
|   |-- customers.json      # Customer data
|   |-- plans.json          # Plan data
|   |-- schema.graphql      # GraphQL schema
|-- main.py                 # Main application
|-- setup_db.py             # Vector DB setup
|-- README.md               # Instructions
|-- requirements.txt        # Dependencies
```

**Create a project directory**
```
  mkdir telecom-genai-demo
  cd telecom-genai-demo
  git init # if using git
```

**Create a virtual environment**
```
  python3 -m venv venv
  source venv/bin/activate
```

**Install dependencies**
```
  pip install chromadb graphql-core langchain ollama
```

**Pull LLaMA 3.1:8b (8B) model**
```
  ollama pull llama3.1:8b
```

**Verify it's running**
```
  ollama list
```

GraphQL Schema
Files:
``` 
touch data/schema.graphql
touch data/customers.json
touch data/plans.json
```

Create the Vector Database
```
python setup_db.py
```
Requirements File
File: requirements.txt
```
python==3.11.11
chromadb==0.4.24
graphql-core==3.2.3
langchain==0.1.0
ollama==0.1.7
```
Try running the main.py program
```
python main.py
```
----

After setup and running the program the output should look like this:

```
python main.py

Natural Language Query: Show me all active customers
Raw LLM Response: query { customers(status: "active") { id name status plan } }
Generated GraphQL Query: query { customers(status: "active") { id name status plan } }
Result: [
  {
    "id": "1",
    "name": "John Doe",
    "status": "active",
    "plan": "Basic"
  },
  {
    "id": "3",
    "name": "Bob Johnson",
    "status": "active",
    "plan": "Pro"
  },
  {
    "id": "4",
    "name": "Alice Brown",
    "status": "active",
    "plan": "Basic"
  },
  {
    "id": "6",
    "name": "David Lee",
    "status": "active",
    "plan": "Premium"
  },
  {
    "id": "7",
    "name": "Emma Davis",
    "status": "active",
    "plan": "Basic"
  },
  {
    "id": "9",
    "name": "Grace Taylor",
    "status": "active",
    "plan": "Premium"
  }
]

Natural Language Query: Show me all inactive customers
Raw LLM Response: query { customers(status: "inactive") { id name status plan } }
Generated GraphQL Query: query { customers(status: "inactive") { id name status plan } }
Result: [
  {
    "id": "2",
    "name": "Jane Smith",
    "status": "inactive",
    "plan": "Premium"
  },
  {
    "id": "5",
    "name": "Charlie Wilson",
    "status": "inactive",
    "plan": "Pro"
  },
  {
    "id": "8",
    "name": "Frank Miller",
    "status": "inactive",
    "plan": "Pro"
  },
  {
    "id": "10",
    "name": "Henry White",
    "status": "inactive",
    "plan": "Basic"
  }
]

Natural Language Query: Show me all plans
Raw LLM Response: query { plans { name price } }
Generated GraphQL Query: query { plans { name price } }
Result: [
  {
    "name": "Basic",
    "price": 10.99
  },
  {
    "name": "Pro",
    "price": 19.99
  },
  {
    "name": "Premium",
    "price": 29.99
  }
]

Natural Language Query: List the lowest priced plan
Raw LLM Response: query { plans(sort: "price") { name price } }
Generated GraphQL Query: query { lowestPricedPlan { name } }
Result: [
  {
    "name": "Basic"
  }
]

Natural Language Query: List the lowest priced plan and its price
Raw LLM Response: query { lowestPricedPlan { name price } }
Generated GraphQL Query: query { lowestPricedPlan { name price } }
Result: [
  {
    "name": "Basic",
    "price": 10.99
  }
]

```
---

# More about the journey

## Testing with custom models
I found that each model had its own quirks regarding *"understanding"* the natural languare and returning GraphQL formatted response.


```
FROM llama3.1:8b
PARAMETER temperature 0.1
PARAMETER top_p 0.5
PARAMETER top_k 10
PARAMETER stop <|start_header_id|>
PARAMETER stop <|end_header_id|>
PARAMETER stop <|eot_id|>
SYSTEM You are a strict GraphQL query generator for a Mobile Telecom system. Respond ONLY with a valid GraphQL query that adheres to the provided schema, focusing on mobile telecom customers and their pricing plans. Return "Invalid query" if untranslatable. NO explanations, NO prose, NO markdown, NO questions—strictly GraphQL syntax. Use quoted strings (e.g., "active") and include subfields for non-scalar types (e.g., Customer, Plan).
SYSTEM Examples:
SYSTEM - "Show me all active customers" -> query { customers(status: "active") { id name status plan } }
SYSTEM - "Show me all inactive customers" -> query { customers(status: "inactive") { id name status plan } }
SYSTEM - "Show me all plans" -> query { plans { name price } }
SYSTEM - "List the lowest priced plan" -> query { lowestPricedPlan { name } }
SYSTEM - "List the lowest priced plan and its price" -> query { lowestPricedPlan { name price } }
TEMPLATE """
{{- if .System }}<|start_header_id|>system<|end_header_id>
{{ .System }}<|eot_id>
{{- end }}
<|start_header_id|>user<|end_header_id>
{{ .Content }}<|eot_id>
<|start_header_id|>assistant<|end_header_id>
"""
```
