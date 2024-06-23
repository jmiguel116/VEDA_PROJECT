import os
import logging
from openai import OpenAI, BadRequestError, AuthenticationError, APIConnectionError, RateLimitError, OpenAIError
import tiktoken

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

if not client.api_key:
    logging.error("OPENAI_API_KEY is not set. Please set the environment variable.")
    raise EnvironmentError("OPENAI_API_KEY is not set. Please set the environment variable.")

# Function to count tokens
def count_tokens(text, model="gpt-3.5-turbo"):
    # Explicitly get the tokenizer
    enc = tiktoken.get_encoding("p50k_base")
    return len(enc.encode(text))

def enhance_ocr_text(ocr_text, model="gpt-3.5-turbo", temperature=0.5):
    """Enhances OCR text using OpenAI API."""
    if not ocr_text.strip():
        logging.error("Empty OCR text provided.")
        raise ValueError("OCR text cannot be empty.")

    prompt = (f"Proofread and enhance the following OCR text, correcting any "
              f"spelling or grammar errors, while preserving the original meaning:\n\n{ocr_text}\n\n")
    logging.debug(f"Prompt: {prompt}")
    
    num_tokens_prompt = count_tokens(prompt, model)
    max_tokens = 4097 - num_tokens_prompt
    logging.debug(f"Num tokens in prompt: {num_tokens_prompt}")
    logging.debug(f"Max tokens for response: {max_tokens}")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        logging.debug(f"Response: {response}")
        enhanced_text = response.choices[0].message.content.strip()
        logging.info("Text has been enhanced successfully.")
        return enhanced_text
    except BadRequestError as e:
        logging.error(f"OpenAI API Bad Request Error: {e}")
        raise
    except AuthenticationError as e:
        logging.error(f"OpenAI API Authentication Error: {e}")
        raise
    except APIConnectionError as e:
        logging.error(f"OpenAI API Connection Error: {e}")
        raise
    except RateLimitError as e:
        logging.error(f"OpenAI API Rate Limit Error: {e}")
        raise
    except OpenAIError as e:
        logging.error(f"OpenAI API General Error: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

# Ensure example usage only runs when script is executed directly
if __name__ == "__main__":
    ocr_text = input("Enter the OCR text to enhance: ")
    try:
        enhanced_text = enhance_ocr_text(ocr_text)
        print("\nEnhanced Text:")
        print(enhanced_text)
    except OpenAIError as e:
        logging.error(f"An OpenAI API error occurred: {e}")
        print(f"An OpenAI API error occurred: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"Error occurred during text enhancement: {e}")
