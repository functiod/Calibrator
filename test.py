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
        x_arr: list = [calibBuffer[i][1] for i in range(len(calibBuffer))]
        y_arr: list = [calibBuffer[i][2]  for i in range(len(calibBuffer))]
        return (x_arr, y_arr)

def plotPolarCoord() -> None:
    filePath: list = [f"IntensityTables\\{file}" for file in listdir("IntensityTables") if isfile(join("IntensityTables", file))]
    for i, filename in enumerate(filePath):
        fig, ax = plt.subplots()
        coordBuffer: tuple = getPolarCoord(filename)
        ax.scatter(*coordBuffer, s = 10)
        # ax.set_rticks([250, 300, 350, 400])
        # ax.set_rlabel_position(-22.5)
        ax.grid(True)
        ax.set_title('Intensity to azimuth angle')
        plt.plot(*coordBuffer, '.')

        plt.show()

if __name__ == "__main__":
    plotPolarCoord()
