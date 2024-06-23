import numpy as np
import pandas as pd
from joblib import Parallel, delayed
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from sklearn.model_selection import train_test_split  # Added import for train_test_split
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_fspl(frequency: np.ndarray, distance: np.ndarray, tx_gain: np.ndarray, rx_gain: np.ndarray) -> np.ndarray:
    """
    Calculate Free Space Path Loss (FSPL).
    
    Args:
        frequency (ndarray): Frequency in Hz
        distance (ndarray): Distance in meters
        tx_gain (ndarray): Transmit antenna gain in dBi
        rx_gain (ndarray): Receive antenna gain in dBi
    
    Returns:
        fspls (ndarray): Free Space Path Loss in dB
    """
    c = 3e8  # Speed of light in m/s

    def fspl_calculator(p):
        # Validate inputs and handle invalid values
        if p['frequency'] <= 0 or p['frequency'] > 1e9:
            return float('nan')
        if p['distance'] < 3 or p['distance'] >= 10000:
            return float('nan')
        if p['tx_gain'] < 0 or p['tx_gain'] > 30:
            return float('nan')
        if p['rx_gain'] < 0 or p['rx_gain'] > 30:
            return float('nan')
        
        # FSPL formula
        fspl = 20 * np.log10(p['distance']) + 20 * np.log10(p['frequency']) - 147.55 + p['tx_gain'] + p['rx_gain']
        return fspl
    
    # Apply the calculator function to each combination of inputs
    fspls = np.vectorize(fspl_calculator)({'frequency': frequency, 'distance': distance, 'tx_gain': tx_gain, 'rx_gain': rx_gain})
    return fspls

def process_batch(combinations):
    try:
        # Extract individual arrays from combinations
        frequencies = np.array([comb[0] for comb in combinations])
        distances = np.array([comb[1] for comb in combinations])
        tx_gains = np.array([comb[2] for comb in combinations])
        rx_gains = np.array([comb[3] for comb in combinations])
        
        # Calculate FSPL for each combination
        fspls = calculate_fspl(frequencies, distances, tx_gains, rx_gains)
        
        # Create a list of results as dictionaries
        return [{'frequency': frequency, 'distance': distance, 
                 'tx_gain': tx_gain, 'rx_gain': rx_gain, 'fspl': fspl}
                for (frequency, distance, tx_gain, rx_gain), fspl in zip(combinations, fspls)]
    except Exception as e:
        logging.error(f"Error processing batch: {e}")
        return None

def main():
    # Load dataset
    logging.info("Loading dataset...")
    df = pd.read_csv('/home/jmiguel/nvme2n1/veda_project/fspl_data.csv')
    
    # Preprocess dataset
    logging.info("Preprocessing dataset...")
    X = df[['frequency', 'distance', 'tx_gain', 'rx_gain']]
    y = df['fspl'].fillna(0)  # Replace NaN values with 0 to avoid errors later on
    
    # Define and compile the model within the GPU context
    with tf.device('/GPU:0'):
        logging.info("Defining the model...")
        model = Sequential([
            Dense(64, activation='relu', input_shape=(X.shape[1],)),
            Dropout(0.2),  # Add dropout to reduce overfitting
            Dense(64, activation='relu'),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])  # Added 'mae' metric
    
    # Split dataset into training and validation
    logging.info("Splitting dataset...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model with early stopping
    logging.info("Training the model...")
    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)
    batch_size = 32  # Batch size for GPU memory reasons
    
    model.fit(X_train, y_train, epochs=100, batch_size=batch_size, validation_data=(X_test, y_test), callbacks=[early_stopping])
    
    # Save the model
    logging.info("Saving the model...")
    model.save('/home/jmiguel/nvme2n1/veda_project/models/fspl_model.h5')
    logging.info("Model training and saving complete.")

if __name__ == "__main__":
    main()
