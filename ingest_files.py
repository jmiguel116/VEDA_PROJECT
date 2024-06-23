<<<<<<< HEAD
import openai

# Setup OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai.api_key)

# Create a new vector store for RF data
vector_store = client.create_vector_store(name="RF Data Store")

# List of files to upload
files = ["path/to/file1.csv", "path/to/file2.csv"]

# Upload files to the vector store
for file in files:
    client.upload_file_to_vector_store(
        vector_store_id=vector_store['id'],
        file=open(file, 'rb')
    )

print("Files uploaded to vector store:", vector_store)
=======
import os
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from joblib import dump, load
from sklearn.metrics import mean_squared_error, r2_score
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
from veda_app import create_app, db
from veda_app.models import Document
from combined_ocr_module import process_image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

app = create_app()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_document(filename, ocr_results, file_type, file_size, user_id):
    """Save the processed document to the database."""
    try:
        document = Document(
            title=filename,
            content=ocr_results,
            file_type=file_type,
            file_size=file_size,
            user_id=user_id
        )
        db.session.add(document)
        db.session.commit()
        logging.info(f"Document {filename} processed and saved to database.")
        return True
    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db.session.rollback()
        return False

def process_file(file_path, user_id):
    """Process a single file, perform OCR, and save the results."""
    try:
        filename = secure_filename(os.path.basename(file_path))
        if allowed_file(filename):
            file_type = os.path.splitext(filename)[1][1:]
            file_size = os.path.getsize(file_path)

            credentials_path = app.config.get('GOOGLE_CLOUD_CREDENTIALS')
            openai_api_key = app.config.get('OPENAI_API_KEY')
            ocr_results = process_image(file_path, credentials_path, openai_api_key)

            if save_document(filename, ocr_results, file_type, file_size, user_id):
                logging.info(f"File {filename} processed successfully.")
            else:
                logging.error(f"Failed to save document {filename} to database.")
        else:
            logging.error(f"File type not allowed: {filename}")
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")

def ingest_files(file_paths, user_id):
    """Ingest multiple files concurrently using a thread pool."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        for file_path in file_paths:
            executor.submit(process_file, file_path, user_id)

def load_data(file_path):
    """Load the dataset from the specified file path."""
    try:
        data = pd.read_csv(file_path)
        logging.info(f"Data loaded from {file_path}")
        return data
    except FileNotFoundError as e:
        logging.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise

def preprocess_data(data):
    """Preprocess the dataset for training."""
    try:
        X = data.drop('FSPL (dB)', axis=1)
        y = data['FSPL (dB)']
        logging.info("Data preprocessing completed.")
        return X, y
    except KeyError as e:
        logging.error(f"Missing key in data: {e}")
        raise
    except Exception as e:
        logging.error(f"Error preprocessing data: {e}")
        raise

def train_model(X_train, y_train):
    """Train the model using the training data."""
    try:
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 20],
            'min_samples_split': [2, 5, 10]
        }
        model = RandomForestRegressor(random_state=42)
        grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5)
        grid_search.fit(X_train, y_train)
        best_model = grid_search.best_estimator_
        logging.info("Model training completed.")
        return best_model
    except Exception as e:
        logging.error(f"Error training model: {e}")
        raise

def evaluate_model(model, X_test, y_test):
    """Evaluate the model using the test data."""
    try:
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        logging.info(f"Model evaluation completed. MSE: {mse}, R-squared: {r2}")
        return mse, r2
    except Exception as e:
        logging.error(f"Error evaluating model: {e}")
        raise

def save_model(model, save_path):
    """Save the trained model to the specified path."""
    try:
        dump(model, save_path)
        logging.info(f"Model saved to {save_path}")
    except Exception as e:
        logging.error(f"Error saving model: {e}")
        raise

def load_model(save_path):
    """Load the trained model from the specified path."""
    try:
        model = load(save_path)
        logging.info(f"Model loaded from {save_path}")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        raise

def main():
    """Main function to orchestrate the entire process."""
    user_id = 'default_user_id'  # Replace with actual user ID logic
    file_directory = '/path/to/files'  # Replace with actual file directory
    file_paths = [os.path.join(file_directory, f) for f in os.listdir(file_directory) if allowed_file(f)]

    logging.info("Starting file ingestion process...")
    ingest_files(file_paths, user_id)
    logging.info("File ingestion process completed.")

    dataset_path = os.getenv('DATASET_PATH', 'fspl_dataset.csv.gz')
    model_save_path = os.getenv('MODEL_SAVE_PATH', 'rf_model.joblib')

    data = load_data(dataset_path)
    X, y = preprocess_data(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = train_model(X_train, y_train)

    mse, r2 = evaluate_model(model, X_test, y_test)

    save_model(model, model_save_path)

    logging.info(f"Training process completed with MSE: {mse}, R-squared: {r2}")

if __name__ == "__main__":
    main()
>>>>>>> 516a66495 (Reinitialize repository and add files)
