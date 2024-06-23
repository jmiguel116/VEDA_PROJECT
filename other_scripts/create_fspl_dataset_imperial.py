import math
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

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
        logging.basicConfig(filename=os.path.join(log_folder, 'fspld.log'), level=logging.DEBUG)
        logging.debug("Logger initialized")
   
    @staticmethod
    def log_results(results):
        """Log the results"""
        with open("results_fspld.txt", "a") as f:
            for r in results:
                f.write(f"{r}\n")
   
    @staticmethod
    def calculate_in_parallel(params):
        """Calculate FSPL in parallel"""
        try:
            return FSPL(*params).calculate()
        except Exception as e:
            logging.error(f"Error calculating FSPL for given parameters: {e}")
            return None
   
    @staticmethod
    def calculate_fspld(frequency, distance_ft, tx_gain, rx_gain):
        """Calculate FSPL"""
        # Convert input distances to meters
        distance = distance_ft * 0.3048  # in meters
       
        fspld = 20 * math.log10(distance) + 20 * math.log10(frequency) - 27.55 + tx_gain + rx_gain
       
        # Convert output parameter (FSPL) back to imperial units (dB per feet)
        fspld *= 0.115149684  # Conversion factor from dB per meter to dB per foot
       
        return {"lambda": distance / frequency, "FSPL_ft": fspld}
   
    def calculate(self):
        """Calculate FSPL for a given set of parameters"""
        params = (self.frequency, self.distance_ft, self.tx_gain, self.rx_gain)
       
        # Use all available CPU cores, but limit to a maximum of 16
        num_cpus = min(cpu_count(), 16)
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")
       
        with Pool(processes=num_cpus) as pool:
            results = pool.map(FSPL.calculate_in_parallel, [params] * 1000)  # Increase number of iterations for better performance
       
        self.log_results(results)
       
        db_folder = "db_fspld"
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
