# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
from math import floor
from adafruit_rplidar import RPLidar         #import RPLidar class

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"                   
lidar = RPLidar(None, PORT_NAME, timeout=3)  #initializing lidar:no logger, serial port name, serial port connection timeout in seconds
stop_value = 3000        # variable used for stop distance from lidar, 3000 = ~9.5 ft.
                         # we need at minimun 5.5 to 6ft of distance to avoid crash at 15mph min val = 2300
wall = 0


def process_data(data):                      #outputs distance values of 360 points
    print(data)


scan_data = [0] * 360                        #makes an array with 360 elements
print(lidar.info)
try:
    
    for scan in lidar.iter_scans():  #returns list of 3 measurements (tuples) in 1 rotation: quality, angle, and distance
        print(scan)
        print("-------------------------------------------------------------")

except Exception as e:
    print("Stopping.", e)
lidar.stop()
lidar.disconnect()
