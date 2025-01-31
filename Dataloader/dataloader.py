import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from skimage import io
from PIL import Image, ImageFile


class SunImageDataset(Dataset):
    def __init__(self, csv_file, offset=None, transform=None):
        self.annotaions = pd.read_csv(csv_file)
        self.offset = offset
        self.transform = transform

    def __len__(self):
        return len(self.annotaions)

    def __getitem__(self, index):
        list_of_images = []
        y_label = torch.tensor(self.annotaions.iloc[index, 1])
        list_of_paths = eval(self.annotaions.iloc[index, 0])
        for path in list_of_paths:
            # image = io.imread(path)
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            image = Image.open(path)
            if image.size != (224, 224):
                image = image.resize((224, 224))
            if self.transform:
                image = self.transform(image)
            list_of_images.append(image)

        return list_of_images, y_label.float()
