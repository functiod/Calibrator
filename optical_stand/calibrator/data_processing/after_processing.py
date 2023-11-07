import numpy as np
import pandas as pd
from optical_stand.calibrator.data_processing.rotator_alignment import get_coax_coords
from optical_stand.calibrator.data_processing.file_processing import read_calib_from_csv

def adjust_calib_data(image_buffer: np.ndarray, df_normal: pd.DataFrame) -> np.ndarray:
    if isinstance(df_normal, pd.DataFrame):
        df: pd.DataFrame = df_normal
    elif isinstance(df_normal, str):
        df: pd.DataFrame = read_calib_from_csv(df_normal)
    else:
        raise Exception("Wrong DataFrame type")
    buffer: np.ndarray = image_buffer
    zenith_col_num: int = df.columns.get_loc('zenith angle')
    x_sens_col_num: int = df.columns.get_loc('x sens')
    y_sens_col_num: int = df.columns.get_loc('y sens')
    coax_coord: dict = get_coax_coords(df)
    for i, sublist in enumerate(buffer):
        for j, _ in enumerate(sublist):
            if j == zenith_col_num:
                buffer[i][j] = buffer[i][j] - coax_coord['zenith coax']
            elif j == x_sens_col_num:
                buffer[i][j] = buffer[i][j] - coax_coord['x coax']
            elif j == y_sens_col_num:
                buffer[i][j] = buffer[i][j] - coax_coord['y coax']
    return buffer
