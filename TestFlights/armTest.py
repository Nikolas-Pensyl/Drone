from dronekit import connect, VehicleMode, APIException

import time
import socket
#import exceptions
import math
import argparse


def connectMyCopter():
   baud_rate = 57600
   connection_string = '/dev/ttyACM0'
   vehicle = connect(connection_string, wait_ready=True)
   return vehicle


def arm():
   
   print("Vehicle is armable")

   vehicle.armed = True
   while vehicle.armed==False:
      print("Waiting for vehicle to be armed")
      time.sleep(1)

   print("Drone go brrrrrrrrrrrrrrrrr")
   return None


vehicle = connectMyCopter()
arm()
time.sleep(2)
