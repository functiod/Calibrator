import numpy as np
import pandas as pd
from dsg.calibrator.data_processing.rotator_alignment import get_coax_coords
from dsg.calibrator.data_processing.file_processing import read_calib_from_csv
from dsg.calibrator.data_processing.calculation import define_aprox_coefs
from dsg.calibrator.data_processing.rotator_alignment import find_coax_x_y

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
                buffer[i][j] = round(buffer[i][j] - coax_coord['zenith coax'], 4)
            elif j == x_sens_col_num:
                buffer[i][j] = round(buffer[i][j] - coax_coord['x coax'], 4)
            elif j == y_sens_col_num:
                buffer[i][j] = round(buffer[i][j] - coax_coord['y coax'], 4)
    return buffer

def prepare_calib_buffer(df_intensity: pd.DataFrame | str, df_normal: pd.DataFrame | str) -> list:
    if isinstance(df_intensity, pd.DataFrame):
        df_intens: pd.DataFrame = df_intensity
    elif isinstance(df_intensity, str):
        df_intens: pd.DataFrame = read_calib_from_csv(df_intensity)
    else:
        raise Exception("Wrong DataFrame type")
    if isinstance(df_normal, pd.DataFrame):
        df_norm: pd.DataFrame = df_normal
    elif isinstance(df_normal, str):
        df_norm: pd.DataFrame = read_calib_from_csv(df_normal)
    else:
        raise Exception("Wrong DataFrame type")
    coefs: list = list(define_aprox_coefs(df_intens))
    coax_x_y: list = list(find_coax_x_y(df_norm))
    final_buffer: list = coefs + coax_x_y + [0.0] + [1.0] + [3.0]
    return final_buffer