#!/bin/usr/python

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

def openlaser(port=''):
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
        # check if the selected port has an IO laser by querying the ID
        whatever = s.write("NM?".encode())
        # check if the ID contains numbers at [1:4]
        try:
            reply = s.readline().decode('utf-8').strip()
            print(reply)
            int(reply[1:4])
            print('connected to:', reply[1:-1])
            break
        except:
            s.close()
            time.sleep(0.1)
            print('not a IO CW laser')
            pass

    # check if connection is open
    if not s.is_open:
        print('opening serial port failed')
        s = ''
    return s


def closelaser(s):
    """close serial connection"""
    if not s.is_open: print('no serial connection'); return
    s.close()
    if not s.is_open:
        print('connection closed')

# %% ---------------------------------------------------------------------------
# possible commands (from MB IO user manual)

commands = {
    "product_ID":       "ID?", # return product ID (6 digits)
    "product_code":     "NM?", # returns laser name (product code)
    "get_settings":     "r s", # receive settings
    "get_readings":     "r r", # receive readings
    "get_om":           "r m", # receive operating mode (APC/ACC)
    "get_info":         "r i", # receive laser information
    "get_optime":       "r t", # receive operating hours/switching times
    "get_access_level": "r l", # receive access level
    "set_access_level": "c u", # change access level (requires number and code)
    "set_crystal_temp": "c 1", # set crystal temp in centidegC (eg 2550))
    "set_diode_temp":   "c 2", # set laser diode temp in centidegC (eg 2550)
    "set_diode_current":"c 3", # set laser diode current in mA (requires current)
    "set_opt_power":    "c 4", # set optical power (requires power in mW, only if feedback diode integrated)
    "set_feedback_DAC": "c 6", # set feedback DAC value (value 0..8191)
    "set_fan_temp":     "c f", # set fan temperature in centidegC
    "set_autostart":    "c a", # enable/disable autostart after power on (1 or 0)
    "laser_output":     "e",   # start/stop laser (1/0)
    "laser_warmup":     "e 2", # enable warm-up of laser (recommended for longevity)
    "save_changes":     "f s"  # save changes
}


# %% ---------------------------------------------------------------------------
# read out settings with commands

def get_ID(s):
    """get module ID"""
    whatever = s.write(commands["product_ID"].encode())
    reply = s.readline().decode('utf-8').strip()
    print('product ID:', reply[1:-1])


def get_productcode(s):
    """get module product code"""
    whatever = s.write(commands["product_code"].encode())
    reply = s.readline().decode('utf-8').strip()
    print('product code:', reply[1:-1])


def get_settings(s, output=False):
    """receive laser settings
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_settings"].encode())
    reply = s.readline().decode('utf-8').strip()
    if output:
        print('Settings: crystal set temp, laser diode set temperature, \
laser diode set current, feedback DAC set value, optical power set value, \
laser diode current limit (mA), autostart mode, access level, fan set temp')
        print(reply)
        return
    else:
        return reply


def get_readings(s, output=False):
    """receive laser readings
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_readings"].encode())
    reply = s.readline().decode('utf-8').strip()
    if output:
        print('Readings:laser diode temperature, crystal temperature (negative if there is no crystal), \
laser base temperature, laser diode current, crystal TEC load, \
laser diode TEC load, system status, fan load, input voltage')
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
    """receive laser information
    if output=True, will spill the whole string with info, otherwise only returns it
    """
    whatever = s.write(commands["get_info"].encode())
    # output comes in five lines, combine it to one list
    reply = ''
    for i in range(5):
        reply += s.readline().decode('utf-8').strip() + '  '
    
    if output:
        print('firmware version, serial number, product code, operating time, \
the number of times the laser diode was turned on.')
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
            print('please input a 4-5 digit number as access level code')
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

