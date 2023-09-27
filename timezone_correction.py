from sys import platform
import os
import time


def adjust_timezone():
    # determine machine OS
    machine_os = None
    if platform == "linux" or platform == "linux2":
        machine_os = 'linux'
    elif platform == "darwin":
        machine_os = 'mac'
    elif platform == "win32":
        machine_os = 'win'

    # if linux and not EST, set timezone to EST (applying to python environment only)
    if machine_os == 'linux':
        if time.tzname == ('UTC', 'UTC'):
            os.environ['TZ'] = 'US/Eastern'
            time.tzset()


