import logging
from google.cloud import vision
import openai
import os
from PIL import Image
import io
import filetype

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass

class OCRError(Exception):
    """Custom exception for OCR errors."""
    pass

class OpenAIError(Exception):
    """Custom exception for OpenAI errors."""
    pass

def process_image(image_path, credentials_path, openai_api_key):
    """ 
    Process the given image to extract and enhance text using OCR and OpenAI.
    
    Parameters:
    - image_path: str, path to the image file
    - credentials_path: str, path to the Google Cloud credentials file
    - openai_api_key: str, OpenAI API key
    
    Returns:
    - str, enhanced text from the image
    """
    try:
        # Check if the image file type is valid
        if not filetype.is_image(image_path):
            raise ImageProcessingError("Invalid image file type.")

        # Set up Google Cloud Vision client
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        client = vision.ImageAnnotatorClient()

        # Load image
        with open(image_path, 'rb') as img_file:
            content = img_file.read()

        image = vision.Image(content=content)

        # Perform OCR using Google Cloud Vision
        response = client.text_detection(image=image)
        texts = response.text_annotations
        if not texts:
            logging.warning("No text detected in the image.")
            raise OCRError("No text detected.")

        # Extract detected text
        detected_text = texts[0].description
        logging.info(f'Detected text: {detected_text}')

        # Enhance text using OpenAI
        openai.api_key = openai_api_key
        enhanced_text = enhance_text_with_openai(detected_text)

        return enhanced_text

    except ImageProcessingError as e:
        logging.error(f"An error occurred during image processing: {e}")
        raise

    except OCRError as e:
        logging.error(f"An error occurred during OCR: {e}")
        raise

    except OpenAIError as e:
        logging.error(f"An error occurred during text enhancement: {e}")
        raise

    except Exception as e:
        logging.error(f"An unknown error occurred during image processing: {e}")
        raise ImageProcessingError(str(e))

def enhance_text_with_openai(text, engine="text-davinci-003"):
    """ 
    Enhance the given text using OpenAI's language model.
    
    Parameters:
    - text: str, the text to enhance
    - engine: str, OpenAI engine to use (default: "text-davinci-003")
    
    Returns:
    - str, enhanced text
    """
    try:
        response = openai.Completion.create(
            engine=engine,
            prompt=f"Enhance the following text:\n\n{text}",
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7
        )
        enhanced_text = response.choices[0].text.strip()
        logging.info(f'Enhanced text: {enhanced_text}')

        return enhanced_text

    except Exception as e:
        logging.error(f"An error occurred during text enhancement: {e}")
        raise OpenAIError(str(e))

# Example usage
if __name__ == "__main__":
    image_path = "path/to/your/image.jpg"
    credentials_path = "path/to/your/credentials.json"
    openai_api_key = "your_openai_api_key"

    try:
        enhanced_text = process_image(image_path, credentials_path, openai_api_key)
        print(f"Enhanced Text: {enhanced_text}")

    except Exception as e:
        print(f"An error occurred: {e}")
