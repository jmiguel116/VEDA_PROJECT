# Signal-to-Noise Ratio (SNR) Calculation Script for VEDA
# This script generates a comprehensive dataset for SNR (Signal-to-Noise Ratio)
# considering a wide range of variables to ensure it's robust and effective for VEDA's learning and knowledge bank.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the SNR class
class SNR:
    def __init__(self, p_signal, p_noise):
        """Initialize the SNR class"""
        self.p_signal = p_signal  # Power of the signal (dBm)
        self.p_noise = p_noise  # Power of the noise (dBm)

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'snr.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_snr.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_snr(p_signal, p_noise):
        """Calculate SNR"""
        snr = p_signal - p_noise
        return {"SNR": snr, "p_signal": p_signal, "p_noise": p_noise}

    def calculate(self):
        """Calculate SNR for a range of parameters"""
        # Define the range of variables
        p_signal_values = np.arange(-100, 0, 1)  # Signal power from -100 dBm to -1 dBm
        p_noise_values = np.arange(-150, -50, 1)  # Noise power from -150 dBm to -51 dBm

        parameters = [(ps, pn) for ps in p_signal_values for pn in p_noise_values]
        num_cpus = min(cpu_count(), 48)  # Use up to 48 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(SNR.calculate_snr_wrapper, parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_snr"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/snr_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "SNR,p_signal,p_noise\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['SNR']},{r['p_signal']},{r['p_noise']}\n"
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

    @staticmethod
    def calculate_snr_wrapper(params):
        return SNR.calculate_snr(*params)

# ## Run the SNR Calculation
if __name__ == "__main__":
    SNR.init_logger()
    snr = SNR(p_signal=-50, p_noise=-100)  # Initial values, will be overwritten by the parameter ranges
    snr.calculate()
