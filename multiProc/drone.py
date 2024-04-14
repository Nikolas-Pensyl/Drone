import asyncio
import websockets
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import json

def start_drone(lidar_queue, server_queue, camera_queue, output_queue):
    #Check which USB with ls /dev/tty*
    #ttyACM1 = USB
    #ttyACM0 = USB
    #ttyS0   = PINS

    connection_string = '/dev/ttyACM0'
    baud_rate = 57600

    # Connect to the Vehicle
    #print('Connecting to vehicle on: %s' % connection_string)
    
    output_queue.put('Connecting to vehicle on: ' + connection_string)
    drone = connect(connection_string, baud_rate)
    
    
    MAX_ANGLE = 5
    MAX_LOST_TIME =5
    
    thrust = 0
    yaw = 0
    pitch = 0
    roll = 0
    auto_land = False
    lock_on_target = False
    arm_drone = False
    armed = False
    lost_target_time = 0

    ##################################################
    #################### main loop ###################
    ##################################################
    try:
        while True:
            ##########################################################
            ################## Get Data From Client ##################
            ##########################################################
            if not server_queue.empty():
                new_message = json.loads(server_queue.get())
                
                thrust = new_message['thrust']
                yaw = new_message['yaw']
                pitch = new_message['pitch']
                roll = new_message['roll']
                lock_on_target = bool(new_message['lockTarg'])
                arm_drone = bool(new_message['arm_drone'])


            ###########################################################
            ################# Arm Drone State #########################
            ###########################################################
            if not armed:
                lidar_objs = lidar_queue.get()
                if arm_drone:
                    arm(drone, output_queue)
            


            if armed and arm_drone:
                ######################################################
                ############  Lidar Detection ########################
                ######################################################
                if not lidar_queue.empty():
                    lidar_objs = lidar_queue.get()
                    if not auto_land and thrust>0:
                        output_queue.put(str(lidar_objs))
                        output_queue.put("AUTO_LANDING")
                        auto_land = True
                        lock_on_target = False
                    elif not auto_land:
                        output_queue.put(str(drone.battery))
                


                ##############################################################
                ###########  Camera Handling #################################
                ##############################################################
                if not camera_queue.empty():
                    camera_instructs = camera_queue.get()
                    #output_queue.put(str(camera_instructs))

                    if camera_instructs[0] != "search" and lock_on_target:
                        if camera_instructs[0] == "LEFT":
                            roll = -1*MAX_ANGLE
                        elif camera_instructs[0] == "RIGHT":
                            roll = MAX_ANGLE
                        else: 
                            roll = 0
                        
                        if camera_instructs[1] == "UP":
                            thrust = .58
                        elif camera_instructs[1] == "DOWN":
                            thrust = .45
                        else:
                            thrust = 0.5
                        
                        if camera_instructs[2] == "FORWARD":
                            pitch = MAX_ANGLE
                        elif camera_instructs[2] == "BACK":
                            pitch = -1*MAX_ANGLE
                        else:
                            pitch = 0

                        lost_target_time = 0
                        yaw = 0

                    elif lock_on_target:
                        #If target is lost wait MAX_LOST_TIME for target to reappear otherwise auto land
                        if lost_target_time == 0:
                            lost_target_time = time.time()
                        
                        if lost_target_time + MAX_LOST_TIME> time.time():
                            auto_land = True
                            lock_on_target = False
                        
                        pitch = 0
                        thrust = 0.5
                        roll = 0
                        yaw = 0
                        

                ##############################################################
                ################# Battery Check ##############################
                ##############################################################
                #if drone.battery

                ################################################################   
                ##################  AUTO LAND ##################################
                ###############################################################      
                if auto_land:
                    #0.5 is hover value 0.43 is value to slowly land
                    thrust = .43
                    yaw = 0
                    pitch = 0
                    roll = 0
                    #print(lidar_objs)
                
                #Send intructions to drone
                set_attitude(drone, thrust=thrust, roll_angle=roll, pitch_angle=pitch, yaw_angle=yaw)

            elif armed and not arm_drone:
                disarm(drone, output_queue)


            #############################################
            ################ END LOOP ###################
            #############################################
    except:
        set_attitude(drone, thrust=0)
        drone.close()
    



