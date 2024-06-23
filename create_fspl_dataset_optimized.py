import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FSPL calculation
def calculate_fspl(frequency, distance, tx_gain, rx_gain):
    c = 3e8  # Speed of light in m/s
    frequency_hz = frequency * 1e6  # Convert MHz to Hz
    wavelength = c / frequency_hz
    fspl = (4 * np.pi * distance / wavelength) ** 2
    fspl_db = 10 * np.log10(fspl)
    return (frequency, distance, tx_gain, rx_gain, fspl_db - tx_gain - rx_gain)

# Generate the dataset
def generate_dataset(frequencies, distances, tx_gains, rx_gains):
    total_tasks = len(frequencies) * len(distances) * len(tx_gains) * len(rx_gains)
    data = Parallel(n_jobs=-1)(
        delayed(calculate_fspl)(freq, dist, tx_gain, rx_gain)
        for freq in tqdm(frequencies, desc="Frequencies", position=0)
        for dist in tqdm(distances, desc="Distances", position=1, leave=False)
        for tx_gain in tx_gains
        for rx_gain in rx_gains
    )
    columns = ['Frequency (MHz)', 'Distance (m)', 'Tx Gain (dBi)', 'Rx Gain (dBi)', 'FSPL (dB)']
    df = pd.DataFrame(data, columns=columns)
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
save_path = '/media/jmiguel-rai-control/fd67fcf7-7925-43d5-9ad0-85c2882c0795/fspl_dataset.csv.gz'

# Save to CSV
dataset.to_csv(save_path, index=False, compression='gzip')
logging.info(f"Dataset saved to {save_path}")
