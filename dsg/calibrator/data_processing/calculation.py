import numpy as np
import pandas as pd
from scipy.optimize import lsq_linear
from scipy.stats import moment
from dsg.calibrator.data_processing.file_processing import read_calib_from_csv

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

def find_zen_angle_dispersion(df_calib: pd.DataFrame | str) -> np.ndarray:
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    dispersion_order: int = 2
    digits: int = 4
    rows_num: int = df.index.stop
    zenith_steps_num: int = len(df.loc[:, 'zenith angle'].drop_duplicates())
    zenith_angle_exp: np.ndarray = df.loc[:, 'zen sens'].to_numpy()
    zenith_angle_thoer: np.ndarray = df.loc[:, 'zenith angle'].to_numpy()
    number_azim_steps: int = rows_num // zenith_steps_num
    zenith_dispersion: list = []
    for i in range(zenith_steps_num):
        err: list = abs(abs(zenith_angle_exp[i*number_azim_steps:(i+1)*number_azim_steps])
                            - abs(zenith_angle_thoer[i*number_azim_steps:(i+1)*number_azim_steps]))
        dispersion: float = round(float(moment(err, dispersion_order)), digits)
        zenith_dispersion.append(np.repeat(dispersion, number_azim_steps))
    zenith_dispersion = np.array(zenith_dispersion).flatten()
    return np.array(zenith_dispersion)

# def find_angle_velocity(df_calib: pd.DataFrame | str) -> np.ndarray:
#     if isinstance(df_calib, pd.DataFrame):
#         df: pd.DataFrame = df_calib
#     elif isinstance(df_calib, str):
#         df: pd.DataFrame = read_calib_from_csv(df_calib)
#     else:
#         raise Exception("Wrong DataFrame type")
#     sensor_coord: np.ndarray = df['sensor angle'].to_numpy()
#     time_list: np.ndarray = df['time, sec'].to_numpy()
#     velocity_list: list = []
#     for i in range(len(time_list))

