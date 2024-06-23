from google_vision_ocr import perform_ocr, set_credentials
from openai_post_processing import enhance_ocr_text
import logging

def process_image(image_path, credentials_path=None):
    set_credentials(credentials_path)
    ocr_texts = perform_ocr(image_path)
    enhanced_texts = [enhance_ocr_text(text.description) for text in ocr_texts]
    return enhanced_texts

# Ensure example usage only runs when script is executed directly
if __name__ == "__main__":
    image_path = input("Enter the path to your image: ")
    credentials_path = input("Enter the path to your Google Cloud credentials JSON file (optional): ")
    try:
        results = process_image(image_path, credentials_path)
        print("\nEnhanced Texts:")
        for result in results:
            print(result)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
