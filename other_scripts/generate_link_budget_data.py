import math
import os
import logging
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

def init_logger():
    log_folder = "logs"
    Path(log_folder).mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=os.path.join(log_folder, 'link_budget.log'), level=logging.DEBUG)
    logging.debug("Logger initialized")

def calculate_received_power(P_t, G_t, L_t, L_p, G_r, L_r):
    """
    Calculate received power using the link budget formula.

    Parameters:
    P_t (float): Transmitted power in dBm
    G_t (float): Gain of the transmitting antenna in dBi
    L_t (float): Losses in the transmitter in dB
    L_p (float): Path loss in dB
    G_r (float): Gain of the receiving antenna in dBi
    L_r (float): Losses in the receiver in dB

    Returns:
    float: Received power in dBm
    """
    P_r = P_t + G_t - L_t - L_p + G_r - L_r
    return P_r

def calculate_path_loss(frequency, distance_ft):
    """
    Placeholder function for path loss calculation.
    Replace with the actual path loss calculation as needed.
    """
    distance_m = distance_ft * 0.3048  # Convert feet to meters
    path_loss = 20 * np.log10(distance_m) + 20 * np.log10(frequency) - 27.55
    return path_loss

def generate_link_budget_data():
    frequencies = np.arange(700, 3001, 50)  # Frequency range from 700 MHz to 3000 MHz
    distances = np.arange(5, 501, 5)  # Distance range from 5 ft to 500 ft
    tx_powers = np.arange(20, 44, 1)  # Transmitter power range from 20 dBm to 43 dBm
    tx_gains = np.arange(0, 16, 1)  # Tx gain from 0 dBi to 15 dBi
    rx_gains = np.arange(0, 16, 1)  # Rx gain from 0 dBi to 15 dBi
    losses_tx = 2.0  # Example transmitter losses in dB
    losses_rx = 2.0  # Example receiver losses in dB

    data = []

    for freq in frequencies:
        for dist in tqdm(distances, desc="Distances"):
            for P_t in tx_powers:
                for G_t in tx_gains:
                    for G_r in rx_gains:
                        L_p = calculate_path_loss(freq, dist)  # Calculate path loss
                        P_r = calculate_received_power(P_t, G_t, losses_tx, L_p, G_r, losses_rx)
                        data.append([freq, dist, P_t, G_t, losses_tx, L_p, G_r, losses_rx, P_r])

    df = pd.DataFrame(data, columns=['Frequency_MHz', 'Distance_ft', 'Tx_Power_dBm', 'Tx_Gain_dBi',
                                      'Losses_Tx_dB', 'Path_Loss_dB', 'Rx_Gain_dBi', 'Losses_Rx_dB', 'Received_Power_dBm'])
    return df

def save_and_compress_data(df):
    file_path = 'link_budget_data.csv'
    df.to_csv(file_path, index=False)
    # Compressing the file
    with ZipFile('link_budget_data.zip', 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    os.remove(file_path)  # Remove the CSV file after compression
    logging.info(f"Data saved and compressed to link_budget_data.zip")

if __name__ == "__main__":
    init_logger()
    logging.info("Starting link budget calculations")

    # Generate data
    link_budget_data = generate_link_budget_data()

    # Save and compress data
    save_and_compress_data(link_budget_data)
    logging.info("Link budget calculations completed and data compressed")
