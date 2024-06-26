import asyncio
import websockets
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import json


def arm():
    print("Arming motors")
    # Copter should arm in GUIDED_NOGPS mode
    drone.mode = VehicleMode("GUIDED_NOGPS")
    drone.armed = True
    print(drone.battery)
    while not drone.armed:
        print(" Waiting for arming...")
        drone.armed = True
        time.sleep(1)
    
    return None

def send_attitude_target(roll_angle = 0.0, pitch_angle = 0.0,
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

def set_attitude(roll_angle = 0.0, pitch_angle = 0.0,
                yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
                thrust = 0.5, duration = 0):
    """
    Note that from AC3.3 the message should be re-sent more often than every
    second, as an ATTITUDE_TARGET order has a timeout of 1s.
    In AC3.2.1 and earlier the specified attitude persists until it is canceled.
    The code below should work on either version.
    Sending the message multiple times is the recommended way.
    """
    send_attitude_target(roll_angle, pitch_angle,
                        yaw_angle, yaw_rate, False,
                        thrust)
    start = time.time()
    while time.time() - start < duration:
        send_attitude_target(roll_angle, pitch_angle,
                            yaw_angle, yaw_rate, False,
                            thrust)
        time.sleep(0.1)
    # Reset attitude, or it will persist for 1s more due to the timeout
    send_attitude_target(0, 0,
                        0, 0, True,
                        thrust)
    



#Check which USB with ls /dev/tty*
#ttyACM1 = USB
#ttyACM0 = USB
#ttyS0   = PINS

connection_string = '/dev/ttyACM0'
baud_rate = 57600

# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
drone = connect(connection_string, baud_rate)

print("Arming")
arm()
print("Armed")

async def droneStartAndControl(websocket, path):
    print("Server Ready")
    print(path)
    try:
        while True:
            # Wait for a message from the client
            message = await websocket.recv()
            new_message = json.loads(message)

            thrust = new_message['thrust']
            yaw = new_message['yaw']
            pitch = new_message['pitch']
            roll = new_message['roll']
            lock = new_message['lockTarg']

            set_attitude(thrust=thrust)
            print(message)
            # Send a response back to the client
            await websocket.send("ready")
    
    except:
        set_attitude(thrust=0)
        drone.close()


# Start the WebSocket server
print("Starting Server")
start_server = websockets.serve(droneStartAndControl, "10.42.0.1", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()





