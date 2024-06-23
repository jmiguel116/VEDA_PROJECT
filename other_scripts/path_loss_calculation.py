import math
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED

class PathLoss:
    def __init__(self, frequency, distance_ft, tx_power, tx_gain, rx_gain, path_loss_exponent, ref_distance_ft=3.28084):
        self.frequency = frequency  # in MHz
        self.distance_ft = distance_ft  # in feet
        self.tx_power = tx_power  # in dBm
        self.tx_gain = tx_gain  # in dBi
        self.rx_gain = rx_gain  # in dBi
        self.path_loss_exponent = path_loss_exponent  # typically ranges from 2 to 4 for indoor environments
        self.ref_distance_ft = ref_distance_ft  # reference distance in feet (1 meter = 3.28084 feet)

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=os.path.join(log_folder, 'path_loss.log'), level=logging.DEBUG)
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results, batch_number):
        """Log the results"""
        with open(f"results_path_loss_batch_{batch_number}.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    def calculate_path_loss(self, d_ft):
        """Calculate path loss using the log-distance path loss model"""
        d_m = d_ft * 0.3048  # convert feet to meters
        d0_m = self.ref_distance_ft * 0.3048  # convert reference distance to meters
        Lp_d0 = 20 * math.log10(d0_m) + 20 * math.log10(self.frequency) - 27.55  # path loss at reference distance in dB
        Lp_d = Lp_d0 + 10 * self.path_loss_exponent * math.log10(d_m / d0_m)  # path loss at distance d in dB
        Pr = self.tx_power + self.tx_gain + self.rx_gain - Lp_d  # Friis Transmission Equation result in dBm
        return {
            "frequency_MHz": self.frequency,
            "distance_ft": d_ft,
            "tx_power_dBm": self.tx_power,
            "tx_gain_dBi": self.tx_gain,
            "rx_gain_dBi": self.rx_gain,
            "path_loss_exponent": self.path_loss_exponent,
            "path_loss_dB": Lp_d,
            "received_power_dBm": Pr
        }

    def calculate(self, num_workers=None):
        """Calculate path loss for a range of distances and parameters"""
        if num_workers is None:
            num_workers = min(cpu_count(), 16)
        logging.debug(f"Using {num_workers} CPU cores for parallel processing")

        frequencies = list(range(700, 3001, 50))  # frequencies from 700 MHz to 3000 MHz
        tx_powers = list(range(20, 44))  # transmission powers from 20 dBm to 43 dBm
        distances_ft = list(range(5, 501, 5))  # distances from 5ft to 500ft

        params = [
            (f, d, p, self.tx_gain, self.rx_gain, self.path_loss_exponent, self.ref_distance_ft)
            for f in frequencies for d in distances_ft for p in tx_powers
        ]

        batch_size = 1000  # processing in batches of 1000
        num_batches = len(params) // batch_size + (1 if len(params) % batch_size > 0 else 0)

        for batch_number in range(num_batches):
            batch_start = batch_number * batch_size
            batch_end = min((batch_number + 1) * batch_size, len(params))
            batch_params = params[batch_start:batch_end]

            results = []
            with Pool(processes=num_workers) as pool:
                for result in tqdm(pool.imap_unordered(self.calculate_in_parallel, batch_params), total=len(batch_params)):
                    if result is not None:
                        results.append(result)

            self.log_results(results, batch_number)
            self.save_to_csv(results, batch_number)

    @staticmethod
    def calculate_in_parallel(params):
        """Calculate path loss in parallel"""
        try:
            path_loss_instance = PathLoss(*params[:7])
            return path_loss_instance.calculate_path_loss(params[1])
        except Exception as e:
            logging.error(f"Error calculating path loss for given parameters: {e}")
            return None

    def save_to_csv(self, results, batch_number):
        """Save results to a CSV file"""
        db_folder = "db_path_loss"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        db_filename = f"{db_folder}/path_loss_batch_{batch_number}.csv"

        df = pd.DataFrame(results)
        df.to_csv(db_filename, index=False)

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

if __name__ == "__main__":
    PathLoss.init_logger()
    path_loss = PathLoss(frequency=2400, distance_ft=100, tx_power=0, tx_gain=2, rx_gain=2, path_loss_exponent=2)
    path_loss.calculate()
