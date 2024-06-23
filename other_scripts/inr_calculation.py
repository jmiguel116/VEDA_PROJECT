# Interference-to-Noise Ratio (INR) Calculation Script for VEDA
# This script generates a comprehensive dataset for INR considering various interference and noise levels.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the INR class
class INR:
    def __init__(self, interference_power, noise_power):
        """Initialize the INR class"""
        self.interference_power = interference_power  # Interference power in dBm
        self.noise_power = noise_power  # Noise power in dBm

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'inr.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_inr.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_inr(interference_power, noise_power):
        """Calculate Interference-to-Noise Ratio (INR)"""
        inr = interference_power - noise_power  # INR in dB

        return {"interference_power": interference_power, "noise_power": noise_power, "inr": inr}

    def calculate(self):
        """Calculate INR for a range of parameters"""
        # Define the range of variables
        interference_power_values = np.arange(-100, 50, 1)  # Interference power from -100 dBm to 49 dBm
        noise_power_values = np.arange(-174, -50, 1)  # Noise power from -174 dBm to -51 dBm

        parameters = [(i, n) for i in interference_power_values for n in noise_power_values]
        num_cpus = min(cpu_count(), 16)  # Limit to 16 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(lambda p: INR.calculate_inr(*p), parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_inr"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/inr_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "interference_power,noise_power,inr\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['interference_power']},{r['noise_power']},{r['inr']}\n"
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

# ## Run the INR Calculation
if __name__ == "__main__":
    INR.init_logger()
    inr = INR(interference_power=-50, noise_power=-100)  # Initial values, will be overwritten by the parameter ranges
    inr.calculate()
