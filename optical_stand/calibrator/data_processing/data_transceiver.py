class DataTransceiver():
    "Class for data transmission and reception"
    def __init__(self) -> None:
        pass

    def prepareBuffer(self, numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> None:
        '''Fills the object's buffer with zeros as two dimensional matrix with certain sizes'''
        self.imageBuffer = np.zeros(((numberAzimuthSteps) * (numberZenithSteps + 1) * fixedAngleRepetition,
                                    self.measurColNum + 1))

    def getBuffer(self) -> list:
        return self.imageBuffer

    def __prepareBufferString(self) -> list:
        '''Returns tuple(Azimuth_angle, x_sensity, y_sensity, zenith_sensity, azimuth_sensity, Zenith_angle)'''
        coords: list = self.sunSensor.getCentreCoords()
        data: list = [coords[self.xSensCol], coords[self.xSensCol], coords[self.zenSensCol],
                       coords[self.azimSensCol], self.pivotZenith.getCoord(), self.pivotAzim.getCoord(),
                       np.sqrt(pow(coords[self.xSensCol], 2) + pow(coords[self.ySensCol], 2))]
        print(data)
        return self.convertDataFormCSV(data)
