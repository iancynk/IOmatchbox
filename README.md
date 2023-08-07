# IOmatchbox
Functions and examples to control Integrated Optics CW lasers and standalone TECs through serial commands with Python.

The official software can be found on the [Supplier Download Site](https://integratedoptics.com/downloads)

Documentation is also available through the same website. The serial commands have been taken from the User Manual (*MB_IO_2.5_Continuous_Wave_Laser_Users_Manual.pdf*).

There is no official documentation for the Stand-alone Air Cooled Heatsink with TEC (AM-H09/10/11). Thus I just used the commands of the laser as far as they worked.

## Requirements
Needs `serial` and `pyserial` (both of them are needed for this to work somehow), best installed through:
```
pip install serial pyserial
```

## Usage
Simply run
```
pip install IOmatchbox
```
Then in your Python script invoke the functions by
```
from IOmatchbox import IOM, IOT
iom = IOM()
iot = IOT()
```
With `iom` you can then call all functions and methods of the laser, with `iot` you can communicate with the external TEC.

Get some more info with
```
iom.get_settings()
iom.get_readings()
iom.laser_status()
```

Fire up the laser with
```
iom.start_laser()
```

Stop the laser with
```
iom.stop_laser()
```

Disconnect with
```
iom.closelaser()
```

To see all functions, simply use
```
help(iom)
```

More examples in [example.py](example.py). Includes also commands to communicate with the TEC though they are still not complete.

**Warning:** Do NOT enable autostart of the TEC. It will just start heating at maximum power no matter what is the setpoint. This is a serious bug and will kill your laser. 


## Access Codes
Most setting changes require a change of access level which can be done with
```
iom.set_access_level(3)
```
However, you need a 5-digit access code for level 2 and 3 that you need to request from the supplier. Level 1 can be accessed by default.

## Serial ports
By default the `openlaser()`-function will use all the ports found under `/dev/ttyUSB*` (Windows: COM[0-255]), try to connect through serial and check the productcode. If the first three digits of the product are a number it will assume that it found a CW laser and stay with that connection. This is to distinguish the port from a port that is potentially connected to a TEC. You can also manually put a port in the `openlaser`-function.

You need write-access to the tty-port. Either run as the admin or change the permissions or the ownership on the serial port, preferably with a udev rule, e.g. something like
`/etc/udev/rules.d/80-usb-serial.rules`
```
SUBSYSTEM=="tty", MODE="0666"
```
(After changing run as root: `udevadm control --reload-rules && udevadm trigger`)

## Status
This is under development but I hope it will be helpful for fellow users. Comments and suggestions highly welcome.

## License
This project is licensed under the MIT license.

