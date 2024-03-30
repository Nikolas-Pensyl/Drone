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

try:
    
    for scan in lidar.iter_scans():  #returns list of 3 measurements (tuples) in 1 rotation: quality, angle, and distance
        room = [0] * 360
        for _, angle, distance in scan:      #only want angle and distance
            scan_data[min([359, floor(angle)])] = distance     #inserting distance in scan_data array
        
            #print(scan_data[min([359, floor(angle)])])
            #print (min([359, floor(angle)]))
            if wall == 1:
                if distance >2000:
                    room[min([359, floor(angle)])] = min([359, floor(angle)])
                    wall = 0
                else:
                    room[min([359, floor(angle)])] = -1
            else:
                if distance < 2000 and distance > 0:
                    room[min([359, floor(angle)])] = min([359, floor(angle)])
                    wall = 1
                
                    
        print(room)
        #process_data(scan_data)             #reads distance values of 360 points
        '''if scan_data[0] < 690:
            print('obj in front: Backup')
        if scan_data[90] < 690:
            print('obj in right: Left')
        if scan_data[180] < 690:
            print('obj in back: Forward')
        if scan_data[270] < 690:
            print('obj in left: Right')'''
        #print(scan_data[359])
        #print(scan_data[0])
        #print(scan_data[1])
        #process_data(scan_data)
    
        print("-------------------------------------------------------------")

except KeyboardInterrupt:
    print("Stopping.")
lidar.stop()
lidar.disconnect()
