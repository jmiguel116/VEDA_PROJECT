import os
import logging
import math
from multiprocessing import Pool, cpu_count
from pathlib import Path
from tqdm import tqdm
from zipfile import ZipFile, ZIP_DEFLATED

class NoiseFigure:
    def __init__(self, snr_in_range, snr_out_range, distance_range, frequency_range, tx_power_range):
        self.snr_in_range = snr_in_range
        self.snr_out_range = snr_out_range
        self.distance_range = distance_range
        self.frequency_range = frequency_range
        self.tx_power_range = tx_power_range

    @staticmethod
    def init_logger():
        log_folder = "logs"
        Path(log_folder).mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=os.path.join(log_folder, 'nf_calculation.log'), level=logging.DEBUG)
        logging.debug("Logger initialized")

    @staticmethod
    def calculate_nf(params):
        snr_in, snr_out, distance, frequency, tx_power = params
        return {
            "SNR_in": snr_in,
            "SNR_out": snr_out,
            "Distance_ft": distance,
            "Frequency_MHz": frequency,
            "Tx_Power_dBm": tx_power,
            "NF_dB": snr_in - snr_out
        }

    def calculate(self):
        parameters = [
            (snr_in, snr_out, distance, frequency, tx_power)
            for snr_in in self.snr_in_range
            for snr_out in self.snr_out_range
            for distance in self.distance_range
            for frequency in self.frequency_range
            for tx_power in self.tx_power_range
        ]

        num_cpus = min(cpu_count(), 16)
        logging.debug(f"Using {num_cpus} CPU cores for parallel processing")

        results = []
        with Pool(processes=num_cpus) as pool:
            for result in tqdm(pool.imap_unordered(NoiseFigure.calculate_nf, parameters), total=len(parameters)):
                if result is not None:
                    results.append(result)

        self.save_results(results)

    def save_results(self, results):
        db_folder = "db_nf"
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        db_filename = f"{db_folder}/nf_data.csv"

        with open(db_filename, 'w') as csvfile:
            header = "SNR_in,SNR_out,Distance_ft,Frequency_MHz,Tx_Power_dBm,NF_dB\n"
            csvfile.write(header)

            for r in results:
                line = f"{r['SNR_in']},{r['SNR_out']},{r['Distance_ft']},{r['Frequency_MHz']},{r['Tx_Power_dBm']},{r['NF_dB']}\n"
                csvfile.write(line)

        self.compress_database(db_folder)

    @staticmethod
    def compress_database(db_folder):
        zip_filename = f"{db_folder}.zip"
        with ZipFile(zip_filename, "w", ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(db_folder):
                for fn in files:
                    file_path = os.path.join(root, fn)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, db_folder))
        print(f"Database compressed to {zip_filename}")

if __name__ == "__main__":
    NoiseFigure.init_logger()
    snr_in_range = range(0, 50, 1)  # Example range for SNR at input in dB
    snr_out_range = range(0, 50, 1)  # Example range for SNR at output in dB
    distance_range = range(5, 500, 5)  # Example range for distance in feet
    frequency_range = range(700, 3000, 50)  # Example range for frequency in MHz
    tx_power_range = range(20, 43, 1)  # Example range for transmitted power in dBm

    nf = NoiseFigure(snr_in_range, snr_out_range, distance_range, frequency_range, tx_power_range)
    nf.calculate()
