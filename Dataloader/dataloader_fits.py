import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset
from skimage import io
from astropy.io import fits


class SunImageDataset(Dataset):
    def __init__(self, csv_file, offset=None, transform=None):
        self.annotaions = pd.read_csv(csv_file)
        self.offset = offset
        # self.transform = transform

    def __len__(self):
        return len(self.annotaions)

    def __getitem__(self, index):
        list_of_images = []
        y_label = torch.tensor(self.annotaions.iloc[index, 1])
        list_of_paths = eval(self.annotaions.iloc[index, 0])
        for path in list_of_paths:
            # Read FITS file
            hdul = fits.open(path, mode="readonly")
            header = hdul[1].header
            image = hdul[1].data

            # Convert PIL image to numpy array
            # image_array = np.array(image).astype(np.float32)
            image_array = image.astype(np.float32)
            # Apply min-max normalization
            if image_array.max() > image_array.min():  # Avoid division by zero
                image_array = (image_array - image_array.min()) / \
                    (image_array.max() - image_array.min())

            # Convert to tensor
            image = torch.from_numpy(image_array)

            list_of_images.append(image)

            hdul.close()
        # Stack images into a single tensor with shape [10, 1, 224, 224]
        images = torch.stack(list_of_images)
        return images, y_label.float()
