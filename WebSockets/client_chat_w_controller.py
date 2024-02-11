import asyncio
import websockets
import pygame._sdl2.controller, pygame

pygame.init()

# Initialize the joystick
pygame._sdl2.controller.init()

# Check if any joystick is connected
if pygame._sdl2.controller.get_count() == 0:
    print("No joystick connected.")
    pygame.quit()
    exit()

# Initialize the first joystick
joystick = pygame._sdl2.controller.Controller(0)
joystick.init()

'''
    Axis 0: left joystick up and down  --> ALTITUDE(UP/DOWN)
    bottom(32767)  --> thrust(0)
    middle(0)      --> thrust(0)
    top(-32768)    --> thrust(1)

    Axis 1: left joystick left and right  --> YAW/(Turn left/right)
    left (-32768)   -->  YAW(-1)
    middle(0)       -->  none(0)
    right(32767)    -->  right(1)

    Axis 2: right joystick up and down --> PITCH/(Move Forward/Backward)
    bottom(32767) --> backwards(-1)       
    middle (0)    --> none(0)
    top(-32768)   --> forwards (1)

    Axis 3: right joystick left and right --> ROLL(Move left/right)
    left (-32768)   -->  left(-1)
    middle(0)       -->  none(0)
    right(32767)    -->  right(1)
'''

async def send_message():
    uri = "ws://10.42.0.1:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            # Send a message to the server
            message = ''

            thrust = joystick.get_axis(0)
            while message == '':
                for event in pygame.event.get():
                    if event.type == pygame.CONTROLLERAXISMOTION:
                        # Joystick axis motion event
                        message = f"Axis {0}: {joystick.get_axis(0)}" + f", Axis {1}: {joystick.get_axis(1)}" + f", Axis {2}: {joystick.get_axis(2)}" + f", Axis {3}: {joystick.get_axis(3)}"  + f", Axis {4}: {joystick.get_axis(4)}" + f", Axis {5}: {joystick.get_axis(5)}"  
                        break
                    
                    elif event.type == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
                        # Joystick button up event
                        message = f"DPAD {event.DPAD} down"
                        break
                    
                    elif event.type == pygame.CONTROLLERBUTTONDOWN:
                        # Joystick button down event
                        message = f"Button {event.button} down"
                        break

                    elif event.type == pygame.CONTROLLERBUTTONUP:
                        # Joystick button up event
                        message = f"Button {event.button} up"
                        break

                    
            await websocket.send(message)

            # Receive and print the response from the server
            response = await websocket.recv()
            print(f"Server response: {response}")
            websocket.recv()

# Start the WebSocket client
asyncio.get_event_loop().run_until_complete(send_message())