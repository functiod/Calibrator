import numpy as np
import pandas as pd
from optical_stand.calibrator.data_processing.file_processing import read_calib_from_csv
from scipy.stats import moment
from scipy.optimize import lsq_linear

dispersion_moment: int = 2
order_of_polynom: int = 6

def find_matrix_dispersion(df: pd.DataFrame) -> pd.DataFrame:
    my_df: pd.DataFrame = df
    zenith_df: pd.Series = my_df.loc[:, ['zenith angle']].drop_duplicates(ignore_index=True)
    radius_col: pd.DataFrame = my_df.loc[:, ['radius sens']]
    amount_unique_cells: int = len(zenith_df)
    number_azim_steps: int = len(radius_col) // amount_unique_cells
    dispersion_list: list = []
    dispersion: float = 0.0
    for i in range(amount_unique_cells):
        dispersion: float = round(float(moment(radius_col[i*number_azim_steps:(i+1)*number_azim_steps], dispersion_moment)), 3)
        dispersion_list.append(dispersion)
    dispersion_df: pd.DataFrame = pd.DataFrame({'radius dispersion' : dispersion_list})
    dispersion_df = zenith_df.join(dispersion_df)
    result_df: pd.DataFrame = my_df.merge(dispersion_df, left_on='zenith angle', right_on='zenith angle')
    return result_df

def find_coax_zenith(df: pd.DataFrame) -> float:
    my_df: pd.DataFrame = df
    dispersion: np.ndarray = my_df['radius dispersion'].to_numpy()
    min_dev: float = np.min(dispersion)
    coax_zenith_angle: float = my_df.loc[df['radius dispersion'] == min_dev, 'zenith angle'].iloc[0]
    return coax_zenith_angle

def define_aprox_coefs(df: pd.DataFrame) -> list:
    '''Находим коэффициенты апроксимирующего полинома шестой степени из калибровочных данных'''
    calib_df: pd.DataFrame = df
    radius: list = calib_df['radius sens'].to_numpy()
    thetta: list = calib_df['zenith angle'].to_numpy()
    A: list = np.vstack([radius**i for i in range(order_of_polynom + 1)]).T
    coefficients: list = lsq_linear(A, thetta).x
    return coefficients

def define_aprox_polynom(df: pd.DataFrame) -> np.poly1d:
    '''Находим полином шестой степени по коэффициентам'''
    calib_df: pd.DataFrame = df
    calib_coefs: list = define_aprox_coefs(calib_df)
    calib_polynomial: np.poly1d = np.poly1d(np.flip(calib_coefs))
    return calib_polynomial

def find_angle_error(df: pd.DataFrame) -> np.ndarray:
    '''Находим отклонение теоретических данных от экспериментальных'''
    calib_df: pd.DataFrame = df
    calib_polynom: np.poly1d = define_aprox_polynom(calib_df)
    theor_data: np.ndarray = calib_df['radius sens'].to_numpy()
    exp_dat: np.ndarray = calib_df['zenith angle'].to_numpy()
    deviation_buff: np.ndarray = calib_polynom(theor_data) - exp_dat
    return deviation_buff