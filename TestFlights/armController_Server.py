import asyncio
import websockets
from threading import Thread
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math
import Drone
import json

message = ''
message_read = False

async def server_handler(websocket, path):
    while True:
        # Wait for a message from the client
        message = await websocket.recv()
        print(f"Client: {message}")

        message_read = False
        while not message_read: continue

        # Send a response back to the client
        response = f"Server received: {message}"
        await websocket.send(response)



def messaging():
    # Start the WebSocket server
    start_server = websockets.serve(server_handler, "10.42.0.1", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def droneStartAndControl():
    connection_string = '/dev/ttyS0'
    baud_rate = 57600

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    drone = Drone(connection_string, baud_rate)
    try:
        while True:
            while message_read: continue
            new_message = json.loads(message)
            message_read = True

            thrust = new_message['thrust']
            yaw = new_message['yaw']
            pitch = new_message['pitch']
            roll = new_message['roll']
            lock = new_message['lockTarg']

            drone.set_attitude(thrust=thrust)
    
    except:
        drone.close()


if __name__ == "__main__":
    message_thread = Thread(target=messaging)
    drone_thread = Thread(target=droneStartAndControl)

    message_thread.start()
    drone_thread.start()

