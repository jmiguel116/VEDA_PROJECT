from google.cloud import aiplatform
import os

# Initialize the Vertex AI client
def init_vertex_ai():
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    aiplatform.init(project=project, location=location)

def predict_with_vertex_ai(endpoint_id, instances):
    client_options = {
        "api_endpoint": f"{location}-aiplatform.googleapis.com"
    }
    
    endpoint = aiplatform.Endpoint(endpoint_name=endpoint_id, client_options=client_options)
    
    prediction = endpoint.predict(instances=instances)
    
    return prediction
