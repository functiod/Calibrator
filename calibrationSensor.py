from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import time
from SunSensor_Lib import setGamSettings, setSettingsMatrix, getImg10bit
from SunSensor_Lib import lupa300_set
from rotatorDriver import Pivot
from rotatorDriver import Axis

class SunSensor:
    sensorAddress: int = 0x04
    photoVerticalSize: int = 480
    photoHorizontalSize: int = 480
    comPort: str = 'COM3'

    def setSettings(self) -> None:
        setGamSettings(lupa300_set)
        setSettingsMatrix(lupa300_set)

    def getCentreCoords(self) -> tuple:
        return getImg10bit(lupa300_set, self.sensorAddress, self.photoVerticalSize, self.photoHorizontalSize)

class Device:
    measurColNum: int = 6
    azimuthCol: int = 0
    xSensCol: int = 1
    ySensCol: int = 2
    radiusSensCol: int = 6
    zenithSensCol: int = 4
    relativeZenithCol: int = 5

    def __init__(self) -> None:
        self.pivotAzim: Pivot = Pivot(Axis.azimuth)
        self.pivotZenith: Pivot = Pivot(Axis.zenith)
        self.sunSensor: SunSensor = SunSensor()
        self.imageBuffer: list = []
        self.normalFallBuffer: list = [0.1, 2.374121398925781250e+02, 2.284291534423828125e+02,
                                        1.396406292915344238e+00, 4.900190734863281250e+01, 2.725000122070312614e+02]
        self.TotNumZenSteps: int = 0
        self.TotNumAzimSteps: int = 0
        self.fig, self.ax = plt.subplots()

    def initialize(self) -> None:
        # if self.devInt.initRequest():
        self.pivotAzim.initialize()
        self.pivotZenith.initialize()

    def disable(self) -> None:
        # if self.devInt.disableRequest():
        self.pivotAzim.disable()
        self.pivotZenith.disable()

    def setDevZeroPosition(self, initialZenithAngle: float) -> None:
        # self.pivotAzim.setZeroPosition(self.devInt.initialAzimuthAngle)
        self.pivotZenith.setZeroPosition(initialZenithAngle)

    def prepareCalibration(self, initialAzimuthAngle: float, initialZenithAngle: float) -> None:
        self.pivotAzim.absoluteRotation(initialAzimuthAngle)
        self.pivotZenith.absoluteRotation(initialZenithAngle)

    def prepareBuffer(self, numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> None:
        self.imageBuffer = np.zeros(((numberAzimuthSteps) * numberZenithSteps *
                                     fixedAngleRepetition, self.measurColNum + 1))

    def getBuffer(self) -> list:
        return self.imageBuffer

    def __prepareBufferString(self) -> tuple:
        return (self.pivotAzim.getCoord(), *list(self.sunSensor.getCentreCoords()),
                abs(self.pivotZenith.getCoord() - self.normalFallBuffer[self.zenithSensCol + 1]))

    def __fillBuffer(self, azimMeasOrder: int) -> None:
        stringBuffer: list = list(self.__prepareBufferString())
        for i in range(self.measurColNum):
            if i == self.xSensCol:
                self.imageBuffer[azimMeasOrder][i] = round((abs(stringBuffer[i] - 237.96079999999998)), 4)
            elif i == self.ySensCol:
                self.imageBuffer[azimMeasOrder][i] = round((abs(stringBuffer[i] - 229.84697500000001)), 4)
            else:
                self.imageBuffer[azimMeasOrder][i] = stringBuffer[i]
        self.imageBuffer[azimMeasOrder][self.measurColNum] = round((np.sqrt(pow(self.imageBuffer[azimMeasOrder][self.xSensCol], 2) +
                                                                    pow(self.imageBuffer[azimMeasOrder][self.ySensCol], 2))), 4)

    def request_sensor(self) -> list:
        self.sunSensor.setSettings()
        self.__fillBuffer(self.TotNumAzimSteps)
        return self.imageBuffer[self.TotNumAzimSteps][:3]

    def circle_azimuth(self, numberAzimuthSteps: int, initialAzimuthAngle: float, endAzimuthAngle: float) -> None:
        for k in range(numberAzimuthSteps):
            self.pivotAzim.absoluteRotation(initialAzimuthAngle + k * (endAzimuthAngle - initialAzimuthAngle) / numberAzimuthSteps)
            time.sleep(1)
            self.update_plot(self.request_sensor())
            self.TotNumAzimSteps += 1
        self.untangleWire()

    def init_graph(self) -> None:
        # self.ax.set_rticks([250, 300, 350, 400])
        # self.ax.set_rlabel_position(-22.5)
        self.ax.grid(True)
        self.ax.set_title('Intensity to azimuth angle')

        plt.show(block=False)

    def update_plot(self, new_data: list) -> None:
        x_new_data: list = new_data[self.xSensCol]
        y_new_data: list = new_data[self.ySensCol]
        self.ax.plot(x_new_data, y_new_data, '.')

        plt.draw()
        plt.pause(0.01)

    def calibrate_azimuth(self, numberAzimuthSteps: int, initialAzimuthAngle: float, endAzimuthAngle: float, fixedAngleRepetition: int) -> list:
        for j in range(fixedAngleRepetition):
            self.circle_azimuth(numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle)

    def circle_zenith(self, initialAzimuthAngle: float, initialZenithAngle: float, endZenithAngle: float, numberZenithSteps: int,
                       numberAzimuthSteps: int, fixedAngleRepetition: int) -> None:
            self.pivotZenith.absoluteRotation(initialZenithAngle + self.TotNumAzimSteps // (numberAzimuthSteps * fixedAngleRepetition) *
                                              (endZenithAngle - initialZenithAngle) / numberZenithSteps)

    def Calibrate(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float,
                    endZenithAngle: float, numberAzimuthSteps: int, numberZenithSteps: int,
                    zenithVelocity: float, azimVelocity: float, fixedAngleRepetition: int) -> None:
        self.pivotAzim.setVel(azimVelocity)
        self.pivotZenith.setVel(zenithVelocity)
        self.pivotAzim.absoluteRotation(initialAzimuthAngle)
        self.init_graph()
        while self.TotNumAzimSteps // (numberAzimuthSteps * fixedAngleRepetition) != numberZenithSteps:
            self.calibrate_azimuth(numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle, fixedAngleRepetition)
            self.circle_zenith(initialAzimuthAngle, initialZenithAngle, endZenithAngle, numberZenithSteps, numberAzimuthSteps, fixedAngleRepetition)

    # def Calibrate(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float,
    #         endZenithAngle: float, numberAzimuthSteps: int, numberZenithSteps: int,
    #         zenithVelocity: float, azimVelocity: float, fixedAngleRepetition: int) -> None:
    #     self.pivotAzim.setVel(azimVelocity)
    #     self.pivotZenith.setVel(zenithVelocity)
    #     for p in range(numberZenithSteps):
    #         self.firstStageCalib(p, numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle, fixedAngleRepetition)
    #         self.secondStageCalib(p + 1, initialAzimuthAngle, initialZenithAngle, endZenithAngle, numberZenithSteps)

    def untangleWire(self) -> None:
        self.pivotAzim.absoluteRotation(0)

class Calibrator(Device):
    folderName: str = "IntensityTables"

    def __init__(self) -> None:
        super().__init__()

    def saveToFile(self, buffer: list) -> str:
        toFile: str = datetime.now().strftime(f"{self.folderName}\\%m-%d-%Y_%H-%M-%S_Intensity.csv")
        np.savetxt(toFile, buffer)
        return toFile

    def downloadFile(self, filename: str) -> list:
        calibMatrix: list = []
        with open(filename, 'r+', encoding='utf-8') as file:
            for _, line in enumerate(file):
                calibMatrix.append([float(str_num) for str_num in line.split()])
        return calibMatrix

    def getPolarCoord(self, filename: str) -> tuple:
        calibBuffer: list = self.downloadFile(filename)
        rho: list = [np.sqrt(pow(calibBuffer[i][self.xSensCol], 2) +
                                    pow(calibBuffer[i][self.ySensCol], 2))
                                    for i in range(len(calibBuffer))]
        phi: list = [calibBuffer[i][self.azimuthCol] * np.pi / 180 for i in range(len(calibBuffer))]
        return (phi, rho)

    # def plotPolarCoord(self) -> None:
    #     filePath: list = [f"{self.folderName}\\{file}" for file in listdir(self.folderName) if isfile(join(self.folderName, file))]
    #     for filename in filePath:
    #         fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
    #         coordBuffer: tuple = self.getPolarCoord(filename)
    #         ax.scatter(*coordBuffer)
    #         ax.set_rticks([250, 300, 350, 400])
    #         ax.set_rlabel_position(-22.5)
    #         ax.grid(True)
    #         ax.set_title('Intensity to azimuth angle')
    #         plt.plot(*coordBuffer, '.')

    #         plt.show()

    def getNormalFallCoord(self) -> None:
        self.sunSensor.setSettings()
        self.normalFallBuffer = list((*self.sunSensor.getCentreCoords(), self.pivotZenith.getCoord()))
        np.savetxt("normalFallCoord.txt", self.normalFallBuffer)

    def plotThettaRadiusGraph(self) -> None:
        y_arr: list = self.getBuffer()[self.relativeZenithCol]
        x_arr: list = self.getBuffer()[self.radiusSensCol]
        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_title('Thetta to radius')
        plt.plot(x_arr, y_arr, '.')

        plt.show()

    def avg_value(self) -> None:
        buff: list = self.downloadFile('IntensityTables//05-16-2023_12-09-34_Intensity.csv')
        x_arr: list = [buff[i][1] for i in range(8)]
        y_arr: list = [buff[i][2] for i in range(8)]
        print(np.average(x_arr), np.average(y_arr))
    # def getSensSysPolarCoord(self, filename: str) -> list:
    #     normalFallBuff: list = self.downloadFile("normalFallCoord.txt")
    #     calibBuffer: list = self.downloadFile(filename)
    #     rho: list = [np.sqrt(pow(calibBuffer[i][self.xSensCol] - normalFallBuff[self.xSensCol][0], 2) +
    #                     pow(calibBuffer[i][self.ySensCol] - normalFallBuff[self.ySensCol][0], 2))
    #                     for i in range(len(calibBuffer))]
    #     return rho

    # def getSensSysAvgPolarCoord(self, filename: str, numberZenithSteps: int, numberAzimuthSteps: int, fixedAngleRepetition: int) -> list:
    #     sensSysPolarCoord: list = self.getSensSysPolarCoord(filename)
    #     calibBuffer: list = self.downloadFile(filename)
    #     same_angle_lines_number: int = numberZenithSteps * fixedAngleRepetition
    #     tempBuff: list = [sensSysPolarCoord[i * numberAzimuthSteps:(i + 1) * numberAzimuthSteps]
    #                       for i in range(same_angle_lines_number)]
    #     theta: list = [calibBuffer[i * numberAzimuthSteps][self.relativeZenithCol] for i in range(same_angle_lines_number)]
    #     sysAvgSensTuple: list = [(theta[i], np.average(tempBuff[i])) for i in range(same_angle_lines_number)]
    #     return sysAvgSensTuple


if __name__ == '__main__':
    calibrator: Calibrator = Calibrator()
    calibrator.avg_value()
    # calibrator.initialize()
    # calibrator.setDevZeroPosition(272.5)
    # calibrator.prepareCalibration(0, 272.5)
    # calibrator.getNormalFallCoord()
    # calibrator.prepareBuffer(8, 4)
    # calibrator.Calibrate(0.0, 60.0, 360.0, 120.0, 8, 4)
    # calibrator.saveToFile(calibrator.getBuffer())
    # calibrator.disable()
