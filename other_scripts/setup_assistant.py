import openai
import os

# Setup OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# Create the assistant with the new API v2
assistant = client.create_assistant(
    name="RF Design Assistant",
    model="gpt-4-turbo",
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"}
    ],
    tool_resources={
        "file_search": {
            "vector_store_ids": ["vs_rf_data"]
        },
        "code_interpreter": {
            "file_ids": ["file-123", "file-456"]
        }
    }
)

print("Assistant created:", assistant)
