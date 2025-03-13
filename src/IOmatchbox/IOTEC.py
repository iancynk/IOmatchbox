#!/bin/usr/python
# Python wrapper to communicate with Integrated Optics TEC
# Copy of IOmatchbox with slightly different and reduced commands
# %% ---------------------------------------------------------------------------
# imports

import serial
import glob
import sys
import time


# %% ---------------------------------------------------------------------------
# IOT class
class IOT():
    # set this to True when you need a more output
    # not really implemented
    DEBUG = False
    
    def __init__ (self, port='', DEBUG=False) :
        self.ser = None
        # open serial connection
        if port:
            # with port if port is given
            self.openTEC(port=port)
        else:
            # otherwise just pick the first found port
            self.openTEC()
        # more output info
        if DEBUG: self.DEBUG = True
    
    
    def __str__(self):
        return "Is a serial instance of a IO TEC."
        self.get_info()
    # --------------------------------------------------------------------------
    # communication functions
    
    def check_reply(self, reply):
        """interpret reply/errorcode according to manual"""
        match reply:
            case '<ACK>':
                print('acknowledged')
            case '<ERR 0>':
                print('0 - error name not assigned yet')
            case '<ERR 1>':
                print('1 - command forbidden for current access level')
            case '<ERR 2>':
                print('2 - laser already on or making ramp-up')
            case '<ERR 3>':
                print('3 - laser busy, task is not complete please wait for 1 s and try again')
            case '<ERR 4>':
                print('4 - arguments out of range')
            case '<ERR 5>':
                print('5 - unknown command')
            case '<ERR 6>':
                print('6 - laser must be enabled to execute this command')
            case _:
                print('unknown reply:', reply)
    
    
    # --------------------------------------------------------------------------
    # serial functions
    
    def openTEC(self, port=''):
        """create a serial connection with the recommended parameters
        if no port is given the function will try all available serial ports
        and check whether the connected device has an ID like an IO laser. 
        """
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.timeout = 2
        # self.ser.rtscts = True # enable hardware (TRS/CTS) flow control
        if not port:
            # find available ports depending on operating system
            if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                # look for the id of the UART controller
                available_ports = glob.glob('/dev/serial/by-id/*CP2102N*')
                if available_ports == '':
                    # look for all USB ports
                    available_ports = glob.glob('/dev/ttyUSB*')
            elif sys.platform.startswith('win'):
                available_ports = ['COM%s' % (i + 1) for i in range(256)]
            else:
                raise EnvironmentError('Unsupported platform')
        else:
            available_ports = [port]
        
        if not available_ports:
            print('no serial port selected, aborting')
            self.ser = None
            return
        
        # try to open the ports until one works
        for port in available_ports:
            try:
                print('opening port', port)
                self.ser.port = port
                self.ser.open()
                time.sleep(0.1)
            except:
                print('failed at port', port)
                continue
            # check if the selected port has an IO TEC by querying info
            _ = self.ser.write("r i".encode())

            # check if the info contains "ExternalTEC"
            try:
                # output comes in five lines, combine it to one string
                reply = ''
                self.ser.timeout = 0.5  # reduce timeout to not block channel too long
                for i in range(5):
                    reply += self.ser.readline().decode('utf-8', 'ignore').strip() + '  '
                if reply[0:11] == "ExternalTEC":
                    print('connected to', reply[0:11])
                    self.ser.timeout = 2
                else:
                    self.ser.close()
            except:
                self.ser.close()
                time.sleep(0.1)
                print('not a IO TEC')
                pass
        
        if self.DEBUG:
            if self.ser.is_open:
                print('port', self.ser.port, 'opened')
        return
    
    
    def port_is_open(self):
        """check whether serial port is open
        returns false if port is closed or not a serial port
        """
        try: 
            if not self.ser.is_open:
                print('serial port not open')
                return False
        except AttributeError:
            print('no serial stage connected, ignoring command')
            return False
        return True
    
    
    def closeTEC(self):
        """close serial connection"""
        if not self.port_is_open(): return
        self.ser.close()
        if not self.ser.is_open:
            print('connection closed')
    
    # --------------------------------------------------------------------------
    # possible commands (from MB IO user manual)
    
    cmds = {
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
    
    
    # --------------------------------------------------------------------------
    # read out settings with commands
    
    def get_settings(self, output=False):
        """receive TEC settings
        if output=True, will spill the whole string with info, otherwise only returns it
        """
        _ = self.ser.write(self.cmds["get_settings"].encode())
        reply = self.ser.readline().decode('utf-8').strip()
        if output:
            print('Settings: min temp?, max temp?, 0, 255, nan, \
                64000, autostart mode, access level, set temp')
            print(reply)
            return
        else:
            return reply
    
    
    def get_readings(self, output=False):
        """receive TEC readings
        if output=True, will spill the whole string with info, otherwise only returns it
        """
        _ = self.ser.write(self.cmds["get_readings"].encode())
        reply = self.ser.readline().decode('utf-8').strip()
        if output:
            print('Readings: some temperature, some temperature, TEC temperature, current, \
                some load, some load, system status, some load, input voltage')
            print(reply)
            return
        else:
            return reply
    
    
    def get_om(self):
        """receive operation mode (APC/ACC)"""
        _ = self.ser.write(self.cmds["get_om"].encode())
        reply = self.ser.readline().decode('utf-8').strip()
        print('operation mode:', reply)
    
    
    def get_info(self, output=False):
        """receive TEC information
        if output=True, will spill the whole string with info, otherwise only returns it
        """
        _ = self.ser.write(self.cmds["get_info"].encode())
        # output comes in five lines, combine it to one list
        reply = ''
        for i in range(5):
            reply += self.ser.readline().decode('utf-8', 'ignore').strip() + '  '
        
        if output:
            print('Driver Version, serial number, product code, operating time, switch times')
            print(reply)
            return
        else:
            return reply
    
    
    def get_optime(self, output=False):
        """receive laser operation time
        if output=True, will spill the whole string with info, otherwise only returns it
        """
        _ = self.ser.write(self.cmds["get_optime"].encode())
        # output comes in two lines, combine it to one list
        reply1 = self.ser.readline().decode('utf-8').strip()[:-1]  # remove trailing dot
        reply2 = self.ser.readline().decode('utf-8').strip()
        reply = reply1 + ', ' + reply2
        if output:
            print('operating hours and how many times the laser diode has been turned on')
            print(reply)
            return
        else:
            return reply
    
    
    def get_access_level(self):
        """receive access level"""
        _ = self.ser.write(self.cmds["get_access_level"].encode())
        reply = self.ser.readline().decode('utf-8').strip()
        access_level = int(reply.split()[2])
        return access_level
    
    
    def set_access_level(self, level):
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
        
        cmd = self.cmds["set_access_level"]+' ' + str(level) + ' ' + input_code
        _ = self.ser.write(cmd.encode())
        reply = self.ser.readline().decode('utf-8').strip()
        # check if access level code worked
        if reply == '<ERR 4>':
            print('invalid code to unlock access level', str(level), ': ', input_code)
        else:
            self.check_reply(reply)
        print('Access level:', str(self.get_access_level()))
    # --------------------------------------------------------------------------
    # modify settings
    
    def set_TEC_temp(self, settemp):
        """set TEC temp (should be in centi-degC, eg 2550)"""
        if self.get_access_level() < 1:
            print('not enough privilege, please update access level to 1 first')
            return
        
        old_settemp = self.get_TEC_set_temp()
        if (settemp > 2000) & (settemp < 3000):
            _ = self.ser.write((self.cmds["set_TEC_temp"]+ ' ' + str(settemp)).encode())
            reply = self.ser.readline().decode('utf-8').strip()
            self.check_reply(reply)
            new_settemp = self.get_TEC_set_temp()
        else:
            print('please give a reasonable input temperature (2000-3000) as integer')
    
    
    def enable_autostart(self):
        """enable autostart on power-on"""
        if self.get_access_level() < 1:
            print('not enough privilege, please update access level to 1 first')
            return
        
        # errorcode = self.ser.write((self.cmds["enable_autostart"] + ' 1').encode())
        # reply = self.ser.readline().decode('utf-8').strip()
        # self.check_reply(reply)
        print("Do not use Autostart! It will just heat your base plate without any regulation.")
        print("You're welcome. Glad I could save your laser.")
    
    
    def disable_autostart(self):
        """disable autostart on power-on"""
        if self.get_access_level() < 1:
            print('not enough privilege, please update access level to 1 first')
            return
        
        errorcode = self.ser.write((self.cmds["enable_autostart"] + ' 0').encode())
        reply = self.ser.readline().decode('utf-8').strip()
        self.check_reply(reply)
    
    
    def save_changes(self):
        """save changes"""
        if self.get_access_level() < 1:
            print('not enough privilege, please update access level to 1 first')
            return
        
        errorcode = self.ser.write(self.cmds["save_changes"].encode())
        reply = self.ser.readline().decode('utf-8').strip()
        self.check_reply(reply)
    
    
    # --------------------------------------------------------------------------
    # get enable/disable output
    
    def enable_TEC(self):
        """enable TEC"""
        _ = self.ser.write((self.cmds["enable_TEC"]+' 1').encode())
        reply = self.ser.readline().decode('utf-8').strip()
        self.check_reply(reply)
    
    
    def disable_TEC(self):
        """disable TEC"""
        errorcode = self.ser.write((self.cmds["enable_TEC"]+' 0').encode())
        reply = self.ser.readline().decode('utf-8').strip()
        self.check_reply(reply)
    
    
    # --------------------------------------------------------------------------
    # get single readings
    
    def get_TEC_temp(self):
        """get TEC temperature from readings"""
        TEC_temp = self.get_readings().split()[3]
        print('TEC temperature: ', TEC_temp, 'degC')
    
    
    def get_TEC_temp_num(self):
        """get TEC temperature from readings only as a number"""
        TEC_temp = self.get_readings().split()[3]
        TEC_temp_num = float(TEC_temp)
        return TEC_temp_num
    
    
    def TEC_status(self):
        """get TEC status (OFF, WRM, APC)"""
        status = self.get_readings().split()[7]
        print('system status:', status)
    
    
    def is_off(self):
        """check if TEC is off"""
        status = self.get_readings().split()[7]
        if status == "OFF":
            print('TEC is off')
        else:
            print('TEC is not off, status:', status)
    
    
    def get_TEC_load(self):
        """get TEC load from readings"""
        TEC_load = self.get_readings().split()[8]
        print('TEC load: ', TEC_load)
    
    
    def get_input_voltage(self):
        """get input voltage from readings"""
        input_voltage = self.get_readings().split()[9]
        print('input voltage: ', input_voltage)
    
    
    # --------------------------------------------------------------------------
    # get single settings
    
    def get_autostart_mode(self):
        """get autostart mode from settings (ON/OFF/WRM)"""
        autostart_mode = self.get_settings().split()[7]
        print('autostart mode: ', autostart_mode)
    
    
    def get_TEC_set_temp(self):
        """get TEC set temperature from settings"""
        TEC_set_temp = self.get_settings().split()[9]
        print('TEC set temperature: ', str(float(TEC_set_temp)/100), 'degC')
    
    # --------------------------------------------------------------------------
    # get single information
    
    def get_driver_version(self):
        """get driver version from information"""
        driver_version = self.get_info().split('  ')[0]
        print(driver_version)
    
    
    def get_optime2(self):
        """get operating time from information (also has a separate serial command)"""
        optime = self.get_info().split('  ')[3]
        print('operating time: ', optime[:-1])  # remove trailing dot
    
    
    def get_switch_times(self):
        """get switch times from information (could also be gotten through optime command)"""
        switch_times = self.get_info().split('  ')[4]
        print('laser diode turned on ', switch_times)
    
    # --------------------------------------------------------------------------
    # send command
    
    def send_cmd(self, cmd):
        """send an arbitrary cmd"""
        _ = self.ser.write(cmd.encode())
        reply = self.ser.readline().decode('utf-8').strip()
        print(reply)

# EOF --------------------------------------------------------------------------