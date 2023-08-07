"""IOmatchbox - Python wrapper to control IO matchbox lasers and TECs"""

import pkg_resources

from .IOmatchbox import IOM
from .IOTEC import IOT

__version__ = pkg_resources.require("IOmatchbox")[0].version
__author__ = "iancynk <ian.cynk@posteo.eu>"
__all__ = ['IOM', 'IOT']