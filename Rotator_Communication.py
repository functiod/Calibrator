import time
from acspy import acsc
from acspy.acsc import ACSC_SAFETY_CPE
import SunSensor_calc as ssc
import matplotlib.pyplot as plt
import numpy as np

hcomm = acsc.openCommEthernetTCP()

#Initialize axis
def init(handle, axis):
    acsc.enable(handle, axis)
    time.sleep(1)
    acsc.commutate(handle, axis)
    acsc.waitCommutated(handle, axis)
    time.sleep(1)

def init_all(handle, axis_zero, axis_first):
    repeat = 1
    while repeat:
        flag_0, flag_1 = int(input("Zero axis to enable: ")), int(input("First axis to enable: "))
        if flag_0 == 0 and flag_1 == 1:
            init(handle, axis_zero)
            init(handle, axis_first)
            repeat = 0
        elif flag_0 == 0 and flag_1 != 1:
            init(handle, axis_zero)
            repeat = 0
        elif flag_0 != 0 and flag_1 == 1:
            init(handle, axis_first)
            repeat = 0
        else:
            repeat = int(input('Do you want to cancel initialization: 0 - Yes, 1 - No '))
    time.sleep(1)
    return repeat

def disable_all(handle, axis_zero, axis_first):
    flag_0, flag_1 = int(input("Zero axis to disable: ")), int(input("First axis to disable: "))
    if flag_0 == 0 and flag_1 == 1:
        acsc.disable(handle, axis_zero)
        acsc.disable(handle, axis_first)
        print("All Axis are disabled")
    elif flag_0 == 0 and flag_1 != 1:
        acsc.disable(handle, axis_zero)
        print("Zero Axis is disabled")
    elif flag_0 != 0 and flag_1 == 1:
        acsc.disable(handle, axis_first)
        print("First Axis is disabled")
    else:
        print("Axis are enable")

def set_zero_pos(handle, axis):
    acsc.disableResponse(handle, axis, ACSC_SAFETY_CPE)
    acsc.toPoint(handle, 0, axis, -360)
    time.sleep(0.3)
    while round(acsc.getFVelocity(handle, axis)) != 0:
        pass
    acsc.setFPosition(handle, axis, 0.00)
    acsc.acs_Break(handle, axis)
    acsc.toPoint(handle, 0, axis, 90)
    acsc.enableResponse(handle, axis, ACSC_SAFETY_CPE)

def set_velocity(handle, axis_zero, axis_first, vel_zero, vel_first):
    acsc.setVelocity(handle, axis_zero, vel_zero)
    acsc.setVelocity(handle, axis_first, vel_first)

def set_acc(handle, axis_zero, axis_first, acc_zero, acc_first):
    acsc.setAcceleration(handle, axis_zero, acc_zero)
    acsc.setAcceleration(handle, axis_first, acc_first)

#__________Defines_the_rotation_angle___________
def define_angle(handle, axis_zero, angle):
    coef = 0
    if abs(angle) >= 360 and angle >= 0:
        coef = angle // 360
        angle = angle - coef * 360
    elif abs(angle) >= 360 and angle < 0:
        coef = -angle // 360
        angle = coef * 360 + angle
    else:
        pass
    if angle < acsc.getFPosition(handle, axis_zero) and angle >= 0:
        pass
    elif angle < acsc.getFPosition(handle, axis_zero) and angle < 0:
        angle = 360 + angle
    elif angle > acsc.getFPosition(handle, axis_zero):
        pass
    return angle

#__________Rotates_to_absolute_angle_______________
def abs_rotation(handle, axis_zero, angle):
    acsc.toPoint(handle, 0, axis_zero, define_angle(handle, axis_zero, angle))
    while abs(acsc.getFPosition(handle, axis_zero) - define_angle(handle, axis_zero, angle)) >= eps:
        pass
    return acsc.getFPosition(handle, axis_zero)

#__________Horizontal_rotation_to_abs_meaning______
def abs_ax1_rotation(handle, axis_first, angle):
    acsc.toPoint(handle, 0, axis_first, angle)
    while abs(acsc.getFPosition(handle, axis_first) - define_angle(handle, axis_first, angle)) >= eps:
        if abs(acsc.getFPosition(handle, axis_first)) >= 360.:
            acsc.setFPosition(handle, axis_first, 0.0000)
            break
       
#_________Axis_1_step_by_step_motion______________
def relative_steps(handle, axis, angle_start, angle_end, angle_step):
    acsc.toPoint(handle, 0, axis, angle_start)
    temp = 0
    while temp != angle_end // angle_step:
        acsc.toPoint(handle, 0x00000002, axis, angle_step)
        time.sleep(0.3)
        temp = temp + 1
    print(acsc.getFPosition(handle, axis))

