# EIRP Calculation Script for VEDA
# This script generates a comprehensive dataset for EIRP (Effective Isotropic Radiated Power)
# considering a wide range of variables to ensure it's robust and effective for VEDA's learning and knowledge bank.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the EIRP class
class EIRP:
    def __init__(self, tx_power, tx_gain, tx_loss):
        """Initialize the EIRP class"""
        self.tx_power = tx_power  # in dBm
        self.tx_gain = tx_gain    # in dBi
        self.tx_loss = tx_loss    # in dB

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'eirp.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_eirp.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_eirp(tx_power, tx_gain, tx_loss):
        """Calculate EIRP"""
        eirp = tx_power + tx_gain - tx_loss
        return {"EIRP": eirp, "tx_power": tx_power, "tx_gain": tx_gain, "tx_loss": tx_loss}

    def calculate(self):
        """Calculate EIRP for a range of parameters"""
        # Define the range of variables
        tx_powers = np.arange(20, 44, 1)  # Transmit power from 20 dBm to 43 dBm
        tx_gains = np.arange(0, 16, 1)    # Transmit gain from 0 dBi to 15 dBi
        tx_losses = np.arange(0, 6, 1)    # Transmit losses from 0 dB to 5 dB

        parameters = [(p, g, l) for p in tx_powers for g in tx_gains for l in tx_losses]
        num_cpus = min(cpu_count(), 16)  # Limit to 16 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(lambda p: EIRP.calculate_eirp(*p), parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_eirp"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/eirp_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "EIRP,tx_power,tx_gain,tx_loss\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['EIRP']},{r['tx_power']},{r['tx_gain']},{r['tx_loss']}\n"
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

# ## Run the EIRP Calculation
if __name__ == "__main__":
    EIRP.init_logger()
    eirp = EIRP(tx_power=20, tx_gain=0, tx_loss=0)  # Initial values, will be overwritten by the parameter ranges
    eirp.calculate()
