from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

def downloadFile(filename: str) -> list:
        calibMatrix: list = []
        with open(filename, 'r+', encoding='utf-8') as file:
            for _, line in enumerate(file):
                calibMatrix.append([float(str_num) for str_num in line.split()])
        return calibMatrix

def getPolarCoord(filename: str) -> tuple:
        calibBuffer: list = downloadFile(filename)
        rho: list = [np.sqrt(pow(calibBuffer[i][1], 2) +
                                    pow(calibBuffer[i][2], 2))
                                    for i in range(len(calibBuffer))]
        phi: list = [calibBuffer[i][0] for i in range(len(calibBuffer))]
        return (phi, rho)

n_colors = 33
color_list = list(colors._colors_full_map.values())[:n_colors]

def plotPolarCoord() -> None:
    filePath: list = [f"IntensityTables\\{file}" for file in listdir("IntensityTables") if isfile(join("IntensityTables", file))]
    for i, filename in enumerate(filePath):
        fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
        coordBuffer: tuple = getPolarCoord(filename)
        ax.scatter(*coordBuffer, s = 2,  c=color_list)
        ax.set_rticks([250, 300, 350, 400])
        ax.set_rlabel_position(-22.5)
        ax.grid(True)
        ax.set_title('Intensity to azimuth angle')
        plt.plot(*coordBuffer, '.')

        plt.show()

if __name__ == "__main__":
    print(color_list)
