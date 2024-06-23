import os
import logging
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from joblib import dump, load
from sklearn.metrics import mean_squared_error, r2_score

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

def load_data(file_path):
    """Load dataset from the specified file path."""
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
    """Main function to orchestrate the training process."""
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