def set_crystal_temp(s, settemp):
    """set crystal temp (centi-degC, eg 2550)"""
    if get_access_level(s) < 3:
        print('not enough privilege, please update access level to 3 first')
        return

    currtemp = get_crystal_temp(s)
    # check if there is actually a crystal
    if currtemp < 0:
        print('no crystal, ignoring input')
        return
    
    old_settemp = get_crystal_set_temp(s)
    if (settemp > 2500) & (settemp < 3500):
        whatever = s.write((commands["set_crystal_temp"]+ ' ' + str(settemp)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_settemp = get_crystal_set_temp(s)
    else:
        print('please give a reasonable input temperature (2500-3500) as integer')


def set_diode_temp(s, settemp):
    """set laser diode temp (centi-degC, eg 2550)"""
    if get_access_level(s) < 3:
        print('not enough privilege, please update access level to 3 first')
        return

    currtemp = get_diode_temp_num(s)
    old_settemp = get_diode_set_temp(s)
    if (settemp > 2500) & (settemp < 3500):
        whatever = s.write((commands["set_diode_temp"]+ ' ' + str(settemp)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_settemp = get_diode_set_temp(s)
    else:
        print('please give a reasonable input temperature (2500-3500) as integer')


def set_diode_current(s, setcurr):
    """set diode current (mA)"""
    if get_access_level(s) < 3:
        print('not enough privilege, please update access level to 3 first')
        return

    currcurr = get_diode_current(s)
    old_setcurr = get_diode_set_current(s)
    currlimit = get_diode_current_limit(s)
    if setcurr <= currlimit:
        whatever = s.write((commands["set_diode_current"]+ ' ' + str(setcurr)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_setcurr = get_diode_set_current(s)
    elif setcurr > currlimit:
        print('current larger than diode current limit, please set a current less than', currlimit, 'mA')
    else:
        print('please give a reasonable input current')


def set_opt_power(s, setpower):
    """set optical power (mW)"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    oldsetpower = get_opt_set_power(s)
    if oldsetpower == 'nan':
        print('sorry, optical power can not be changed on this device')
    else:
        whatever = s.write((commands["set_opt_power"] + ' ' + str(setpower)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        newsetpower = get_opt_set_power(s)
    return


def set_DAC_value(s, setvalue):
    """set feedback DAC value (0..8191)"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return
    
    old_setvalue = get_DAC_set_value(s)
    if (setvalue > 0) & (setvalue <= 8191):
        whatever = s.write((commands["set_feedback_DAC"]+ ' ' + str(setcurr)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_setvalue = get_DAC_set_value(s)
    else:
        print('please give a reasonable input value [0..8191]')


def set_fan_temp(s, settemp):
    """set fan temp (should be in centi-degC, eg 2550)"""
    if get_access_level(s) < 1:
        print('not enough privilege, please update access level to 1 first')
        return

    old_settemp = get_fan_set_temp(s)
    if (settemp > 2500) & (settemp < 3500):
        whatever = s.write((commands["set_fan_temp"]+ ' ' + str(settemp)).encode())
        reply = s.readline().decode('utf-8').strip()
        check_reply(reply)
        new_settemp = get_fan_set_temp(s)
    else:
        print('please give a reasonable input temperature (2500-3500) as integer')


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

def start_laser(s):
    """enable laser output"""
    whatever = s.write((commands["laser_output"]+' 1').encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)


def stop_laser(s):
    """disable laser output"""
    errorcode = s.write((commands["laser_output"]+' 0').encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)


def warmup_laser(s):
    """enable laser warmup (not well-documented. seems to be a setting that needs to be done once)"""
    errorcode = s.write(commands["laser_warmup"].encode())
    reply = s.readline().decode('utf-8').strip()
    check_reply(reply)

# %% ---------------------------------------------------------------------------
# get single readings

def get_diode_temp(s):
    """get diode temperature from readings"""
    diode_temp = get_readings(s).split()[1]
    print('laser diode temperature: ', diode_temp, 'degC')


def get_diode_temp_num(s):
    """get diode temperature from readings only as a number"""
    diode_temp = get_readings(s).split()[1]
    diode_temp_num = float(diode_temp)
    return diode_temp_num


def get_crystal_temp(s):
    """get laser crystal temperature from readings"""
    crystal_temp = get_readings(s).split()[2]
    if float(crystal_temp) < 0:
        print('system has no crystal')
    else:
        print('crystal temperature: ', crystal_temp, 'degC')


def get_base_temp(s):
    """get laser base temperature from readings"""
    base_temp = get_readings(s).split()[3]
    print('laser base temperature: ', base_temp, 'degC')


def get_base_temp_num(s):
    """get laser base temperature from readings only as a number"""
    base_temp = get_readings(s).split()[3]
    base_temp_num = float(base_temp)
    return base_temp_num


def get_diode_current(s):
    """get laser diode current from readings"""
    diode_current = get_readings(s).split()[4]
    print('laser diode current: ', diode_current)


def get_diode_current_num(s):
    """get laser diode current from readings only as a number"""
    diode_current = get_readings(s).split()[4]
    diode_current_num = float(diode_current.split('m')[0])
    return diode_current_num


def get_TEC_load(s):
    """get crystal/diode TEC loads from readings"""
    TEC_load_crystal = get_readings(s).split()[5]
    TEC_load_diode = get_readings(s).split()[6]
    print('crystal TEC load: ', TEC_load_crystal)
    print('  diode TEC load: ', TEC_load_diode)


def laser_status(s):
    """get laser status (OFF, WRM, APC)"""
    status = get_readings(s).split()[7]
    print('system status:', status)


def is_off(s):
    """check if laser is off"""
    status = get_readings(s).split()[7]
    if status == "OFF":
        print('laser is off')
    else:
        print('laser is not off, status:', status)


def get_fan_load(s):
    """get fan load from readings"""
    fan_load = get_readings(s).split()[8]
    print('fan load: ', fan_load)


def get_input_voltage(s):
    """get input voltage from readings"""
    input_voltage = get_readings(s).split()[9]
    print('input voltage: ', input_voltage)


# %% ---------------------------------------------------------------------------
# get single settings

def get_crystal_set_temp(s):
    """get crystal set temperature from settings"""
    crystal_set_temp = float(get_settings(s).split()[1])/100
    print('crystal set temperature: ', str(crystal_set_temp), 'degC')


def get_diode_set_temp(s):
    """get laser diode set temperature from settings"""
    diode_set_temp = float(get_settings(s).split()[2])/100
    print('laser diode set temperature: ', str(diode_set_temp), 'degC')


def get_diode_set_current(s):
    """get laser diode set current from settings"""
    diode_set_current = get_settings(s).split()[3]
    print('laser diode set current: ', diode_set_current, 'mA')


def get_DAC_set_value(s):
    """get feedback DAC set value from settings"""
    DAC_set_value = get_settings(s).split()[4]
    print('feedback DAC set value: ', DAC_set_value)


def get_opt_set_power(s):
    """get optical power set current from settings"""
    optical_set_power = get_settings(s).split()[5]
    print('set optical power: ', optical_set_power)


def get_diode_current_limit(s):
    """get laser diode current limit from settings"""
    diode_current_limit = get_settings(s).split()[6]
    print('laser diode current limit: ', diode_current_limit, 'mA')


def get_autostart_mode(s):
    """get autostart mode from settings (ON/OFF/WRM)"""
    autostart_mode = get_settings(s).split()[7]
    print('autostart mode: ', autostart_mode)


def get_fan_set_temp(s):
    """get fan set temperature from settings"""
    fan_set_temp = get_settings(s).split()[9]
    print('fan set temperature: ', str(float(fan_set_temp)/100), 'degC')

# %% ---------------------------------------------------------------------------
# get single information

def get_firmware_version(s):
    """get firmware version from information"""
    firmware_version = get_info(s).split('  ')[0]
    print(firmware_version)


def get_serial_number(s):
    """get serial number from information"""
    serial_number = get_info(s).split('  ')[1]
    print(serial_number)


def get_laser_model(s):
    """get laser model from information"""
    laser_model = get_info(s).split('  ')[2]
    print(laser_model)


def get_optime2(s):
    """get operating time from information (also has a separate serial command)"""
    optime = get_info(s).split('  ')[3]
    print('operating time: ', optime[:-1])  #remove trailing dot


def get_switch_times(s):
    """get switch times from information (could also be gotten through optime command)"""
    switch_times = get_info(s).split('  ')[4]
    print('laser diode turned on ', switch_times)

# EOF --------------------------------------------------------------------------