def arm(drone, output_queue):
    print("Arming motors")
    output_queue.put("Arming Motors")
    # Copter should arm in GUIDED_NOGPS mode
    drone.mode = VehicleMode("GUIDED_NOGPS")
    
    output_queue.put(str(drone.battery))
    
    drone.armed = True

    while not drone.armed:
        print(" Waiting for arming...")
        output_queue.put(" Waiting for arming...")
        drone.armed = True
        time.sleep(1)
    
    output_queue.put("Armed")
    return None

def disarm(drone, output_queue):
    print("Disarming motors")
    output_queue.put("Disarming Motors")
    
    drone.armed = False

    while drone.armed:
        #print(" Waiting for arming...")
        output_queue.put(" Waiting for disarming...")
        drone.armed = False
        time.sleep(1)

    output_queue.put("Disarmed")
    return None

def send_attitude_target(drone, roll_angle = 0.0, pitch_angle = 0.0,
                        yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
                        thrust = 0.5):
    """
    use_yaw_rate: the yaw can be controlled using yaw_angle OR yaw_rate.
                When one is used, the other is ignored by Ardupilot.
    thrust: 0 <= thrust <= 1, as a fraction of maximum vertical thrust.
            Note that as of Copter 3.5, thrust = 0.5 triggers a special case in
            the code for maintaining current altitude.
    """
    if yaw_angle is None:
        # this value may be unused by the vehicle, depending on use_yaw_rate
        yaw_angle = drone.attitude.yaw
    # Thrust >  0.5: Ascend
    # Thrust == 0.5: Hold the altitude
    # Thrust <  0.5: Descend
    msg = drone.message_factory.set_attitude_target_encode(
        0, # time_boot_ms
        1, # Target system
        1, # Target component
        0b00000000 if use_yaw_rate else 0b00000100,
        to_quaternion(roll_angle, pitch_angle, yaw_angle), # Quaternion
        0, # Body roll rate in radian
        0, # Body pitch rate in radian
        math.radians(yaw_rate), # Body yaw rate in radian/second
        thrust  # Thrust
    )
    drone.send_mavlink(msg)

def to_quaternion(roll = 0.0, pitch = 0.0, yaw = 0.0):
    """
    Convert degrees to quaternions
    """
    t0 = math.cos(math.radians(yaw * 0.5))
    t1 = math.sin(math.radians(yaw * 0.5))
    t2 = math.cos(math.radians(roll * 0.5))
    t3 = math.sin(math.radians(roll * 0.5))
    t4 = math.cos(math.radians(pitch * 0.5))
    t5 = math.sin(math.radians(pitch * 0.5))

    w = t0 * t2 * t4 + t1 * t3 * t5
    x = t0 * t3 * t4 - t1 * t2 * t5
    y = t0 * t2 * t5 + t1 * t3 * t4
    z = t1 * t2 * t4 - t0 * t3 * t5

    return [w, x, y, z]

def set_attitude(drone, roll_angle = 0.0, pitch_angle = 0.0,
                yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
                thrust = 0.5, duration = 0):
    """
    Note that from AC3.3 the message should be re-sent more often than every
    second, as an ATTITUDE_TARGET order has a timeout of 1s.
    In AC3.2.1 and earlier the specified attitude persists until it is canceled.
    The code below should work on either version.
    Sending the message multiple times is the recommended way.
    """
    send_attitude_target(drone, roll_angle, pitch_angle,
                        yaw_angle, yaw_rate, False,
                        thrust)
    
    '''
    start = time.time()
    while time.time() - start < duration:
        send_attitude_target(drone, roll_angle, pitch_angle,
                            yaw_angle, yaw_rate, False,
                            thrust)
        time.sleep(0.1)
    # Reset attitude, or it will persist for 1s more due to the timeout
    send_attitude_target(drone, 0, 0,
                        0, 0, True,
                        thrust)
    '''
