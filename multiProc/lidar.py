
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import time
from math import floor
from adafruit_rplidar import RPLidar         #import RPLidar class


def lidar_main(lidar_queue):
    # Setup the RPLidar
    PORT_NAME = "/dev/ttyUSB0"                   
    lidar = RPLidar(None, PORT_NAME, timeout=3)  #initializing lidar:no logger, serial port name, serial port connection timeout in seconds

    # variable used for stop distance from lidar, 3000 = ~9.5 ft.
    # we need at minimun 5.5 to 6ft of distance to avoid crash at 15mph min val = 2300
    stop_distance = 2000

    try:
        for scan in lidar.iter_scans():  #returns list of 3 measurements (tuples) in 1 rotation: quality, angle, and distance
            start_obj_angle = -1
            objs = [] #each item in the array is a tuple containing the starting angle and the ending angle for each detected object within the desired distance

            for _, angle, distance in scan:      #only want angle and distance
                ang = min(359, floor(angle))
                if ang>45 and ang<135: continue
                #print(scan_data[min([359, floor(angle)])])
                #print (min([359, floor(angle)]))

                #Save starting angle of object
                if start_obj_angle == -1 and distance < stop_distance and distance>0:
                    start_obj_angle = ang

                #Add tuple of starting and ending angle of object to array
                elif start_obj_angle != -1 and distance > stop_distance:
                    objs.append(start_obj_angle)
                    objs.append(ang-1)
                    start_obj_angle = -1

            #Check to make sure the last angle was not still in object dected mode
            if start_obj_angle !=-1:
                if len(objs)>0 and objs[0]<2:
                     objs[0] = start_obj_angle

                else:
                    objs.append(start_obj_angle)
                    objs.append(359)

            if len(objs)>0:
                lidar_queue.put(objs)

    except Exception as e:
        lidar_queue.put(e)

    finally:
        lidar_queue.put("Stopping.")

        lidar.stop()
        lidar.disconnect()
