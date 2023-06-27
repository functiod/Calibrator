from enum import Enum
import time
from acspy import acsc
from acspy.acsc import ACSC_SAFETY_CPE

class Axis(Enum):
    zenith: int = 0
    azimuth: int = 1

class Pivot:
    MIN_COORD: float = 0.00
    MAX_COORD: float = 360.00
    EPS: float = 0.001
    podval_ip: str = '10.2.1.202'
    static_ip: str = '10.0.0.100'

    def __init__(self, axis: Axis, ip: str = podval_ip) -> None:
        '''installs the connection with a controller via EthernetTCP'''
        self.ip: str = ip
        self.com_port = acsc.openCommEthernetTCP(address = ip)
        self.axis: Axis = axis

    def initialize(self) -> None:
        '''Commutates Axes with the controller'''
        acsc.enable(self.com_port, self.axis.value)
        time.sleep(1)
        acsc.commutate(self.com_port, self.axis.value)
        acsc.waitCommutated(self.com_port, self.axis.value)
        time.sleep(1)

    def disable(self) -> None:
        '''Decommutates Axes'''
        acsc.disable(self.com_port, self.axis.value)
        acsc.closeComm(self.com_port)

    def setZeroPosition(self, initialPos: float) -> None:
        '''Sets digital zero position in view of physical one. Then goes to a fixed position'''
        acsc.disableResponse(self.com_port, self.axis.value, ACSC_SAFETY_CPE)
        acsc.toPoint(self.com_port, 0, self.axis.value, -self.MAX_COORD)
        time.sleep(0.3)
        while round(acsc.getFVelocity(self.com_port, self.axis.value)) != 0:
            pass
        acsc.setFPosition(self.com_port, self.axis.value, self.MIN_COORD)
        acsc.acs_Break(self.com_port, self.axis.value)
        acsc.toPoint(self.com_port, 0, self.axis.value, initialPos)
        acsc.enableResponse(self.com_port, self.axis.value, ACSC_SAFETY_CPE)

    def setVel(self, velocity: float) -> None:
        acsc.setVelocity(self.com_port, self.axis.value, velocity)

    def setAcc(self, acceleration: float) -> None:
        acsc.setAcceleration(self.com_port, self.axis.value, acceleration)

    def __defineToAngle(self, angle: float) -> float:
        '''Converts physical angle to digital in the range of 0 to 360. Returns the digital angle'''
        coef: int = 0
        if abs(angle) >= self.MAX_COORD and angle >= self.MIN_COORD:
            coef = angle // int(self.MAX_COORD)
            angle: float = angle - coef * self.MAX_COORD
        elif abs(angle) >= self.MAX_COORD and angle < self.MIN_COORD:
            coef = -angle // self.MAX_COORD
            angle = coef * self.MAX_COORD + angle
        else:
            pass
        if angle < acsc.getFPosition(self.com_port, self.axis.value) and angle >= self.MIN_COORD:
            pass
        elif angle < acsc.getFPosition(self.com_port, self.axis.value) and angle < self.MIN_COORD:
            angle = self.MAX_COORD + angle
        elif angle > acsc.getFPosition(self.com_port, self.axis.value):
            pass
        return angle

    def absoluteRotation(self, angle: float) -> None:
        '''Rotates on a digital angle.
        Angle == 540 ---> Angle == 540 - 360 = 180
        Angle == -180 ---> Angle == 360 - 180 = 180'''
        acsc.toPoint(self.com_port, 0, self.axis.value, angle)
        while abs(acsc.getFPosition(self.com_port, self.axis.value) - self.__defineToAngle(angle)) >= self.EPS:
            if abs(acsc.getFPosition(self.com_port, self.axis.value)) >= self.MAX_COORD + self.EPS:
                acsc.setFPosition(self.com_port, self.axis.value, self.MIN_COORD)
                break

    def getCoord(self) -> float:
        return(acsc.getFPosition(self.com_port, self.axis.value))
