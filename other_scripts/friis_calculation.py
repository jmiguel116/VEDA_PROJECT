# Friis Transmission Equation Script for VEDA
# This script generates a comprehensive dataset for the Friis Transmission Equation considering various environments.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the Friis class
class Friis:
    def __init__(self, p_tx, g_tx, g_rx, l_tx, distance, frequency, environment):
        """Initialize the Friis class"""
        self.p_tx = p_tx  # Transmitted power (dBm)
        self.g_tx = g_tx  # Gain of the transmitting antenna (dBi)
        self.g_rx = g_rx  # Gain of the receiving antenna (dBi)
        self.l_tx = l_tx  # Losses in the transmitter (dB)
        self.distance = distance  # Distance (m)
        self.frequency = frequency  # Frequency (MHz)
        self.environment = environment  # Environment type

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'friis.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_friis.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_friis(p_tx, g_tx, g_rx, l_tx, distance, frequency, environment):
        """Calculate Friis Transmission Equation"""
        c = 3 * 10**8  # Speed of light in m/s
        lambda_ = c / (frequency * 10**6)  # Wavelength in meters

        # Environment factor
        if environment == 'urban':
            path_loss_exponent = 2.7
        elif environment == 'suburban':
            path_loss_exponent = 2.2
        else:  # rural
            path_loss_exponent = 1.8

        # Friis transmission equation with environment factor
        l_p = 20 * np.log10(distance / lambda_) + 10 * path_loss_exponent * np.log10(distance)
        p_r = p_tx + g_tx + g_rx - l_tx - l_p

        return {"p_r": p_r, "p_tx": p_tx, "g_tx": g_tx, "g_rx": g_rx, "l_tx": l_tx, "distance": distance, "frequency": frequency, "environment": environment}

    def calculate(self):
        """Calculate Friis Transmission Equation for a range of parameters"""
        # Define the range of variables
        p_tx_values = np.arange(0, 50, 1)  # Transmitted power from 0 dBm to 49 dBm
        g_tx_values = np.arange(0, 15, 1)  # Transmitting antenna gain from 0 dBi to 14 dBi
        g_rx_values = np.arange(0, 15, 1)  # Receiving antenna gain from 0 dBi to 14 dBi
        l_tx_values = np.arange(0, 5, 1)  # Transmitter losses from 0 dB to 4 dB
        distance_values = np.arange(1, 1001, 10)  # Distance from 1 meter to 1000 meters
        frequency_values = np.arange(700, 3001, 50)  # Frequency from 700 MHz to 3000 MHz
        environment_values = ['urban', 'suburban', 'rural']  # Environment types

        parameters = [(p, g_t, g_r, l_t, d, f, e) for p in p_tx_values for g_t in g_tx_values for g_r in g_rx_values for l_t in l_tx_values for d in distance_values for f in frequency_values for e in environment_values]
        num_cpus = min(cpu_count(), 16)  # Limit to 16 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(lambda p: Friis.calculate_friis(*p), parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_friis"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/friis_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "p_r,p_tx,g_tx,g_rx,l_tx,distance,frequency,environment\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['p_r']},{r['p_tx']},{r['g_tx']},{r['g_rx']},{r['l_tx']},{r['distance']},{r['frequency']},{r['environment']}\n"
                    csvfile.write(line)

        self.compress_database(db_folder)

    @staticmethod
    def compress_database(db_folder):
        """Compress database folder"""
        zip_filename = f"{db_folder}.zip"
        with ZipFile(zip_filename, "w", ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(db_folder):
                for fn in files:
                    file_path = os.path.join(root, fn)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, db_folder))
        print(f"Database compressed to {zip_filename}")

# ## Run the Friis Calculation
if __name__ == "__main__":
    Friis.init_logger()
    friis = Friis(p_tx=20, g_tx=10, g_rx=10, l_tx=2, distance=100, frequency=2400, environment='urban')  # Initial values, will be overwritten by the parameter ranges
    friis.calculate()
