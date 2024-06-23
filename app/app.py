from flask import Flask, request, jsonify
from combined_ocr_module import process_image
import logging
import os
import tempfile
import filetype

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    """
    Endpoint to handle OCR processing requests.
    Expects an image file and optional credentials path in the form data.
    """
    try:
        # Retrieve the uploaded image file from the request
        image_file = request.files['image']
        
        # Validate the file type
        if not filetype.guess(image_file.stream):
            logging.warning('Invalid image file received.')
            return jsonify({'error': 'Invalid image file'}), 400
        
        # Save the image file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            image_path = temp_file.name
            image_file.save(image_path)
            logging.info(f'Image saved to {image_path}')

        # Retrieve credentials path from the form data
        credentials_path = request.form.get('credentials_path')
        if credentials_path:
            logging.info(f'Using credentials from {credentials_path}')
        else:
            logging.warning('No credentials path provided.')

        # Process the image using the combined OCR module
        results = process_image(image_path, credentials_path)
        return jsonify({'ocr_results': results})
    
    except KeyError as e:
        error_message = f"Missing form data: {e}"
        logging.error(error_message)
        return jsonify({'error': error_message}), 400
    
    except FileNotFoundError as e:
        error_message = f"Credentials file not found: {e}"
        logging.error(error_message)
        return jsonify({'error': error_message}), 400
    
    except Exception as e:
        error_message = f"An error occurred: {e}"
        logging.error(error_message)
        return jsonify({'error': error_message}), 500
    
    finally:
        # Ensure the temporary image file is deleted after processing
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
            logging.info(f'Temporary image file {image_path} deleted.')

if __name__ == '__main__':
    # Use environment variables for configuration
    debug = os.getenv('FLASK_DEBUG', 'true').lower() in ['true', '1', 't']
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug, port=port)
