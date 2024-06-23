from google.cloud import aiplatform
import os

def init_vertex_ai():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    aiplatform.init(project=project_id, location=location)

def predict_with_vertex_ai(endpoint_name, instances):
    client = aiplatform.gapic.PredictionServiceClient()
    endpoint = client.endpoint_path(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        endpoint=endpoint_name,
    )
    response = client.predict(
        endpoint=endpoint,
        instances=instances,
    )
    return response.predictions
