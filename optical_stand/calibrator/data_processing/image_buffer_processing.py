


class Calibrator():
    "Class representing a calibrator"

    def __init__(self) -> None:
        pass

    def calibrate(self, initialAzimuthAngle: float, initialZenithAngle: float, endAzimuthAngle: float, endZenithAngle: float,
                   numberAzimuthSteps: int, numberZenithSteps: int, fixedAngleRepetition: int) -> np.ndarray:
        '''Makes a fixed number of rotations around the azimuth angle.
            Then makes a rotation around the zenith angle.
            Untangles the sensor's wire making a 360 back rotation'''
        buffer: list = []
        buffer_concat: list = []
        for i in range(numberZenithSteps + 1):
            self.move_zenith(self.__define_step_angle(numberZenithSteps, initialZenithAngle, endZenithAngle, self.TotNumZenSteps))
            for j in range(fixedAngleRepetition):
                buff: list = self.rotate_round_azimuth(numberAzimuthSteps, initialAzimuthAngle, endAzimuthAngle)
            buffer_concat.append(buff)
            buff = None
        final_buff = np.concatenate(buffer_concat[:], axis = 0)
        return np.array(final_buff)


    def untangle_wire(self) -> None:
        self.pivotAzim.absoluteRotation(0.0)