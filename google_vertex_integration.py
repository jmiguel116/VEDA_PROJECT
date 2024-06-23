<<<<<<< HEAD
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
=======
import logging
from google.cloud import aiplatform
import os
import yaml
from google.api_core.exceptions import NotFound, InvalidArgument

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class VertexAIError(Exception):
    """Custom exception for Google Vertex AI errors."""

def initialize_vertex_ai(credentials_path, project_id, location="us-central1"):
    """Initialize Google Vertex AI with the provided credentials and project details.

    Args:
        credentials_path (str): Path to the Google Cloud credentials file.
        project_id (str): Google Cloud project ID.
        location (str, optional): Vertex AI region. Defaults to "us-central1".

    Raises:
        VertexAIError: If an error occurs during initialization.
    """
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        aiplatform.init(project=project_id, location=location)
        logging.info("Google Vertex AI initialized.")
    except FileNotFoundError as e:
        error_message = f"Credentials file not found: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)
    except Exception as e:
        error_message = f"Failed to initialize Google Vertex AI: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)

def upload_model_to_vertex_ai(model_path, display_name, project_id, location="us-central1"):
    """Upload a model to Google Vertex AI.

    Args:
        model_path (str): Path to the model file.
        display_name (str): Display name for the model in Vertex AI.
        project_id (str): Google Cloud project ID.
        location (str, optional): Vertex AI region. Defaults to "us-central1".

    Returns:
        model: The uploaded model.

    Raises:
        VertexAIError: If an error occurs during model upload.
    """
    try:
        model = aiplatform.Model.upload(
            display_name=display_name,
            artifact_uri=model_path,
            project=project_id,
            location=location,
        )
        logging.info(f"Model uploaded successfully: {model.resource_name}")
        return model
    except Exception as e:
        error_message = f"Failed to upload model to Vertex AI: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)

def deploy_model_to_endpoint(model, endpoint_name, project_id, location="us-central1"):
    """Deploy a model to an endpoint in Google Vertex AI.

    Args:
        model (Model): The model to deploy.
        endpoint_name (str): Name of the endpoint to deploy the model to.
        project_id (str): Google Cloud project ID.
        location (str, optional): Vertex AI region. Defaults to "us-central1".

    Returns:
        endpoint: The deployed endpoint.

    Raises:
        VertexAIError: If an error occurs during model deployment.
    """
    try:
        endpoint = aiplatform.Endpoint.create(
            display_name=endpoint_name,
            project=project_id,
            location=location,
        )
        model.deploy(endpoint=endpoint)
        logging.info(f"Model deployed to endpoint: {endpoint.resource_name}")
        return endpoint
    except Exception as e:
        error_message = f"Failed to deploy model to endpoint: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)

def predict_with_vertex_ai(endpoint, instances):
    """Make predictions using a deployed model in Google Vertex AI.

    Args:
        endpoint (Endpoint): The endpoint to use for prediction.
        instances (list): List of instances for prediction.

    Returns:
        list: Predictions from the model.

    Raises:
        VertexAIError: If an error occurs during prediction.
    """
    try:
        predictions = endpoint.predict(instances=instances).predictions
        logging.info(f"Predictions: {predictions}")
        return predictions
    except NotFound as e:
        error_message = f"Model or endpoint not found: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)
    except InvalidArgument as e:
        error_message = f"Invalid input data: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)
    except Exception as e:
        error_message = f"Failed to make predictions with Vertex AI: {e}"
        logging.error(error_message)
        raise VertexAIError(error_message)

def main():
    """Main function for example usage."""
    config_path = "config.yaml"
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        return

    credentials_path = config.get('credentials_path')
    project_id = config.get('project_id')
    model_path = config.get('model_path')
    display_name = config.get('display_name')
    endpoint_name = config.get('endpoint_name')
    location = config.get('location', "us-central1")

    if not all([credentials_path, project_id, model_path, display_name, endpoint_name]):
        logging.error("Missing required configuration values.")
        return

    try:
        initialize_vertex_ai(credentials_path, project_id, location)
        model = upload_model_to_vertex_ai(model_path, display_name, project_id, location)
        endpoint = deploy_model_to_endpoint(model, endpoint_name, project_id, location)

        # Example input data
        instances = [{"input": "example input data"}]

        logging.info("Making predictions...")
        predictions = predict_with_vertex_ai(endpoint, instances)
        logging.info(f"Predictions: {predictions}")

    except (ValueError, VertexAIError) as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    main()
>>>>>>> 516a66495 (Reinitialize repository and add files)
