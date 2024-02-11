import asyncio
import websockets
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
from Drone import arm, set_attitude
import json


async def droneStartAndControl(websocket, path):
    connection_string = '/dev/ttyS0'
    baud_rate = 57600

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    drone = connect(connection_string, baud_rate)
    arm(drone)
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

            set_attitude(vehicle=drone, thrust=thrust)

            # Send a response back to the client
            await websocket.send("ready")
    
    except:
        set_attitude(thrust=0)
        drone.close()


# Start the WebSocket server
start_server = websockets.serve(droneStartAndControl, "10.42.0.1", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
