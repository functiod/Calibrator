import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from optical_stand.calibrator.data_processing.calc import define_aprox_polynom, find_angle_error

def plot_teor_exp_calib(df: pd.DataFrame) -> None:
    '''График экспериментальных данных с апроксимирующей кривой'''
    calib_df: pd.DataFrame = df
    x_min: float = np.min(calib_df['radius sens'].to_numpy())
    x_max: float = np.max(calib_df['radius sens'].to_numpy())
    x_new: np.ndarray = np.linspace(x_min, x_max, x_max)
    y_new: np.ndarray = define_aprox_polynom(calib_df)(x_new)

    x: np.ndarray = calib_df['radius sens'].to_numpy()
    y: np.ndarray = calib_df['zenith angle'].to_numpy()

    fig, ax = plt.subplots()
    ax.set_title('Thetta to radius')
    plt.plot(x_new, y_new, '-', x, y, '.')

    plt.show()

def plotZenithDeviation(df: pd.DataFrame) -> None:
    calib_df: pd.DataFrame = df
    y_new: np.ndarray = find_angle_error(calib_df)
    y: np.ndarray = calib_df['zenith angle'].to_numpy()

    fig, ax = plt.subplots()
    ax.set_title('Thetta to radius')
    plt.scatter(y, y_new, marker='o', c = 'r', label = 'Python data')
    plt.xticks(np.arange(0, 60, step=2))
    plt.yticks(np.arange(-0.20, 0.20, step=0.025))
    plt.grid(True)
    plt.show()

# def init_graph(self) -> None:
#     '''Inits a real time graph'''
#     self.ax.set_rticks([250, 300, 350, 400])
#     self.ax.set_rlabel_position(-22.5)
#     self.ax.grid(True)
#     self.ax.set_title('Intensity to azimuth angle')

#     plt.show(block=False)

# def update_plot(self, new_data: list) -> None:
#     '''Updates a real time graph with new dotes'''
#     x_new_data: list = new_data[self.xSensCol]
#     y_new_data: list = new_data[self.ySensCol]
#     self.ax.plot(x_new_data, y_new_data, '.')

#     plt.draw()
#     plt.pause(0.01)