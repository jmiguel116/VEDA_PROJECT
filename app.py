from flask import Flask, request, jsonify
from combined_ocr_module import process_image
import logging

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr_endpoint():
    try:
        image_file = request.files['image']
        image_path = f'/tmp/{image_file.filename}'
        image_file.save(image_path)
        logging.info(f'Image saved to {image_path}')

        credentials_path = request.form.get('credentials_path')
        logging.info(f'Using credentials from {credentials_path}')

        results = process_image(image_path, credentials_path)
        return jsonify({'ocr_results': results})
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


