import numpy as np
import pandas as pd
from scipy.stats import moment
from optical_stand.calibrator.data_processing.file_processing import read_calib_from_csv

dispersion_moment: int = 2
number_of_digits: int = 3


def find_matrix_dispersion(df_calib: pd.DataFrame | str) -> pd.DataFrame:
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    zenith_df: pd.Series = df.loc[:, ['zenith angle']].drop_duplicates(ignore_index=True)
    radius_col: pd.DataFrame = df.loc[:, ['radius sens']]
    amount_unique_cells: int = len(zenith_df)
    number_azim_steps: int = len(radius_col) // amount_unique_cells
    dispersion_list: list = []
    dispersion: float = 0.0
    for i in range(amount_unique_cells):
        dispersion: float = round(float(moment(radius_col[i*number_azim_steps:(i+1)*number_azim_steps], dispersion_moment)), number_of_digits)
        dispersion_list.append(dispersion)
    dispersion_df: pd.DataFrame = pd.DataFrame({'radius dispersion' : dispersion_list})
    dispersion_df = zenith_df.join(dispersion_df)
    result_df: pd.DataFrame = df.merge(dispersion_df, left_on='zenith angle', right_on='zenith angle')
    return result_df

def find_zenith_coax(df_calib: pd.DataFrame | str) -> float:
    '''Находим соосное расположение ротатора по вертикальной оси'''
    df: pd.DataFrame = df_calib
    df: pd.DataFrame = find_matrix_dispersion(df)
    dispersion: np.ndarray = df['radius dispersion'].to_numpy()
    min_dev: float = np.min(dispersion)
    zenith_coax_angle: float = df.loc[df['radius dispersion'] == min_dev, 'zenith angle'].iloc[0]
    return zenith_coax_angle

def find_coax_x_y(df_calib: pd.DataFrame | str) -> float:
    '''Находим зенитный и азимутальный центр матрицы'''
    df: pd.DataFrame = df_calib
    zenith_coax_angle: float = find_zenith_coax(df)
    x_coax: float = np.average(df.loc[df['zenith angle'] == zenith_coax_angle, 'x sens'].to_numpy())
    y_coax: float = np.average(df.loc[df['zenith angle'] == zenith_coax_angle, 'y sens'].to_numpy())
    return x_coax, y_coax

def get_coax_coords(df_calib: pd.DataFrame | str) -> dict:
    df: pd.DataFrame = df_calib
    x, y = find_coax_x_y(df)
    center_coords_dict: dict = {
        'x coax' : x,
        'y coax' : y,
        'zenith coax' : find_zenith_coax(df)
    }
    return center_coords_dict
