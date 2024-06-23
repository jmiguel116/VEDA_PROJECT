# Doppler Shift Calculation Script for VEDA
# This script generates a comprehensive dataset for Doppler Shift considering various scenarios.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the DopplerShift class
class DopplerShift:
    def __init__(self, frequency, velocity, angle):
        """Initialize the DopplerShift class"""
        self.frequency = frequency  # Frequency in MHz
        self.velocity = velocity  # Velocity in m/s
        self.angle = angle  # Angle in degrees

    @staticmethod
    def init_logger():
        """Initialize logger"""
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'doppler_shift.log'),
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s:%(message)s'
        )
        logging.debug("Logger initialized")

    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_doppler_shift.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")

    @staticmethod
    def calculate_doppler_shift(frequency, velocity, angle):
        """Calculate Doppler Shift"""
        c = 3 * 10**8  # Speed of light in m/s
        # Convert angle to radians
        angle_rad = np.deg2rad(angle)
        # Doppler shift formula
        doppler_shift = (velocity * np.cos(angle_rad) / c) * frequency * 10**6  # Shift in Hz

        return {"frequency": frequency, "velocity": velocity, "angle": angle, "doppler_shift": doppler_shift}

    def calculate(self):
        """Calculate Doppler Shift for a range of parameters"""
        # Define the range of variables
        frequency_values = np.arange(700, 3001, 50)  # Frequency from 700 MHz to 3000 MHz
        velocity_values = np.arange(0, 101, 1)  # Velocity from 0 m/s to 100 m/s
        angle_values = np.arange(0, 181, 1)  # Angle from 0 to 180 degrees

        parameters = [(f, v, a) for f in frequency_values for v in velocity_values for a in angle_values]
        num_cpus = min(cpu_count(), 16)  # Limit to 16 cores
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(lambda p: DopplerShift.calculate_doppler_shift(*p), parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.log_results(results)

        db_folder = "db_doppler_shift"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        batch_size = 100000  # Define batch size for saving
        for i in range(0, len(results), batch_size):
            batch_results = results[i:i + batch_size]
            db_filename = f"{db_folder}/doppler_shift_batch_{i // batch_size}.csv"

            with open(db_filename, 'w') as csvfile:
                header = "frequency,velocity,angle,doppler_shift\n"
                csvfile.write(header)

                for r in batch_results:
                    line = f"{r['frequency']},{r['velocity']},{r['angle']},{r['doppler_shift']}\n"
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

# ## Run the Doppler Shift Calculation
if __name__ == "__main__":
    DopplerShift.init_logger()
    doppler_shift = DopplerShift(frequency=2400, velocity=10, angle=45)  # Initial values, will be overwritten by the parameter ranges
    doppler_shift.calculate()
