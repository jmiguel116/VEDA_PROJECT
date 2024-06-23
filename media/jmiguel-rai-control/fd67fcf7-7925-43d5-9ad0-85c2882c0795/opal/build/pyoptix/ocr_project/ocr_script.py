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
