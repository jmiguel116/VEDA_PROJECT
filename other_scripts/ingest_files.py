import openai

# Setup OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# Create a new vector store for RF data
vector_store = client.create_vector_store(name="RF Data Store")

# List of files to upload
files = ["path/to/file1.csv", "path/to/file2.csv"]

# Upload files to the vector store
for file in files:
    client.upload_file_to_vector_store(
        vector_store_id=vector_store['id'],
        file=open(file, 'rb')
    )

print("Files uploaded to vector store:", vector_store)
