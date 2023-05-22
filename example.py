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
import time
import matplotlib.pyplot as plt


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

# %% --------------------------------------------------------------------------
# disconnect laser
iom.closelaser(s)

# EOF --------------------------------------------------------------------------