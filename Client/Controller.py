import asyncio
import websockets
import pygame._sdl2.controller, pygame
import json


'''
        Axis 5: Right Trigger  --> ALTITUDE(UP/DOWN)
        No Press(0)      --> thrust(0)
        Full Press(32767)    --> thrust(1)

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

        Button 2: Pink Square    --> Hold Alitude (thrust = 0.5)  (After release of button able to release Axis 0 with out throttle going to 0)
        Button 3: Green Triangle --> Lock/Release Target
        Button 1: Red Circle     --> AutoLand
    '''

def controller_main():
    # Start the WebSocket client
    asyncio.get_event_loop().run_until_complete(send_message())

async def send_message():
    uri = "ws://10.42.0.1:8765"
    holdAlt = False
    lockTarg = False
    autoLand = False

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

    async with websockets.connect(uri) as websocket:
        while True:

            for event in pygame.event.get():
                    if event.type == pygame.CONTROLLERBUTTONDOWN:
                        # Joystick button down event
                        if event.button == 1:
                            autoLand = True
                            lockTarg = False
                            holdAlt = False
                        elif event.button == 2:
                            holdAlt = True
                        break

                    elif event.type == pygame.CONTROLLERBUTTONUP:
                        # Joystick button up event
                        if event.button == 3:
                            lockTarg = not lockTarg
                        elif event.button ==0:
                            autoLand = False
                            holdAlt = False
                        break

            # Send a message to the server
            message = {
                "thrust": 0.5 if holdAlt else 0.43 if autoLand else abs(max(joystick.get_axis(5)/32767, 0)),
                "yaw": joystick.get_axis(0),
                "pitch": (joystick.get_axis(3)*-1),
                "roll": joystick.get_axis(2),
                "lockTarg": lockTarg
            }

                    
            await websocket.send(json.dumps(message))

            # Receive and print the response from the server
            response = await websocket.recv()
            if len(response)>0:
                print(response)