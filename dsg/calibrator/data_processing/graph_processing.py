import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dsg.calibrator.data_processing.calculation import define_aprox_polynom, find_angle_error
from dsg.calibrator.data_processing.file_processing import read_calib_from_csv
from dsg.calibrator.data_processing.calculation import find_zen_angle_dispersion

def plot_teor_exp_calib(df_calib: pd.DataFrame) -> None:
    '''График экспериментальных данных с апроксимирующим полиномом 6 порядка'''
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    x_min: float = np.min(df['radius sens'].to_numpy())
    x_max: float = np.max(df['radius sens'].to_numpy())
    x_new: np.ndarray = np.linspace(x_min, x_max, x_max)
    y_new: np.ndarray = define_aprox_polynom(df)(x_new)

    x: np.ndarray = df['radius sens'].to_numpy()
    y: np.ndarray = df['zenith angle'].to_numpy()

    fig, ax = plt.subplots()
    ax.set_title('Thetta to radius')
    plt.plot(x_new, y_new, '-', x, y, '.')
    plt.show()

def plot_zenith_deviation(df_calib: pd.DataFrame) -> None:
    '''График отклонения экспериментального угла от теоретического'''
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    y_new: np.ndarray = find_angle_error(df)
    y: np.ndarray = df['zenith angle'].to_numpy()

    fig, ax = plt.subplots()
    ax.set_title('Thetta to radius')
    plt.scatter(y, y_new, marker='o', c = 'r', label = 'Python data')
    plt.xticks(np.arange(0, 60, step=2))
    plt.yticks(np.arange(-0.20, 0.20, step=0.025))
    plt.grid(True)
    plt.show()

def plot_exp_zenith_angle(df_calib: pd.DataFrame | str) -> None:
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    exp_zen_angle: np.ndarray = df['zen sens'].to_numpy()
    theor_zen_angle: np.ndarray = df['zenith angle'].to_numpy()

    fig = plt.figure(figsize=(14, 7))
    axes = fig.subplots(nrows=1, ncols=2)
    axes[0].scatter(theor_zen_angle, abs(exp_zen_angle), c='g', s=15)
    axes[0].scatter(theor_zen_angle, abs(theor_zen_angle), c='r', s=15)
    axes[0].set_title('Зенитный угол датчика')
    axes[0].grid(True)
    axes[0].legend(['Датчик', 'Ротатор'])
    axes[0].set_xlabel('Угол поворта, град.')
    axes[0].set_ylabel('Угол датчика и поворота, град.')
    axes[1].scatter(theor_zen_angle, abs(abs(exp_zen_angle) - abs(theor_zen_angle)), s=15)
    axes[1].set_title('Ошибка зенитного угла датчика')
    axes[1].grid(True)
    axes[1].legend(['Ошибка'])
    axes[1].set_xlabel('Угол поворта, град.')
    axes[1].set_ylabel('Отклонение угла датчика, град.')
    plt.show()

def plot_exp_angle_dispersion(df_calib: pd.DataFrame | str) -> None:
    if isinstance(df_calib, pd.DataFrame):
        df: pd.DataFrame = df_calib
    elif isinstance(df_calib, str):
        df: pd.DataFrame = read_calib_from_csv(df_calib)
    else:
        raise Exception("Wrong DataFrame type")
    theor_zen_angle: np.ndarray = df['zenith angle'].to_numpy()
    plt.scatter(theor_zen_angle, find_zen_angle_dispersion(df_calib), s=15)
    plt.grid(True)
    plt.xlabel('Угол поворота, град.')
    plt.ylabel('Дисперсия угла')
    plt.title('Дисперсия угла датчика')
    plt.show()