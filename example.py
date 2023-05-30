#!/bin/usr/python
# -----------------------------------------------------------------------------
# pip install serial pyserial
# (both of them are needed for this to work somehow)
# -----------------------------------------------------------------------------
# This code gives basic examples how to use the IOmatchbox library
# scripted by ian cynk (ian.cynk@posteo.eu) 2023
# %% --------------------------------------------------------------------------
# imports
import IOmatchbox as iom
import IOTEC as iot
import time

# %% --------------------------------------------------------------------------
# connect laser
s = iom.openlaser()

iom.get_productcode(s)

iom.get_settings(s)

iom.get_readings(s)

iom.laser_status(s)

iom.get_laser_model(s)

iom.start_laser(s)

# read diode temperature continuously
for n in range(10):
    iom.get_diode_temp(s)
    iom.get_diode_current(s)
    iom.get_base_temp_num(s)
    time.sleep(1)

# change user access level
iom.set_access_level(s, 1)

# read and change feedback DAC value
iom.get_DAC_set_value(s)
iom.set_DAC_value(s, 1000)

# read and change diode temperature
iom.get_diode_set_temp(s)
iom.set_access_level(s, 3)  # requires code from supplier
iom.set_diode_temp(s, 3205)

# turn off laser
iom.stop_laser(s)

# disconnect laser
iom.closelaser(s)

# %% --------------------------------------------------------------------------
# connect TEC
t = iot.openTEC()
iot.get_settings(t)
iot.get_readings(t)
iot.get_info(t)
iot.TEC_status(t)
iot.get_TEC_set_temp(t)

iot.enable_TEC(t)

# read temperature continuously
for n in range(10):
    iot.get_TEC_temp(t)
    iot.get_TEC_load(t)
    time.sleep(1)

# change user access level
iot.set_access_level(t, 1)

# change TEC setpoint
iot.set_TEC_temp(t, 2490)

# turn off laser
iot.disable_TEC(t)

# %% --------------------------------------------------------------------------
# disconnect laser
iot.closeTEC(t)
# EOF --------------------------------------------------------------------------