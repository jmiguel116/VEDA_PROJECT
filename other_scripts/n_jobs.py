import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
import logging
import os
import multiprocessing
import psutil

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
    # Use 75% of available CPU cores
    num_cores = int(multiprocessing.cpu_count() * 0.75)

    # Dynamic batch size based on available memory
    available_memory = psutil.virtual_memory().available
    estimated_memory_per_combination = 0.0001  # Estimated memory usage per combination in MB
    batch_size = int(available_memory / (estimated_memory_per_combination * 1024))

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
    for i in tqdm(range(0, len(param_combinations), batch_size), desc="Processing Batches"):
        batch = param_combinations[i:i + batch_size]
        batch_results = Parallel(n_jobs=num_cores)(
            delayed(process_combination)(*params) for params in tqdm(batch, desc="Processing Combinations", leave=False)
        )
        results.extend(filter(None, batch_results))  # Filter out None results due to errors

    # Create DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv('fspl_dataset.csv', index=False, compression='zip')
    logging.info("FSPL dataset saved successfully.")

if __name__ == "__main__":
    main()
