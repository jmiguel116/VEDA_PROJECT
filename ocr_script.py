<<<<<<< HEAD
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set Tesseract path based on your environment
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update this path as needed

# Set Tesseract configuration (optional)
custom_config = r'--oem 3 --psm 6'  # Example configuration for better accuracy

def preprocess_image(image_path, contrast_level=2.0, sharpen_radius=2.0):
    """
    Preprocesses the image for better OCR results.

    Args:
        image_path (str): Path to the image file.
        contrast_level (float): Factor to enhance contrast (default: 2.0).
        sharpen_radius (float): Radius for image sharpening (default: 2.0).

    Returns:
        PIL.Image: The preprocessed image.
    """
    try:
        with Image.open(image_path) as image:
            image = image.convert('L')  # Grayscale conversion
            image = image.filter(ImageFilter.UnsharpMask(radius=sharpen_radius))  # Sharpening
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast_level)
            return image
    except FileNotFoundError:
        logging.error(f"Image not found at {image_path}")
        raise
    except Exception as e:  # Catch more specific exceptions if needed
        logging.error(f"Image preprocessing failed: {e}")
        raise

def perform_ocr(image, config=custom_config):
    """
    Performs OCR on the given image using Tesseract.

    Args:
        image (PIL.Image): The preprocessed image.
        config (str): Tesseract configuration string (optional).

    Returns:
        str: The extracted text.
    """
    try:
        return pytesseract.image_to_string(image, config=config)
    except Exception as e:  # Catch more specific exceptions if needed
        logging.error(f"OCR failed: {e}")
        raise

def save_text_to_file(text, file_path):
    """
    Saves the extracted text to a file.

    Args:
        text (str): The extracted text.
        file_path (str): Path to the output text file.
    """
    try:
        with open(file_path, 'w') as file:
            file.write(text)
    except Exception as e:
        logging.error(f"Failed to save text to file: {e}")
        raise

def main():
    # Configuration (make these command-line arguments or use a config file for flexibility)
    image_path = 'path_to_your_image.jpg'  # Update this path to your actual image path
    output_file_path = 'extracted_text.txt'  # Update this path to your desired output file path

    preprocessed_image = preprocess_image(image_path)
    text = perform_ocr(preprocessed_image)
    save_text_to_file(text, output_file_path)
    logging.info(f"OCR completed. Results saved to {output_file_path}")

if __name__ == "__main__":
    main()
=======
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

def process_image(image_path, credentials_path, openai_api_key, engine="text-davinci-003"):
    """Process the given image to extract and enhance text using OCR and OpenAI.
    
    Parameters:
    - image_path: str, path to the image file or URL
    - credentials_path: str, path to the Google Cloud credentials file
    - openai_api_key: str, OpenAI API key
    - engine: str, OpenAI engine to use (default: "text-davinci-003")
    
    Returns:
    - str, enhanced text from the image
    """
    try:
        # Set up Google Cloud Vision client
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        client = vision.ImageAnnotatorClient()
        
        # Load image and validate file type
        kind = filetype.guess(image_path)
        if kind is None:
            logging.error(f"Invalid file type: {image_path}")
            raise ImageProcessingError("Invalid file type.")
        
        image = Image.open(image_path)
        image_bytes = io.BytesIO()
        image.save(image_bytes, format=kind.extension)
        content = image_bytes.getvalue()
        
        # Perform OCR using Google Cloud Vision
        response = client.text_detection(image=vision.Image(content=content))
        texts = response.text_annotations
        if not texts:
            logging.warning("No text detected in the image.")
            raise OCRError("No text detected.")
        
        # Choose the text annotation with the highest confidence
        best_text = max(texts, key=lambda text: text.confidence)
        extracted_text = best_text.description
        
        # Enhance text using OpenAI
        openai.api_key = openai_api_key
        prompt = f"Original text: {extracted_text}\nEnhance the text:"
        response = openai.Completion.create(engine=engine, prompt=prompt, max_tokens=200, temperature=0.7)
        enhanced_text = response.choices[0].text.strip()
        
        logging.info(f"Enhanced text: {enhanced_text}")
        return enhanced_text
    
    except FileNotFoundError as e:
        logging.error(f"File not found: {e.filename}")
        raise ImageProcessingError("File not found.")
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

# Example Usage
if __name__ == "__main__":
    image_path = "path/to/image.jpg"
    credentials_path = "path/to/credentials.json"
    openai_api_key = "YOUR_OPENAI_API_KEY"
    try:
        enhanced_text = process_image(image_path, credentials_path, openai_api_key)
        print(f"Enhanced Text: {enhanced_text}")
    except Exception as e:
        print(f"An error occurred: {e}")
>>>>>>> 516a66495 (Reinitialize repository and add files)
