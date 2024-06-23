import math
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm

class FSPL:
    def __init__(self, frequency, distance_ft, tx_gain, rx_gain):
        """Initialize the FSPL class with imperial units"""
        self.frequency = frequency  # in MHz
        self.distance_ft = distance_ft
        self.tx_gain = tx_gain  # in dBi, stays the same
        self.rx_gain = rx_gain  # in dBi, stays the same

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'fspld.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results, batch_num):
        """Log the results"""
        with open(f"results_fspld_batch_{batch_num}.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_in_parallel(params):
        """Calculate FSPL in parallel"""
        try:
            return FSPL.calculate_fspld(*params)
        except Exception as e:
            logging.error(f"Error calculating FSPL for given parameters: {e}")
            return None

    @staticmethod
    def calculate_fspld(frequency, distance_ft, tx_gain, rx_gain):
        """Calculate FSPL"""
        # Convert input distances to meters
        distance = distance_ft * 0.3048  # in meters

        fspld = 20 * math.log10(distance) + 20 * math.log10(frequency) + 20 * math.log10(4 * math.pi / 0.3048) - 147.55 + tx_gain + rx_gain

        return {"lambda": distance / frequency, "FSPL_ft": fspld}

    def calculate(self, batch_size=1000):
        """Calculate FSPL for a range of parameters"""
        # Define ranges for frequency, distance, tx_gain, and rx_gain
        frequency_range = range(700, 3001, 50)  # 700 MHz to 3000 MHz in steps of 50 MHz
        distance_range = range(5, 751, 5)  # 5 ft to 750 ft in steps of 5 ft
        tx_gain_range = range(0, 16, 1)  # 0 dBi to 15 dBi in steps of 1 dBi
        rx_gain_range = range(0, 16, 1)  # 0 dBi to 15 dBi in steps of 1 dBi

        params = [(freq, dist, tx_gain, rx_gain) for freq in frequency_range for dist in distance_range for tx_gain in tx_gain_range for rx_gain in rx_gain_range]

        num_cpus = min(cpu_count(), 16)  # Limit to 16 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        total_batches = len(params) // batch_size + (1 if len(params) % batch_size != 0 else 0)
        for batch_num in range(total_batches):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, len(params))
            batch_params = params[start_index:end_index]

            results = []
            with Pool(processes=num_cpus) as pool:
                for result in tqdm(pool.imap_unordered(FSPL.calculate_in_parallel, batch_params), total=len(batch_params)):
                    if result is not None:
                        results.append(result)

            self.log_results(results, batch_num)

            db_folder = f"db_fspld_batch_{batch_num}"
            Path(db_folder).mkdir(parents=True, exist_ok=True)
            db_filename = f"{db_folder}/fspld.csv"

            with open(db_filename, 'w') as csvfile:
                header = "lambda,FSPL_ft\n"
                csvfile.write(header)

                for r in results:
                    if r is not None:
                        line = f"{r['lambda']},{r['FSPL_ft']}\n"
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

if __name__ == "__main__":
    FSPL.init_logger()
    fspl = FSPL(frequency=2400, distance_ft=100, tx_gain=2, rx_gain=2)
    fspl.calculate()

