import os
import logging
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def set_credentials(credentials_path=None):
    """ Set the Google Cloud credentials environment variable. """
    if credentials_path:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        logging.info("Credentials path set.")
    elif 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
        logging.error("Google Cloud credentials are not set.")
        raise EnvironmentError("Google Cloud credentials are not set. Please provide a credentials path.")

def perform_ocr(image_path):
    """Performs OCR on an image using Google Cloud Vision.
    
    Args:
        image_path: The path to the image file.
    
    Returns:
        list: A list of TextAnnotation objects containing the detected text.
    """
    client = vision_v1.ImageAnnotatorClient()
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
        image = types.Image(content=content)
        response = client.text_detection(image=image)
    
    if response.error.message:
        logging.error(f"Error during OCR: {response.error.message}")
        raise Exception(f"Error during OCR: {response.error.message}")
    
    return response.text_annotations

def main():
    image_path = input("Enter the path to your image: ")
    credentials_path = input("Enter the path to your Google Cloud credentials JSON file (optional): ")
    set_credentials(credentials_path)

    try:
        texts = perform_ocr(image_path)
        print("\nExtracted Text:")
        for text in texts:
            print(text.description)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
