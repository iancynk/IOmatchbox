#!/bin/usr/python
# Copy of IOmatchbox for control of the IO TEC
# Has slightly different and reduced commands

# %% ---------------------------------------------------------------------------
# imports

import serial
import glob
import sys
import time


# %% ---------------------------------------------------------------------------
# communication functions

def check_reply(reply):
    """interpret reply/errorcode according to manual"""
    if reply == '<ACK>':
        print('acknowledged')
    elif reply == '<ERR 0>':
        print('0 - error name not assigned yet')
    elif reply == '<ERR 1>':
        print('1 - command forbidden for current access level')
    elif reply == '<ERR 2>':
        print('2 - laser already on or making ramp-up')
    elif reply == '<ERR 3>':
        print('3 - laser busy, task is not complete please wait for 1 s and try again')
    elif reply == '<ERR 4>':
        print('4 - arguments out of range')
    elif reply == '<ERR 5>':
        print('5 - unknown command')
    elif reply == '<ERR 6>':
        print('6 - laser must be enabled to execute this command')
    else:
        print('unknown reply:', reply)
    return


# %% ---------------------------------------------------------------------------
# serial functions

def openTEC(port=''):
    """create a serial connection with the recommended parameters
    if no port is given the function will try all available serial ports
    and check whether the connected device has an ID like an IO laser. 
    """
    s = serial.Serial()
    s.baudrate = 115200
    s.bytesize = serial.EIGHTBITS
    s.parity = serial.PARITY_NONE
    s.stopbits = serial.STOPBITS_ONE
    s.timeout = 5
    # s.rtscts = True # enable hardware (TRS/CTS) flow control
    if not port:
        # find available ports depending on operating system
        if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            available_ports = glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('win'):
            available_ports = ['COM%s' % (i + 1) for i in range(256)]
        else:
            raise EnvironmentError('Unsupported platform')
    else:
        available_ports = [port]

    # try to open the ports until one works
    for port in available_ports:
        try:
            print('opening port', port)
            s.port = port
            s.open()
            time.sleep(0.1)
        except:
            print('failed at port', port)
            continue
        # check if the selected port has an IO TEC by querying info
        whatever = s.write("r i".encode())

        # check if the info contains "ExternalTEC"
        try:
            # output comes in five lines, combine it to one string
            reply = ''
            for i in range(5):
                reply += s.readline().decode('utf-8', 'ignore').strip() + '  '
            if reply[0:11] == "ExternalTEC":
                print('connected to', reply[0:11])
            break
        except:
            s.close()
            time.sleep(0.1)
            print('not a IO TEC')
            pass

    # check if connection is open
    if not s.is_open:
        print('opening serial port failed')
        s = ''
    return s


def closeTEC(s):
    """close serial connection"""
    if not s.is_open: print('no serial connection'); return
    s.close()
    if not s.is_open:
        print('connection closed')

# %% ---------------------------------------------------------------------------
# possible commands (from MB IO user manual)

commands = {
    "get_settings":     "r s", # receive settings
    "get_readings":     "r r", # receive readings
    "get_om":           "r m", # receive operating mode (APC/ACC)
    "get_info":         "r i", # receive TEC information
    "get_optime":       "r t", # receive operating hours/switching times
    "get_access_level": "r l", # receive access level
    "set_access_level": "c u", # change access level (requires number and code)
    "set_TEC_temp":     "c f", # set fan temperature in centidegC
    "enable_autostart": "c a", # enable/disable autostart after power on (1 or 0)
    "enable_TEC":       "e",   # enable/disable TEC (1/0)
    "save_changes":     "f s"  # save changes
}


# %% ---------------------------------------------------------------------------
# read out settings with commands

def get_settings(s, output=False):
    """receive TEC settings
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_settings"].encode())
    reply = s.readline().decode('utf-8').strip()
    if output:
        print('Settings: min temp?, max temp?, 0, 255, nan, \
            64000, autostart mode, access level, set temp')
        print(reply)
        return
    else:
        return reply


def get_readings(s, output=False):
    """receive TEC readings
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_readings"].encode())
    reply = s.readline().decode('utf-8').strip()
    if output:
        print('Readings: some temperature, some temperature, TEC temperature, current, \
            some load, some load, system status, some load, input voltage')
        print(reply)
        return
    else:
        return reply


def get_om(s):
    """receive operation mode (APC/ACC)"""
    whatever = s.write(commands["get_om"].encode())
    reply = s.readline().decode('utf-8').strip()
    print('operation mode:', reply)


def get_info(s, output=False):
    """receive TEC information
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_info"].encode())
    # output comes in five lines, combine it to one list
    reply = ''
    for i in range(5):
        reply += s.readline().decode('utf-8', 'ignore').strip() + '  '
    
    if output:
        print('Driver Version, serial number, product code, operating time, switch times')
        print(reply)
        return
    else:
        return reply


def get_optime(s, output=False):
    """receive laser operation time
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_optime"].encode())
    # output comes in two lines, combine it to one list
    reply1 = s.readline().decode('utf-8').strip()[:-1]  # remove trailing dot
    reply2 = s.readline().decode('utf-8').strip()
    reply = reply1 + ', ' + reply2
    if output:
        print('operating hours and how many times the laser diode has been turned on')
        print(reply)
        return
    else:
        return reply


