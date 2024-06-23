from flask import render_template, request, jsonify
from veda_app import create_app
from veda_app.openai_integration import ask_openai
from veda_app.google_vertex_integration import init_vertex_ai, predict_with_vertex_ai
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Initialize the Flask app and Vertex AI
app = create_app()
init_vertex_ai()

@app.route('/')
def index():
    """Default route for VEDA."""
    return "Hello, VEDA!"

def handle_api_error(error_message, status_code=500):
    """Helper function to handle API errors."""
    logging.error(error_message)
    return jsonify({'error': error_message}), status_code

@app.route('/ask_openai', methods=['POST'])
def ask_openai_endpoint():
    """Endpoint to interact with OpenAI."""
    try:
        data = request.json
        prompt = data.get('prompt')
        if not prompt or not isinstance(prompt, str):
            return handle_api_error("Invalid prompt provided.", 400)
        
        logging.info(f"Received prompt: {prompt}")
        response = ask_openai(prompt)
        logging.info(f"OpenAI response: {response}")
        
        return jsonify({'response': response})
    
    except Exception as e:
        return handle_api_error(f"An error occurred while interacting with OpenAI: {e}")

@app.route('/predict_vertex_ai', methods=['POST'])
def predict_vertex_ai_endpoint():
    """Endpoint to make predictions using Vertex AI."""
    try:
        data = request.json
        endpoint_id = data.get('endpoint_id')
        instances = data.get('instances')
        
        if not endpoint_id or not isinstance(endpoint_id, str):
            return handle_api_error("Invalid endpoint ID provided.", 400)
        
        if not instances or not isinstance(instances, list):
            return handle_api_error("Invalid instances provided.", 400)
        
        logging.info(f"Endpoint ID: {endpoint_id}, Instances: {instances}")
        prediction = predict_with_vertex_ai(endpoint_id, instances)
        logging.info(f"Vertex AI prediction: {prediction}")
        
        return jsonify({'prediction': prediction})
    
    except Exception as e:
        return handle_api_error(f"An error occurred while making predictions with Vertex AI: {e}")

if __name__ == '__main__':
    # Use environment variables for configuration
    debug = os.getenv('FLASK_DEBUG', 'true').lower() in ['true', '1', 't']
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=debug, port=port)
