import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from openpyxl import Workbook
from datetime import datetime
import time
import os

def saveToFileCSV(buff: list) -> None:
    buff: list = np.array(buff)
    data: dict = {
        'x_sensity' : buff[:, 1],
        'y_sensity' : buff[:, 2],
        'zenith_sensity' : buff[:, 3],
        'azimuth_sensity' : buff[:, 4],
        'Rotator_Zenith_angle' : buff[:, 5],
        'Rotator_Azimuth_angle' : buff[:, 0],
        'Radius' : buff[:, 6]
    }
    toFile: str = datetime.now().strftime(f"{'IntensityTables'}\\%m-%d-%Y_%H-%M-%S_Intensity.csv")
    df = pd.DataFrame(data)
    df.to_csv(toFile, index = False, header = False, sep = ' ', na_rep = 'nan')

def downloadFile(filename: str) -> list:
    calibMatrix: list = []
    with open(filename, 'r+', encoding='utf-8') as file:
        for _, line in enumerate(file):
            calibMatrix.append([str_num for str_num in line.split()])
    return calibMatrix

def convertDataFormXLS(data: list) -> list:
    '''Converts exponential to string with a dot as a delimeter with four digits for XSLS files'''
    return [y.replace(',', '.') for y in np.array(data)]

def convertDataFormCSV(data: tuple) -> tuple:
    '''Converts exponential to float with four digits for CSV and TXT files'''
    return tuple([round(float(x), 4) for x in np.array(data)])

if __name__ == '__main__':
    buff = downloadFile('IntensityTables/test.txt')
    new = [convertDataFormXLS(y) for y in buff]
    # new_2 = [convertDataFormCSV(x) for x in new]
    saveToFileCSV(new)
