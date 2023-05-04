from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
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
    azimSensCol: int = 3
    zenithSensCol: int = 4
    relativeZenithCol: int = 5
    avrgCol: int = 6

    def __init__(self) -> None:
        self.pivotAzim: Pivot = Pivot(Axis.azimuth)
        self.pivotZenith: Pivot = Pivot(Axis.zenith)
        self.sunSensor: SunSensor = SunSensor()
        self.imageBuffer: list = []
        # self.devInt: Device_interface = Device_interface()

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
                                     fixedAngleRepetition + 1, self.measurColNum))

    def getBuffer(self) -> list:
        return self.imageBuffer

    def __prepareBufferString(self) -> tuple:
        return (self.pivotAzim.getCoord(), *list(self.sunSensor.getCentreCoords()), self.pivotZenith.getCoord())

    def __fillBuffer(self, azimMeasOrder: int) -> None:
        stringBuffer: list = list(self.__prepareBufferString())
        for i in range(self.measurColNum):
            self.imageBuffer[azimMeasOrder][i] = stringBuffer[i]

    def firstStageCalib(self, motionFlag: int, numberAzimuthSteps: int,
                         initialAzimuthAngle: float, endAzimuthAngle: float, fixedAngleRepetition: int) -> None:
        for j in range(fixedAngleRepetition):
            for k in range(numberAzimuthSteps + 1):
                self.pivotAzim.absoluteRotation(initialAzimuthAngle + k * (endAzimuthAngle - initialAzimuthAngle) / numberAzimuthSteps)
                self.sunSensor.setSettings()
                self.__fillBuffer(k + j * numberAzimuthSteps + motionFlag * numberAzimuthSteps * fixedAngleRepetition)
            self.untangleWire()

    def secondStageCalib(self, motionFlag: int, initialAzimuthAngle: float, initialZenithAngle: float,
                        endZenithAngle: float, numberZenithSteps: int) -> None:
        self.pivotAzim.absoluteRotation(initialAzimuthAngle)
        self.pivotZenith.absoluteRotation(initialZenithAngle + motionFlag * (endZenithAngle - initialZenithAngle) / numberZenithSteps)

    def untangleWire(self) -> None:
        self.pivotAzim.absoluteRotation(-360.)

class Calibrator(Device):
    folderName: str = "IntensityTables"

    def __init__(self) -> None:
        super().__init__()

    def Calibrate(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float,
                endZenithAngle: float, numberAzimuthSteps: int, numberZenithSteps: int,
                zenithVelocity: float, azimVelocity: float, fixedAngleRepetition: int) -> None:
        self.pivotAzim.setVel(azimVelocity)
        self.pivotZenith.setVel(zenithVelocity)
        for p in range(numberZenithSteps):
            self.firstStageCalib(p, numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle, fixedAngleRepetition)
            self.secondStageCalib(p + 1, initialAzimuthAngle, initialZenithAngle, endZenithAngle, numberZenithSteps)

    def saveToFile(self, buffer: list) -> str:
        toFile: str = datetime.now().strftime(f"{self.folderName}\\%m-%d-%Y_%H-%M-%S_Intensity.txt")
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
        phi: list = [calibBuffer[i][self.azimuthCol] for i in range(len(calibBuffer))]
        return (phi, rho)

    def plotPolarCoord(self) -> None:
        filePath: list = [f"{self.folderName}\\{file}" for file in listdir(self.folderName) if isfile(join(self.folderName, file))]
        for filename in filePath:
            fig, ax = plt.subplots(subplot_kw={'projection' : 'polar'})
            coordBuffer: tuple = self.getPolarCoord(filename)
            ax.scatter(*coordBuffer)
            ax.set_rticks([250, 300, 350, 400])
            ax.set_rlabel_position(-22.5)
            ax.grid(True)
            ax.set_title('Intensity to azimuth angle')
            plt.plot(*coordBuffer, '.')

            plt.show()

    def getNormalFallCoord(self) -> list:
        self.sunSensor.setSettings()
        normalFallList = list((self.pivotAzim.getCoord(), *self.sunSensor.getCentreCoords()))
        np.savetxt("normalFallCoord.txt", normalFallList)
        return normalFallList

    def getSensSysPolarCoord(self, filename: str) -> list:
        normalFallBuff: list = self.downloadFile("normalFallCoord.txt")
        calibBuffer: list = self.downloadFile(filename)
        rho: list = [np.sqrt(pow(calibBuffer[i][self.xSensCol] - normalFallBuff[self.xSensCol][0], 2) +
                        pow(calibBuffer[i][self.ySensCol] - normalFallBuff[self.ySensCol][0], 2))
                        for i in range(len(calibBuffer))]
        return rho

    def getSensSysAvgPolarCoord(self, filename: str, numberZenithSteps: int, numberAzimuthSteps: int, fixedAngleRepetition: int) -> list:
        sensSysPolarCoord: list = self.getSensSysPolarCoord(filename)
        calibBuffer: list = self.downloadFile(filename)
        same_angle_lines_number: int = numberZenithSteps * fixedAngleRepetition
        tempBuff: list = [sensSysPolarCoord[i * numberAzimuthSteps:(i + 1) * numberAzimuthSteps]
                          for i in range(same_angle_lines_number)]
        theta: list = [calibBuffer[i * numberAzimuthSteps][self.relativeZenithCol] for i in range(same_angle_lines_number)]
        sysAvgSensTuple: list = [(theta[i], np.average(tempBuff[i])) for i in range(same_angle_lines_number)]
        return sysAvgSensTuple



if __name__ == '__main__':
    calibrator: Calibrator = Calibrator()
    # calibrator.initialize()
    # calibrator.setDevZeroPosition()
    # calibrator.prepareBuffer(8, 4)
    # calibrator.prepareCalibration(0, 60)
    # calibrator.Calibrate(0.0, 60.0, 360.0, 120.0, 8, 4)
    # calibrator.saveToFile(calibrator.getBuffer())
    calibrator.plotPolarCoord()
    # calibrator.disable()
