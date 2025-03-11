import os
import numpy as np

from sunpy.net import Fido, attrs as a
import astropy.units as u

import sunpy.map
from astropy.io import fits

from aiapy.calibrate import correct_degradation
from aiapy.calibrate.util import get_correction_table

import matplotlib.pyplot as plt

from tqdm import tqdm

import cv2
from PIL import Image

import shutil

import time
import datetime
from dateutil.relativedelta import relativedelta

from concurrent.futures import ThreadPoolExecutor

download_dir = 'D:\\AIA testing 3'

# List all files in the download directory
aia_files = [os.path.join(download_dir, f)
             for f in os.listdir(download_dir) if f.endswith('.fits')]


def clip_scale_values(aia_file):
    aia_file_path = os.path.join(download_dir, aia_file)
    try:
        with fits.open(aia_file_path, mode="update", memmap=False) as hdul:
            data = hdul[1].data

            # Calculate percentiles for this specific image
            p1 = max(np.percentile(data, 1), 0)  # Ensure p1 is at least 0
            p99 = np.percentile(data, 99)

            # Clip the values between p1 and p99
            data_clipped = np.clip(data, p1, p99)

            data_clipped = np.sqrt(data_clipped)

            # # Standardize the data (zero mean, unit variance)
            # mean_val = np.mean(data_clipped)
            # std_val = np.std(data_clipped)
            # data_clipped = (data_clipped - mean_val) / std_val

            # data_clipped = np.sqrt(data_clipped)

            min_val = np.min(data_clipped)
            max_val = np.max(data_clipped)
            data_clipped = (data_clipped - min_val) / (max_val - min_val)
            # Save the processed image
            hdul[1].data = data_clipped

    except Exception as e:
        return f"FILE CORRUPTED: {aia_file_path}, Error: {e}"

    return None


with ThreadPoolExecutor(max_workers=30) as executor:
    list(tqdm(executor.map(clip_scale_values, aia_files),
         total=len(aia_files), desc="Clipping Values"))


# def rescale_to_log10(aia_file):
#     aia_file_path = os.path.join(download_dir, aia_file)
#     try:
#         with fits.open(aia_file_path, mode="update", memmap=False) as hdul:
#             header = hdul[1].header
#             data = hdul[1].data
#             # Apply log10 scaling (adding 1 to avoid log10(0))
#             # data_log = np.log10(data + 1)

#             # Apply min-max scaling to normalize values to [0, 1] range
#             min_val = np.min(data)
#             max_val = np.max(data)
#             data_log10 = (data - min_val) / (max_val - min_val)

#             # Save the rescaled image
#             hdul[1].data = data_log10

#     except Exception as e:
#         return f"FILE CORRUPTED: {aia_file_path}, Error: {e}"

#     return None


# with ThreadPoolExecutor(max_workers=20) as executor:
#     list(tqdm(executor.map(rescale_to_log10, aia_files),
#          total=len(aia_files), desc="Rescaling to log10"))
