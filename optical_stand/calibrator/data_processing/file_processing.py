from datetime import datetime
import pandas as pd
import numpy as np

def save_calib_to_csv(final_buffer: np.ndarray, folder_path: str = 'utils\IntensityTables') -> None:
    my_buffer: np.ndarray = np.array(final_buffer)
    df: pd.DataFrame = pd.DataFrame(my_buffer, columns=[
        'zen sens', 'azim sens', 'x sens', 'y sens', 'zenith angle', 'azimuth angle'
    ])
    to_file: str = datetime.now().strftime(f"{folder_path}\\%m-%d-%Y_%H-%M-%S_Intensity.csv")
    df.to_csv(to_file, index = False, na_rep = 'nan')

def read_calib_from_csv(file_path: str) -> pd.DataFrame:
    df: pd.DataFrame = pd.read_csv(file_path)
    return df

def download_file(file_path: str) -> np.ndarray:
    calib_matrix: np.ndarray = np.array([])
    with open(file_path, 'r+', encoding = 'utf-8') as file:
        for _, line in enumerate(file):
            np.append(calib_matrix, [float(str_num) for str_num in line.split()])
    return calib_matrix