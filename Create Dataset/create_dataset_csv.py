import os
import pandas as pd
import datetime
from tqdm import tqdm


image_dir = 'D:\Dissertation\Preprocessing\helioviewer_images'
kp_csv_path = 'D:\Dissertation\Kp data\kpdata.csv'

kp_data = pd.read_csv(kp_csv_path)

imagelist = []
label = []


for i in tqdm.tqdm(range(len(kp_data))):
    kp_data_date = datetime.datetime.strptime(
        kp_data['datetime'][i], '%Y-%m-%d').date()
    year = kp_data_date.year
    month = kp_data_date.month
    day = kp_data_date.day
    file_paths = []
    for i in range(20):
        file_paths.append(
            image_dir + f'\\{year:04d}\\AIA_193_' + f'{year:04d}{month:02d}{day:02d}' + f'_{i:02d}0000' + '.jp2')
        if i == 9:
            imagelist.append(file_paths)
            label.append(kp_data['Kp'][i])
            file_paths = []
    imagelist.append(file_paths)
    label.append(kp_data['Kp'][i])

label = [kp for kp in kp_data['Kp'] for _ in range(2)]
print("Length of image list: ", len(imagelist))
print("Length of label list: ", len(label))

# Create a DataFrame with imagelist and label
df = pd.DataFrame({'imagelist': imagelist, 'label': label})
print(df.head())
# Save the DataFrame to a CSV file
output_csv_path = 'D:/Dissertation/dataset.csv'
df.to_csv(output_csv_path, index=False)

print("DataFrame created and saved to CSV.")
