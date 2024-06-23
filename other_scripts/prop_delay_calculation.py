# ## Propagation Delay Calculation Script for VEDA
# This script generates a comprehensive dataset for propagation delay
# considering a wide range of variables to ensure it's robust and effective for VEDA's learning and knowledge bank.

# ## Import necessary libraries
import math
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm

# ## Define the Propagation Delay class
class PropagationDelay:
    def __init__(self, distance_miles, speed_of_light_mps):
        """Initialize the Propagation Delay class with imperial units"""
        self.distance_miles = distance_miles  # Distance in miles
        self.speed_of_light_mps = speed_of_light_mps  # Speed of light in miles per second

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'propagation_delay.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_propagation_delay.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_propagation_delay(params):
        """Calculate propagation delay"""
        distance_miles, speed_of_light_mps = params
        delay = distance_miles / speed_of_light_mps
        return {"delay_sec": delay, "distance_miles": distance_miles, "speed_of_light_mps": speed_of_light_mps}

    def calculate(self):
        """Calculate propagation delay for a range of parameters"""
        # Define the range of variables
        distance_miles_values = [i * 0.1 for i in range(1, 10001)]  # Distance from 0.1 miles to 1000 miles
        speed_of_light_mps = 186282.397  # Speed of light in miles per second

        parameters = [(d, speed_of_light_mps) for d in distance_miles_values]
        num_cpus = min(cpu_count(), 48)  # Limit to 48 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(PropagationDelay.calculate_propagation_delay, parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_propagation_delay"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 1000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/propagation_delay_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "delay_sec,distance_miles,speed_of_light_mps\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['delay_sec']},{r['distance_miles']},{r['speed_of_light_mps']}\n"
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

# ## Run the Propagation Delay Calculation
if __name__ == "__main__":
    PropagationDelay.init_logger()
    propagation_delay = PropagationDelay(distance_miles=1, speed_of_light_mps=186282.397)  # Initial values
    propagation_delay.calculate()
