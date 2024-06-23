# Carrier-to-Interference Ratio (CIR) Calculation Script for VEDA
# This script generates a comprehensive dataset for CIR considering various carrier and interference levels.

# ## Import necessary libraries
import os
import logging
from multiprocessing import Pool, cpu_count
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from tqdm import tqdm
import numpy as np

# ## Define the CIR class
class CIR:
    def __init__(self, carrier_power, interference_power):
        """Initialize the CIR class"""
       
