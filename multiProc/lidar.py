# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#import time
from math import floor
from adafruit_rplidar import RPLidar         #import RPLidar class

# Setup the RPLidar
PORT_NAME = "/dev/ttyUSB0"                   
lidar = RPLidar(None, PORT_NAME, timeout=3)  #initializing lidar:no logger, serial port name, serial port connection timeout in seconds

def lidar_main(lidar_queue):
    scan_data = [0] * 360                        #makes an array with 360 elements

    try:
        for scan in lidar.iter_scans():          #returns list of 3 measurements (tuples) in 1 rotation: quality, angle, and distance 
            for _, angle, distance in scan:      #only want angle and distance
                scan_data[min([359, floor(angle)])] = distance       #inserting distance in scan_data array
            #process_data(scan_data)             #reads distance values of 360 points
            move = ''
            if scan_data[0] < 690:
                move += 'obj in front: Backup'
            if scan_data[90] < 690:
                move += 'obj in right: Left'
            if scan_data[180] < 690:
                move += 'obj in back: Forward'
            if scan_data[270] < 690:
                move += 'obj in left: Right'
            lidar_queue.put(move)

    except KeyboardInterrupt:
        print("Stopping.")
        lidar.stop()
        lidar.disconnect()


def process_data(data, lidar_queue):                      #outputs distance values of 360 points
    print(data)
    



        