def get_access_level(s):
    """receive access level"""
    whatever = s.write(commands["get_access_level"].encode())
    reply = s.readline().decode('utf-8').strip()
    access_level = int(reply.split()[2])
    return access_level


def set_access_level(s, level):
    """change user access level (default level over serial is 0)
    requires setting the correct codes that need to be obtained from the supplier (level 2-3)
    """
    if level == 0:
        print('cannot return to access level 0')
        return
    elif level == 1:
        input_code = '1234'  # code supplied in user manual
    elif (level == 2) or (level == 3):
        input_code = input('please input access level code for level ' + str(level) + '\n')
        # check if code is numerical
        try:
            code = int(input_code)
        except ValueError:
            print('please input a 5 digit number as access level code')
            return
    else:
        print('invalid access level, please choose a number in [0..3]')
        return

    command = commands["set_access_level"]+' ' + str(level) + ' ' + input_code
    whatever = s.write(command.encode())
    reply = s.readline().decode('utf-8').strip()
    # check if access level code worked
    if reply == '<ERR 4>':
        print('invalid code to unlock access level', str(level), ': ', input_code)
    else:
        check_reply(reply)
    print('Access level:', str(get_access_level(s)))
# %% ---------------------------------------------------------------------------
# modify settings

def set_TEC_temp(s, settemp):
    """set TEC temp (should be in centi-degC, eg 2550)"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    old_settemp = get_TEC_set_temp(s)
    if (settemp > 2000) & (settemp < 3000):
        whatever = s.write((commands["set_TEC_temp"]+ ' ' + str(settemp)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_settemp = get_TEC_set_temp(s)
    else:
        print('please give a reasonable input temperature (2000-3000) as integer')


def enable_autostart(s):
    """enable autostart on power-on"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    # errorcode = s.write((commands["enable_autostart"] + ' 1').encode())
    # reply = s.readline().decode('utf-8').strip()
    # check_reply(reply)
    print("Do not use Autostart! It will just heat your base plate without any regulation.")
    print("You're welcome. Glad I could save your laser.")


def disable_autostart(s):
    """disable autostart on power-on"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    errorcode = s.write((commands["enable_autostart"] + ' 0').encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)


def save_changes(s):
    """save changes"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    errorcode = s.write(commands["save_changes"].encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)

# %% ---------------------------------------------------------------------------
# get enable/disable output

def enable_TEC(s):
    """enable TEC"""
    whatever = s.write((commands["enable_TEC"]+' 1').encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)


def disable_TEC(s):
    """disable TEC"""
    errorcode = s.write((commands["enable_TEC"]+' 0').encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)


# %% ---------------------------------------------------------------------------
# get single readings

def get_TEC_temp(s):
    """get TEC temperature from readings"""
    TEC_temp = get_readings(s).split()[3]
    print('TEC temperature: ', TEC_temp, 'degC')


def get_TEC_temp_num(s):
    """get TEC temperature from readings only as a number"""
    TEC_temp = get_readings(s).split()[3]
    TEC_temp_num = float(TEC_temp)
    return TEC_temp_num


def TEC_status(s):
    """get TEC status (OFF, WRM, APC)"""
    status = get_readings(s).split()[7]
    print('system status:', status)


def is_off(s):
    """check if TEC is off"""
    status = get_readings(s).split()[7]
    if status == "OFF":
        print('TEC is off')
    else:
        print('TEC is not off, status:', status)


def get_TEC_load(s):
    """get TEC load from readings"""
    TEC_load = get_readings(s).split()[8]
    print('TEC load: ', TEC_load)


def get_input_voltage(s):
    """get input voltage from readings"""
    input_voltage = get_readings(s).split()[9]
    print('input voltage: ', input_voltage)


# %% ---------------------------------------------------------------------------
# get single settings

def get_autostart_mode(s):
    """get autostart mode from settings (ON/OFF/WRM)"""
    autostart_mode = get_settings(s).split()[7]
    print('autostart mode: ', autostart_mode)


def get_TEC_set_temp(s):
    """get TEC set temperature from settings"""
    TEC_set_temp = get_settings(s).split()[9]
    print('TEC set temperature: ', str(float(TEC_set_temp)/100), 'degC')

# %% ---------------------------------------------------------------------------
# get single information

def get_driver_version(s):
    """get driver version from information"""
    driver_version = get_info(s).split('  ')[0]
    print(driver_version)


def get_optime2(s):
    """get operating time from information (also has a separate serial command)"""
    optime = get_info(s).split('  ')[3]
    print('operating time: ', optime[:-1])  #remove trailing dot


def get_switch_times(s):
    """get switch times from information (could also be gotten through optime command)"""
    switch_times = get_info(s).split('  ')[4]
    print('laser diode turned on ', switch_times)

# %% ---------------------------------------------------------------------------
# send command

def send_command(s, command):
    """send an arbitrary command"""
    whatever = s.write(command.encode())
    reply = s.readline().decode('utf-8').strip()
    print(reply)

# EOF --------------------------------------------------------------------------