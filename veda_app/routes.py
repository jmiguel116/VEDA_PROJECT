from flask import render_template, request, jsonify
from veda_app import create_app
from veda_app.openai_integration import ask_openai
from veda_app.google_vertex_integration import init_vertex_ai, predict_with_vertex_ai

app = create_app()
init_vertex_ai()

@app.route('/')
def index():
    return "Hello, VEDA!"

@app.route('/ask_openai', methods=['POST'])
def ask_openai_endpoint():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    response = ask_openai(prompt)
    return jsonify({'response': response})

@app.route('/predict_vertex_ai', methods=['POST'])
def predict_vertex_ai_endpoint():
    data = request.json
    endpoint_id = data.get('endpoint_id')
    instances = data.get('instances')
    if not endpoint_id or not instances:
        return jsonify({'error': 'Invalid request parameters'}), 400

    prediction = predict_with_vertex_ai(endpoint_id, instances)
    return jsonify({'prediction': prediction})
