import openai

# Setup OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# Assistant ID (from setup_assistant.py output)
assistant_id = "your_assistant_id"

# Query for RF propagation data
query = "Retrieve RF propagation data for 800 MHz frequency"

# Run the query
response = client.run_assistant_query(
    assistant_id=assistant_id,
    instructions="Use the file_search tool to find relevant data.",
    tool_choice="file_search",
    query=query
)

print("Query response:", response)
