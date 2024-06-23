import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

class RSSI:
    def __init__(self, pr, path_loss, nf):
        """Initialize the RSSI class"""
        self.pr = pr  # Received power (dBm)
        self.path_loss = path_loss  # Path loss (dB)
        self.nf = nf  # Noise figure (dB)

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'rssi.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_rssi.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_rssi(pr, path_loss, nf):
        """Calculate RSSI"""
        rssi = pr - path_loss - nf
        return {"RSSI": rssi, "pr": pr, "path_loss": path_loss, "nf": nf}

    @staticmethod
    def calculate_rssi_static(params):
        """Static method for multiprocessing"""
        return RSSI.calculate_rssi(*params)

    def calculate(self):
        """Calculate RSSI for a range of parameters"""
        # Define the range of variables
        pr_values = np.arange(-100, 0, 1)  # Received power from -100 dBm to -1 dBm
        path_loss_values = np.arange(0, 150, 1)  # Path loss from 0 dB to 149 dB
        nf_values = np.arange(0, 10, 0.5)  # Noise figure from 0 dB to 9.5 dB

        parameters = [(p, pl, n) for p in pr_values for pl in path_loss_values for n in nf_values]
        num_cpus = min(cpu_count(), 48)  # Use 48 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        db_folder = "db_rssi"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving

        for i in range(0, len(parameters), batch_size):
            batch_params = parameters[i:i + batch_size]
            results = []
            with Pool(processes=num_cpus) as pool:
                for result in tqdm(pool.imap_unordered(RSSI.calculate_rssi_static, batch_params), total=len(batch_params)):
                    if result is not None:
                        results.append(result)

            self.log_results(results)

            db_filename = f"{db_folder}/rssi_batch_{i // batch_size}.csv"
            with open(db_filename, 'w') as csvfile:
                header = "RSSI,pr,path_loss,nf\n"
                csvfile.write(header)
                for r in results:
                    if r is not None:
                        line = f"{r['RSSI']},{r['pr']},{r['path_loss']},{r['nf']}\n"
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

# Run the RSSI Calculation
if __name__ == "__main__":
    RSSI.init_logger()
    rssi = RSSI(pr=-50, path_loss=50, nf=5)  # Initial values, will be overwritten by the parameter ranges
    rssi.calculate()
