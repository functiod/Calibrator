from enum import Enum, auto
import time
from typing import Any
from dsg.calibrator.acspy_lib import acsc
from dsg.calibrator.acspy_lib.acsc import ACSC_SAFETY_CPE


class Axis(Enum):
    zenith: int = 0
    azimuth: int = 1

class Pivot():
    "Class for work with acs library"

    MIN_COORD: float = 0.00
    MAX_COORD: float = 360.00
    EPS: float = 0.001
    additional_ip: str = '10.2.1.202'
    static_ip: str = '10.0.0.1'
    additional_ip_2: str = '127.0.0.1'
    sleep_time: float = 1.0
    default_position: float = 90.0
    com_port: Any

    def __init__(self, axis: Axis) -> None:
        self.axis: Axis = axis

    def connect_TCP(self, ip: str = additional_ip) -> None:
        self.com_port: Any | None = acsc.openCommEthernetTCP(address = ip)

    def initialize(self) -> bool:
        acsc.enable(self.com_port, self.axis.value)
        time.sleep(self.sleep_time)
        acsc.commutate(self.com_port, self.axis.value)
        acsc.waitCommutated(self.com_port, self.axis.value)
        time.sleep(self.sleep_time)
        return True

    def disable(self) -> None:
        acsc.disable(self.com_port, self.axis.value)
        acsc.closeComm(self.com_port)

    def set_zero_position(self) -> None:
        acsc.disableResponse(self.com_port, self.axis.value, ACSC_SAFETY_CPE)
        acsc.toPoint(self.com_port, 0, self.axis.value, -self.MAX_COORD)
        time.sleep(self.sleep_time)
        while round(acsc.getFVelocity(self.com_port, self.axis.value)) != 0:
            pass
        acsc.setFPosition(self.com_port, self.axis.value, self.MIN_COORD)
        acsc.acs_Break(self.com_port, self.axis.value)
        acsc.toPoint(self.com_port, 0, self.axis.value, self.default_position)
        acsc.enableResponse(self.com_port, self.axis.value, ACSC_SAFETY_CPE)

    def set_velocity(self, velocity: float) -> None:
        acsc.setVelocity(self.com_port, self.axis.value, velocity)

    def set_acceleration(self, acceleration: float) -> None:
        acsc.setAcceleration(self.com_port, self.axis.value, acceleration)

    def get_velocity(self) -> float:
        return acsc.getVelocity(self.com_port, self.axis.value)

    def __define_to_angle(self, angle: float) -> float:
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

    def absolute_rotation(self, angle: float) -> None:
        acsc.toPoint(self.com_port, 0, self.axis.value, angle)
        to_angle: float = self.__define_to_angle(angle)
        while abs(acsc.getFPosition(self.com_port, self.axis.value) - to_angle) >= self.EPS:
            if abs(acsc.getFPosition(self.com_port, self.axis.value)) >= self.MAX_COORD + self.EPS:
                acsc.setFPosition(self.com_port, self.axis.value, self.MIN_COORD)
                break

    def get_coord(self) -> float:
        return(acsc.getFPosition(self.com_port, self.axis.value))
