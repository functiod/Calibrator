import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import openpyxl
from datetime import datetime
import time
import os
from scipy.optimize import lsq_linear
from scipy.stats import moment
from SunSensor_Lib import setGamSettings, setSettingsMatrix, getImg10bit
from SunSensor_Lib import lupa300_set
from rotatorDriver import Pivot
from rotatorDriver import Axis

class SunSensor:
    cmd: int = 0x04
    photoVerticalSize: int = 480
    photoHorizontalSize: int = 480

    def setSettings(self) -> None:
        '''Set matrix settings'''
        setGamSettings(lupa300_set)
        setSettingsMatrix(lupa300_set)

    def getCentreCoords(self) -> tuple:
        '''Returns [x_sensity, y_sensity, zenith_sensity, azimuth_sensity] of the incident beam'''
        return getImg10bit(lupa300_set, self.cmd, self.photoVerticalSize, self.photoHorizontalSize)

class Device:
    xSensCol: int = 0
    ySensCol: int = 1
    zenSensCol: int = 2
    azimSensCol: int = 3
    zenRotatorCol: int = 4
    azimRotatorCol: int = 5
    radiusSensCol: int = 6
    measurColNum: int = 6

    sleep_time: int = 1

    def __init__(self) -> None:
        self.pivotAzim: Pivot = Pivot(Axis.azimuth)
        self.pivotZenith: Pivot = Pivot(Axis.zenith)
        self.sunSensor: SunSensor = SunSensor()
        self.imageBuffer: list = []
        # self.paramBuffer: list = [initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float,
        #             endZenithAngle: float, numberAzimuthSteps: int, numberZenithSteps: int,
        #             zenithVelocity: float, azimVelocity: float, fixedAngleRepetition: int]
        self.TotNumZenSteps: int = 0
        self.TotNumAzimSteps: int = 0
        # self.fig, self.ax = plt.subplots()

    def initialize(self) -> None:
        '''Commutates both Axes with the controller'''
        self.pivotAzim.initialize()
        self.pivotZenith.initialize()

    def disable(self) -> None:
        '''Decommutates both Axes from the controller'''
        self.pivotAzim.disable()
        self.pivotZenith.disable()

    def setDevZeroPosition(self, initialZenithAngle: float) -> None:
        '''Sets digital zero position in view of physical one. Then goes to a fixed position'''
        self.pivotZenith.setZeroPosition(initialZenithAngle)

    def setDevVelocity(self, azimVelocity: float, zenVelocity: float):
        self.pivotAzim.setVel(azimVelocity)
        self.pivotZenith.setVel(zenVelocity)

    def prepareCalibration(self, initialAzimuthAngle: float, initialZenithAngle: float) -> None:
        '''Sets initial positions on both Axes'''
        self.pivotAzim.absoluteRotation(initialAzimuthAngle)
        self.pivotZenith.absoluteRotation(initialZenithAngle)

    def prepareBuffer(self, numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> None:
        '''Fills the object's buffer with zeros as two dimensional matrix with certain sizes'''
        self.imageBuffer = np.zeros(((numberAzimuthSteps) * (numberZenithSteps + 1) * fixedAngleRepetition,
                                      self.measurColNum + 1))

    def getBuffer(self) -> list:
        return self.imageBuffer

    def convertDataFormCSV(self, data: tuple) -> tuple:
        '''Converts exponential to float with four digits for CSV and TXT files'''
        return tuple([round(float(x), 4) for x in data])

    def __prepareBufferString(self) -> tuple:
        '''Returns tuple(Azimuth_angle, x_sensity, y_sensity, zenith_sensity, azimuth_sensity, Zenith_angle)'''
        data: tuple = (*list(self.sunSensor.getCentreCoords()), self.pivotZenith.getCoord(), self.pivotAzim.getCoord())
        return self.convertDataFormCSV(data)

    def __fillBuffer(self, azimMeasOrder: int, buff: list | None = None) -> None:
        '''Fills the object's buffer string as follows:
            1 column - x sensity;
            2 column - y sensity;
            3 column - zenith sensity;
            4 column - azimuth sensity;
            5 column - Rotator Zenith angle;
            6 column - Rotator Azimuth angle;
            7 column - Radius --> sqrt(x^2 + y^2)
        '''
        buff: list = buff or self.imageBuffer
        stringBuffer: list = list(self.__prepareBufferString())
        for i in range(self.measurColNum):
            if i == self.xSensCol:
                buff[azimMeasOrder][i] = stringBuffer[i]
            elif i == self.ySensCol:
                buff[azimMeasOrder][i] = stringBuffer[i]
            else:
                buff[azimMeasOrder][i] = stringBuffer[i]
        buff[azimMeasOrder][self.radiusSensCol] = (np.sqrt(pow(buff[azimMeasOrder][self.xSensCol], 2) +
                                                                    pow(buff[azimMeasOrder][self.ySensCol], 2)))

    def request_sensor(self, buff: list | None = None) -> list:
        '''Sets sensor's settings and requests for coordinates.
            Fills the object's buffer string with the coordinates.
            Optionally: return x and y sensities for real time plotting.
        '''
        buff: list = buff or self.imageBuffer
        self.sunSensor.setSettings()
        self.__fillBuffer(self.TotNumAzimSteps)
        return buff[self.TotNumAzimSteps][:3]


    # def init_graph(self) -> None:
    #     '''Inits a real time graph'''
    #     # self.ax.set_rticks([250, 300, 350, 400])
    #     # self.ax.set_rlabel_position(-22.5)
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

    def __define_step_angle(self, numberSteps: int, initialAngle: float, endAngle: float, step: int) -> float:
       '''Defines the destination angle of the single rotation step'''
       if step % numberSteps == 0:
           angle: float = endAngle
       else:
           angle: float = initialAngle + (endAngle - initialAngle) * (step % numberSteps) / numberSteps
       return angle

    def move_azimuth(self, azimDestAngle: float) -> None:
        '''Moves with a single step to the destination angle.'''
        self.pivotAzim.absoluteRotation(azimDestAngle)
        time.sleep(self.sleep_time)

    def rotate_round_azimuth(self, numberAzimuthSteps: int, initialAzimuthAngle: float, endAzimuthAngle: float, buff: list | None = None) -> None:
        '''Makes a full circular azimuth rotation.
            Fills the object's buffer with the coordinates and untangles the wire.
        '''
        for i in range(numberAzimuthSteps):
            self.move_azimuth(self.__define_step_angle(numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle, self.TotNumAzimSteps))
            print(self.request_sensor(buff))
            self.TotNumAzimSteps += 1
            print('axis 1 - ', self.pivotAzim.getCoord())
            print('axis 0 - ', self.pivotZenith.getCoord())
            print('///////////////////////////////////')
        self.untangleWire()

    def move_zenith(self, zenDestAngle: float) -> None:
        '''Moves with a single step to the destination angle.'''
        self.pivotZenith.absoluteRotation(zenDestAngle)
        print('axis 0 -', self.pivotZenith.getCoord())
        print('///////////////////////////////////')
        time.sleep(self.sleep_time)
        self.TotNumZenSteps += 1

    def rotate_round_zenith(self, numberZenithSteps: int, initialZenithAngle: float, endZenithAngle: float) -> None:
        '''Makes a rotation from the initial angle to the end angle with the certain number of steps'''
        for i in range(numberZenithSteps):
            self.move_zenith(self.__define_step_angle(numberZenithSteps, initialZenithAngle, endZenithAngle, self.TotNumZenSteps))
            print('axis 0 -', self.pivotZenith.getCoord())

    def calibrate(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float, endZenithAngle: float,
                   numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> None:
        '''Makes a fixed number of rotations around the azimuth angle.
            Then makes a rotation around the zenith angle.
            Untangles the sensor's wire making a 360 back rotation'''
        for i in range(numberZenithSteps + 1):
            self.move_zenith(self.__define_step_angle(numberZenithSteps, initialZenithAngle, endZenithAngle, self.TotNumZenSteps))
            for j in range(fixedAngleRepetition):
                self.rotate_round_azimuth(numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle)


    def untangleWire(self) -> None:
        self.pivotAzim.absoluteRotation(0.0)

class Calibrator(Device):
    calibFolder: str = "IntensityTables"
    order_of_polynom: int = 6
    zenithDevCol: int = 7

    def __init__(self) -> None:
        super().__init__()

    def alignCenter(self, buffer: list | None = None, from_file: str = '') -> list:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer if buffer.any() else self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        # npBuff[:, self.zenRotatorCol] = npBuff[:, self.zenRotatorCol] - 272.5
        npbuffer[:, self.radiusSensCol] = np.sqrt((npbuffer[:, self.xSensCol] - 238.25)**2 + (npbuffer[:, self.ySensCol] - 242.5)**2)
        return npbuffer

    def saveToFileCSV(self, buffer: list | None = None, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer if buffer.any() else self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        data: dict = {
            'x_sensity' : npbuffer[:, self.xSensCol],
            'y_sensity' : npbuffer[:, self.ySensCol],
            'zenith_sensity' : npbuffer[:, self.zenSensCol],
            'azimuth_sensity' : npbuffer[:, self.azimSensCol],
            'Rotator_Zenith_angle' : npbuffer[:, self.zenRotatorCol],
            'Rotator_Azimuth_angle' : npbuffer[:, self.azimRotatorCol],
            'Radius' : npbuffer[:, self.radiusSensCol]
        }
        to_file: str = datetime.now().strftime(f"{self.calibFolder}\\%m-%d-%Y_%H-%M-%S_Intensity.csv")
        df = pd.DataFrame(data)
        df.to_csv(to_file, index = False, header = False, sep = ' ', na_rep = 'nan')

    def downloadFile(self, filename: str) -> list:
        calibMatrix: list = []
        with open(filename, 'r+', encoding = 'utf-8') as file:
            for _, line in enumerate(file):
                calibMatrix.append([float(str_num) for str_num in line.split()])
        return calibMatrix

    def saveToXLSX(self, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        to_file: str = datetime.now().strftime(f"{self.calibFolder}\\%m-%d-%Y_%H-%M-%S_Intensity.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        for row in npbuffer:
            ws['A1:A{}'.format(len(row))][0][0].number_format = '0.0000'
            ws.append(list(row))
        wb.save(to_file)

    def defineAproxPolynom(self, buffer: list)-> list:
        npbuffer: np.ndarray = np.array(buffer)
        radius: list = npbuffer[:, self.radiusSensCol]
        thetta: list = npbuffer[:, self.zenRotatorCol]
        A: list = np.vstack([radius**i for i in range(self.order_of_polynom + 1)]).T
        coefficients: list = lsq_linear(A, thetta).x
        return coefficients

    def plotAproxPolynom(self, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        coefs: list = self.defineAproxPolynom(npbuffer)
        x: list = npbuffer[:, self.radiusSensCol]
        y: list = npbuffer[:, self.zenRotatorCol]
        polynomial = np.poly1d(np.flip(coefs))
        xnew: list = np.linspace(0, 200, 200)
        ynew: list = polynomial(xnew)
        # excel_coefs: list = [-0.453618892, 0.460921313, -0.003197088, 5.04852E-05, -4.70544E-07, 2.05266E-09, -3.38893E-12]
        # polynomial_excel = np.poly1d(np.flip(excel_coefs))
        # y_excel: list = polynomial_excel(xnew)

        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_title('Thetta to radius')
        plt.plot(xnew, ynew, '-', x, y, '.')

        plt.show()

    def defineZenithDeviation(self, buffer: list) -> tuple:
        npbuffer: np.ndarray = np.array(buffer)
        coefs: list = self.defineAproxPolynom(npbuffer)
        coefs_excel: list = [-0.453618892, 0.460921313, -0.003197088, 5.04852E-05, -4.70544E-07, 2.05266E-09, -3.38893E-12]
        polynomial = np.poly1d(np.flip(coefs))
        polynomial_excel = np.poly1d(np.flip(coefs_excel))
        deviationBuff: list = [polynomial(npbuffer[:, self.radiusSensCol]) - npbuffer[:, self.zenRotatorCol],
                               polynomial_excel(npbuffer[:, self.radiusSensCol]) - npbuffer[:, self.zenRotatorCol]]
        angleBuff: list = npbuffer[:, self.zenRotatorCol]
        return (angleBuff, deviationBuff)

    def plotZenithDeviation(self, buffer: list | None = None, from_file: str = '') -> None:
        if from_file != '':
            mybuffer: list = self.downloadFile(from_file)
        else:
            mybuffer: list = buffer if buffer.any() else self.imageBuffer
        npbuffer: np.ndarray = np.array(mybuffer)
        angleBuff, deviationBuff = self.defineZenithDeviation(npbuffer)

        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_title('Zenith angle deviation')
        plt.xlim(-0.5, 60)
        plt.ylim(-0.5, 0.5)
        plt.scatter(angleBuff, deviationBuff[0], marker='o', c = 'r')
        plt.scatter(angleBuff, deviationBuff[1], marker='^', c = 'b')
        plt.show()

if __name__ == '__main__':
    calibrator: Calibrator = Calibrator()
    # calibrator.saveToFileCSV(calibrator.alignCenter(buffer = calibrator.downloadFile('IntensityTables/06-27-2023_17-45-35_Intensity.csv')))
    # print(calibrator.defineAproxPolynom('IntensityTables/06-27-2023_13-21-58_Intensity.csv'))
    # calibrator.plotAproxPolynom('IntensityTables/06-27-2023_13-21-58_Intensity.csv')
    # print(calibrator.defineZenithDeviation(from_file = 'IntensityTables/06-27-2023_13-21-58_Intensity.csv'))
    # calibrator.plotZenithDeviation(from_file='IntensityTables/06-27-2023_17-59-53_Intensity.csv')
    # device.initialize()
    # device.setDevVelocity(50, 50)
    # device.setDevZeroPosition(90.0)
    # device.prepareCalibration(0.0, 272.5)
    # device.prepareBuffer(4, 4, 1)
    # device.calibrate(0.0, 272.5, 360.0, 312.5, 4, 4, 1)
    # calibrator.saveToXLSX('test_2')
    # calibrator.saveToFileCSV(device.imageBuffer)
    # calibrator.disable()
