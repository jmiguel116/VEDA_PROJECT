import math
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from zipfile import ZipFile, ZIP_DEFLATED

# # EIRP Calculation Script
# This script calculates the Effective Isotropic Radiated Power (EIRP) and generates a dataset.
# It uses parallel processing to speed up the calculations and saves the results in batches.

class EIRP:
    def __init__(self, pt_dbm, gt_db, lt_db):
        """Initialize the EIRP class with the necessary parameters"""
        self.pt_dbm = pt_dbm  # Transmitted power (dBm)
        self.gt_db = gt_db    # Gain of the transmitting antenna (dBi)
        self.lt_db = lt_db    # Losses in the transmitter (dB)

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=os.path.join(log_folder, 'eirp.log'), level=logging.DEBUG)
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_eirp.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_eirp(pt_dbm, gt_db, lt_db):
        """Calculate the EIRP"""
        eirp = pt_dbm + gt_db - lt_db
        return {"Pt (dBm)": pt_dbm, "Gt (dBi)": gt_db, "Lt (dB)": lt_db, "EIRP (dBm)": eirp}

    def calculate(self):
        """Calculate EIRP for a range of parameters"""
        num_cpus = min(cpu_count(), 48)  # Limit to 48 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        parameters = []
        for pt_dbm in range(20, 44):  # Transmitted power from 20 dBm to 43 dBm
            for gt_db in range(0, 16):  # Antenna gain from 0 dBi to 15 dBi
                for lt_db in range(0, 11):  # Losses from 0 dB to 10 dB
                    parameters.append((pt_dbm, gt_db, lt_db))

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(lambda p: EIRP.calculate_eirp(*p), parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)
                    if len(results) % 10000 == 0:  # Save every 10000 results to avoid using too much memory
                        self.save_to_csv(results, len(results) // 10000)
                        results.clear()

        # Save any remaining results
        if results:
            self.save_to_csv(results, len(results) // 10000 + 1)

        self.compress_database("db_eirp")

    @staticmethod
    def save_to_csv(data, batch_num):
        """Save data to CSV file"""
        db_folder = "db_eirp"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        db_filename = f"{db_folder}/eirp_data_batch_{batch_num}.csv"
        with open(db_filename, 'w') as csvfile:
            header = "Pt (dBm),Gt (dBi),Lt (dB),EIRP (dBm)\n"
            csvfile.write(header)
            for r in data:
                line = f"{r['Pt (dBm)']},{r['Gt (dBi)']},{r['Lt (dB)']},{r['EIRP (dBm)']}\n"
                csvfile.write(line)
        logging.debug(f"Saved batch {batch_num} to {db_filename}")

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
        logging.debug(f"Database compressed to {zip_filename}")

if __name__ == "__main__":
    EIRP.init_logger()
    eirp = EIRP(pt_dbm=30, gt_db=5, lt_db=2)
    eirp.calculate()
