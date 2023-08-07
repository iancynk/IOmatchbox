#!/bin/usr/python
# -----------------------------------------------------------------------------
# pip install serial pyserial
# (both of them are needed for this to work somehow)
# -----------------------------------------------------------------------------
# This code gives basic examples how to use the IOmatchbox library
# scripted by ian cynk (ian.cynk@posteo.eu) 2023
# %% --------------------------------------------------------------------------
# imports
import time
from IOmatchbox import IOM, IOT

# %% --------------------------------------------------------------------------
# connect laser
iom = IOM()
iom = IOM(port='/dev/ttyUSB0')  # connect laser with specified port

iom.get_productcode()

iom.get_settings()

iom.get_readings()

iom.laser_status()

iom.get_laser_model()

iom.start_laser()

# read diode temperature continuously
for n in range(10):
    iom.get_diode_temp()
    iom.get_diode_current()
    iom.get_base_temp_num()
    time.sleep(1)

# change user access level
iom.set_access_level(1)

# read and change feedback DAC value
iom.get_DAC_set_value()
iom.set_DAC_value(1000)

# read and change diode temperature
iom.get_diode_set_temp()
iom.set_access_level(3)  # requires code from supplier
iom.set_diode_temp(3205)

# turn off laser
iom.stop_laser()

# disconnect laser
iom.closelaser()

# %% --------------------------------------------------------------------------
# connect TEC
iot = IOT()
iot = IOT(port='/dev/ttyUSB1')  # connect TEC with specified port

# get settings and status
iot.get_settings()
iot.get_readings()
iot.get_info()
iot.TEC_status()
iot.get_TEC_set_temp()

iot.enable_TEC()

# read temperature continuously
for n in range(10):
    iot.get_TEC_temp()
    iot.get_TEC_load()
    time.sleep(1)

# change user access level
iot.set_access_level(1)

# change TEC setpoint
iot.set_TEC_temp(2490)

# disable TEC
iot.disable_TEC()

# disconnect TEC
iot.closeTEC()
# EOF --------------------------------------------------------------------------