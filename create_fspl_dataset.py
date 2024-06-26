import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
import logging
<<<<<<< HEAD

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def calculate_fspl(frequency, distance, tx_gain, rx_gain):
    """
    Calculate Free Space Path Loss (FSPL).
    
    Args:
    - frequency (float): Frequency in Hz
    - distance (float): Distance in meters
    - tx_gain (float): Transmit antenna gain in dBi
    - rx_gain (float): Receive antenna gain in dBi
    
    Returns:
    - fspl (float): Free Space Path Loss in dB
    """
    c = 3e8  # Speed of light in m/s
    fspl = 20 * np.log10(distance) + 20 * np.log10(frequency) - 147.55 + tx_gain + rx_gain
    return fspl

def process_combination(frequency, distance, tx_gain, rx_gain):
    try:
        fspl = calculate_fspl(frequency, distance, tx_gain, rx_gain)
        return {
            'frequency': frequency,
            'distance': distance,
            'tx_gain': tx_gain,
            'rx_gain': rx_gain,
            'fspl': fspl
        }
    except Exception as e:
        logging.error(f"Error processing combination: {e}")
        return None

def main():
    frequencies = np.linspace(1e6, 1e9, 250)  # 250 frequencies from 1 MHz to 1 GHz
    distances = np.arange(3, 10003, 100)  # From 3 meters to 10000 meters, step by 100 meters
    tx_gains = np.arange(0, 31, 1)  # Tx Gain from 0 to 30 dBi
    rx_gains = np.arange(0, 31, 1)  # Rx Gain from 0 to 30 dBi

    # Prepare the combination of parameters
    param_combinations = [
        (frequency, distance, tx_gain, rx_gain)
        for frequency in frequencies
        for distance in distances
        for tx_gain in tx_gains
        for rx_gain in rx_gains
    ]

    # Process in parallel with progress bar
    results = []
    batch_size = 10000  # Adjust batch size as needed
    for i in tqdm(range(0, len(param_combinations), batch_size), desc="Processing Batches"):
        batch = param_combinations[i:i + batch_size]
        batch_results = Parallel(n_jobs=-1)(
            delayed(process_combination)(*params) for params in batch
        )
        results.extend(filter(None, batch_results))  # Filter out None results due to errors

    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv('fspl_dataset.csv', index=False, compression='zip')
    logging.info("FSPL dataset saved successfully.")

if __name__ == "__main__":
    main()

=======
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
SPEED_OF_LIGHT = 3e8  # Speed of light in m/s

def calculate_fspl(frequency_mhz, distance_m, tx_gain_dbi, rx_gain_dbi):
    """
    Calculate the Free Space Path Loss (FSPL) for given parameters.

    Args:
        frequency_mhz: Frequency in MHz.
        distance_m: Distance in meters.
        tx_gain_dbi: Transmitter gain in dBi.
        rx_gain_dbi: Receiver gain in dBi.

    Returns:
        A dictionary containing the calculated FSPL and input parameters.
    """
    try:
        frequency_hz = frequency_mhz * 1e6  # Convert MHz to Hz
        wavelength = SPEED_OF_LIGHT / frequency_hz
        fspl = (4 * np.pi * distance_m / wavelength) ** 2
        fspl_db = 10 * np.log10(fspl)
        return {
            'Frequency (MHz)': frequency_mhz,
            'Distance (m)': distance_m,
            'Tx Gain (dBi)': tx_gain_dbi,
            'Rx Gain (dBi)': rx_gain_dbi,
            'FSPL (dB)': fspl_db - tx_gain_dbi - rx_gain_dbi
        }
    except Exception as e:
        logging.error(f"Error in FSPL calculation: {e}")
        return {
            'Frequency (MHz)': frequency_mhz,
            'Distance (m)': distance_m,
            'Tx Gain (dBi)': tx_gain_dbi,
            'Rx Gain (dBi)': rx_gain_dbi,
            'FSPL (dB)': None
        }

def generate_dataset(frequencies, distances, tx_gains, rx_gains):
    """
    Generate a dataset for FSPL calculations.

    Args:
        frequencies: Array of frequencies in MHz.
        distances: Array of distances in meters.
        tx_gains: Array of transmitter gains in dBi.
        rx_gains: Array of receiver gains in dBi.

    Returns:
        A pandas DataFrame containing the generated FSPL dataset.
    """
    total_tasks = len(frequencies) * len(distances) * len(tx_gains) * len(rx_gains)
    logging.info(f"Total calculations to perform: {total_tasks}")

    # Use tqdm outside the Parallel loop for efficient progress tracking
    data = []
    with tqdm(total=total_tasks, desc="Generating FSPL Dataset") as pbar:
        for result in Parallel(n_jobs=-1)(
            delayed(calculate_fspl)(freq, dist, tx_gain, rx_gain)
            for freq in frequencies
            for dist in distances
            for tx_gain in tx_gains
            for rx_gain in rx_gains
        ):
            data.append(result)
            pbar.update(1)

    df = pd.DataFrame(data)
    return df

# Define ranges
frequencies = np.arange(1, 4001, 0.5)  # 1 MHz to 4 GHz with 0.5 MHz steps
distances = np.arange(3, 10001, 0.5)  # 3 meters to 10,000 meters with 0.5 meter steps
tx_gains = np.arange(0, 31, 0.5)  # 0 dBi to 30 dBi with 0.5 dBi steps
rx_gains = np.arange(0, 31, 0.5)  # 0 dBi to 30 dBi with 0.5 dBi steps

logging.info("Starting dataset generation...")
dataset = generate_dataset(frequencies, distances, tx_gains, rx_gains)
logging.info("Dataset generation completed.")

# Specify the save path
save_path = os.getenv('FSPL_DATASET_PATH', '/media/jmiguel-rai-control/fd67fcf7-7925-43d5-9ad0-85c2882c0795/fspl_dataset.csv.gz')

# Save to CSV
dataset.to_csv(save_path, index=False, compression='gzip')
logging.info(f"Dataset saved to {save_path}")
>>>>>>> 516a66495 (Reinitialize repository and add files)
