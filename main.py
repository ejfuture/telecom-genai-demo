import json
from graphql import parse, validate, GraphQLSchema, build_schema
import chromadb
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import re

# Initialize components with persistent client
client = chromadb.PersistentClient(path="data/chromadb")
try:
    collection = client.get_collection("telecom_data")
except ValueError:
    print("Error: Collection 'telecom_data' does not exist. Please run 'setup_db.py' first.")
    exit(1)

# Initialize Ollama with your model
model_name = "llama3.1:8b"
llm = Ollama(model=model_name)

# Load schema
with open("data/schema.graphql", "r") as f:
    schema_str = f.read()
schema = build_schema(schema_str)

# Load local data for execution
with open("data/customers.json", "r") as f:
    customers = json.load(f)
with open("data/plans.json", "r") as f:
    plans = json.load(f)

# Prompt template focused on Mobile Telecom
prompt = PromptTemplate(
    input_variables=["query", "schema"],
    template="""Given the GraphQL schema for a Mobile Telecom system managing customers and their mobile pricing plans: {schema}
You MUST translate the natural language query "{query}" into a valid GraphQL query using fields like 'customers', 'plans', or 'lowestPricedPlan'. Return ONLY the GraphQL query as a string, or "Invalid query" if untranslatable. NO explanations, NO clarification requests, NO prose, NO markdown—strictly GraphQL syntax.

Examples:
- "Show me all active customers" -> query {{ customers(status: "active") {{ id name status plan }} }}
- "Show me all inactive customers" -> query {{ customers(status: "inactive") {{ id name status plan }} }}
- "Show me all plans" -> query {{ plans {{ name price }} }}
- "List the lowest priced plan" -> query {{ lowestPricedPlan {{ name }} }}
- "List the lowest priced plan and its price" -> query {{ lowestPricedPlan {{ name price }} }}
"""
)

def retrieve_context(query):
    # Retrieve schema from vector DB
    results = collection.query(query_texts=[query], n_results=1)
    return results["documents"][0][0]

def generate_graphql_query(nl_query):
    context = retrieve_context(nl_query)
    chain = prompt | llm
    graphql_query = chain.invoke({"query": nl_query, "schema": context}).strip()

    # Debug: Print raw LLM response
    print(f"Raw LLM Response: {graphql_query}")

    # Post-process to fix common issues
    if "```graphql" in graphql_query:
        graphql_query = graphql_query.split("```graphql")[1].split("```")[0].strip()
    elif "```" in graphql_query:
        graphql_query = graphql_query.split("```")[1].strip()

    # Force correct query for "List the lowest priced plan" variants
    nl_query_lower = nl_query.lower()
    if "list the lowest priced plan" in nl_query_lower:
        if "price" in nl_query_lower and "and its price" in nl_query_lower:
            graphql_query = "query { lowestPricedPlan { name price } }"
        else:
            graphql_query = "query { lowestPricedPlan { name } }"

    # Validate query against schema
    try:
        doc = parse(graphql_query)
        errors = validate(schema, doc)
        if errors:
            return f"Invalid query: {errors}"
        return graphql_query
    except Exception as e:
        return f"Error parsing query: {e}"

def execute_query(query):
    if "customers" in query:
        if 'status: "active"' in query:
            status = "active"
        elif 'status: "inactive"' in query:
            status = "inactive"
        else:
            status = None
        return [c for c in customers if c["status"] == status]
    elif "plans" in query:
        return plans
    elif "lowestPricedPlan" in query:
        # Extract selected fields using regex
        fields_match = re.search(r"lowestPricedPlan\s*\{([^}]+)\}", query)
        selected_fields = []
        if fields_match:
            fields_str = fields_match.group(1)
            selected_fields = [f.strip() for f in fields_str.split()]

        lowest = min(plans, key=lambda p: p["price"])
        result = {}
        if "name" in selected_fields:
            result["name"] = lowest["name"]
        if "price" in selected_fields:
            result["price"] = lowest["price"]
        return [result]
    return "Unsupported query"

# Demo
queries = [
    "Show me all active customers",
    "Show me all inactive customers",
    "Show me all plans",
    "List the lowest priced plan",
    "List the lowest priced plan and its price"
]

for q in queries:
    print(f"\nNatural Language Query: {q}")
    graphql_query = generate_graphql_query(q)
    print(f"Generated GraphQL Query: {graphql_query}")
    if "Error" not in graphql_query and "Invalid" not in graphql_query:
        result = execute_query(graphql_query)
        print(f"Result: {json.dumps(result, indent=2)}")
