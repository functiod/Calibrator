import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from optical_stand.calibrator.data_processing.file_processing import read_calib_from_csv

order_of_polynom: int = 6

def define_aprox_coefs(df_calib: pd.DataFrame | str) -> list:
    '''Находим коэффициенты апроксимирующего полинома шестой степени из калибровочных данных'''
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    radius: list = df['radius sens'].to_numpy()
    thetta: list = df['zenith angle'].to_numpy()
    A: list = np.vstack([radius**i for i in range(order_of_polynom + 1)]).T
    coefficients: list = lsq_linear(A, thetta).x
    return coefficients

def define_aprox_polynom(df_calib: pd.DataFrame | str) -> np.poly1d:
    '''Находим полином шестой степени по коэффициентам'''
    df: pd.DataFrame = df_calib
    calib_coefs: list = define_aprox_coefs(df)
    calib_polynomial: np.poly1d = np.poly1d(np.flip(calib_coefs))
    return calib_polynomial

def find_angle_error(df_calib: pd.DataFrame | str) -> np.ndarray:
    '''Находим отклонение теоретических данных от экспериментальных'''
    df: pd.DataFrame = df_calib
    calib_polynom: np.poly1d = define_aprox_polynom(df)
    theor_data: np.ndarray = df['radius sens'].to_numpy()
    exp_dat: np.ndarray = df['zenith angle'].to_numpy()
    deviation_buff: np.ndarray = calib_polynom(theor_data) - exp_dat
    return deviation_buff
