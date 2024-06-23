import os
import numpy as np
import pandas as pd
import multiprocessing
import logging
from tqdm import tqdm
from datetime import datetime

# Set up logging
logging.basicConfig(filename='dataset_creation.log', level=logging.INFO)

# Function to calculate Free Space Path Loss (FSPL)
def fspl(freq, dist, tx_gain, rx_gain):
    """
    Calculates Free Space Path Loss (FSPL) in dB.

    Args:
        freq: Frequency in Hz.
        dist: Distance in meters.
        tx_gain: Transmit gain in dBi.
        rx_gain: Receive gain in dBi.

    Returns:
        Path loss in dB.
    """
    c = 299792458  # Speed of light in m/s
    wavelength = c / freq
    loss_db = 20 * np.log10(4 * np.pi * dist / wavelength) + tx_gain + rx_gain
    return loss_db

# Function to create dataset batch
def create_dataset_batch(start_freq, end_freq, start_dist, end_dist, start_tx_gain, end_tx_gain, start_rx_gain, end_rx_gain, batch_num):
    """
    Creates a batch of FSPL data and saves it to a compressed CSV file.

    Args:
        start_freq: Starting frequency in Hz.
        end_freq: Ending frequency in Hz.
        start_dist: Starting distance in meters.
        end_dist: Ending distance in meters.
        start_tx_gain: Starting transmit gain in dBi.
        end_tx_gain: Ending transmit gain in dBi.
        start_rx_gain: Starting receive gain in dBi.
        end_rx_gain: Ending receive gain in dBi.
        batch_num: Batch number for file naming.
    """
    logging.info(f'Starting dataset batch {batch_num} creation...')

    freq_range = np.arange(start_freq, end_freq + 1, 1e6)  # Frequency range in Hz
    dist_range = np.arange(start_dist, end_dist + 1, 1)  # Distance range in meters
    tx_gain_range = np.arange(start_tx_gain, end_tx_gain + 0.5, 0.5)  # Tx Gain range in dBi
    rx_gain_range = np.arange(start_rx_gain, end_rx_gain + 0.5, 0.5)  # Rx Gain range in dBi

    dataset = []
    for freq in tqdm(freq_range, desc=f'Batch {batch_num} Frequencies'):
        for dist in tqdm(dist_range, desc='Distances', leave=False):
            for tx_gain in tx_gain_range:
                for rx_gain in rx_gain_range:
                    loss_db = fspl(freq, dist, tx_gain, rx_gain)
                    dataset.append([freq, dist, tx_gain, rx_gain, loss_db])

    df = pd.DataFrame(dataset, columns=['Frequency (Hz)', 'Distance (m)', 'Tx Gain (dBi)', 'Rx Gain (dBi)', 'Path Loss (dB)'])
    
    # Define a structured folder path based on the frequency range
    folder_path = os.path.join('/home/jmiguel/Documents/FSPL Dataset', f'{int(start_freq/1e6)}-{int(end_freq/1e6)} MHz')  
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(folder_path, f'batch_{batch_num:03d}.csv.gz')  # Use three-digit batch number for sorting
    df.to_csv(file_path, index=False, compression='gzip')

    logging.info(f'Dataset batch {batch_num} created and saved to {file_path}')


# Define parameters
start_freq = 1e6  # 1 MHz
end_freq = 4e9  # 4 GHz
start_dist = 3  # 3 meters
end_dist = 10000  # 10,000 meters
start_tx_gain = 0  # 0 dBi
end_tx_gain = 30  # 30 dBi
start_rx_gain = 0  # 0 dBi
end_rx_gain = 30  # 30 dBi
batch_size = 500  # Adjust based on available memory
num_batches = int((end_freq - start_freq) / batch_size) + 1

# Create dataset batches using multiprocessing
pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
for i in range(num_batches):
    start = start_freq + i * batch_size
    end = min(start_freq + (i + 1) * batch_size, end_freq)
    pool.apply_async(create_dataset_batch, args=(start, end, start_dist, end_dist, start_tx_gain, end_tx_gain, start_rx_gain, end_rx_gain, i))

pool.close()
pool.join()

logging.info('Dataset creation process completed')
