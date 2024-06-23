import openai
import os

def ask_openai(question):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        engine="davinci",
        prompt=question,
        max_tokens=100
    )
    return response.choices[0].text.strip()
