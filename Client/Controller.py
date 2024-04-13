import asyncio
import websockets
import pygame._sdl2.controller, pygame
import json

#TODO: Battery Level (5%) and RPI Battery Level (8%) Auto Land


'''
        Axis 5: Right Trigger  --> ALTITUDE(UP/DOWN)
        No Press(0)      --> thrust(0.4)
        Full Press(32767)    --> thrust(0.75)

        Axis 1: Right joystick left and right  --> YAW/(Turn left/right)
        left (-32768)   -->  YAW(-1)
        middle(0)       -->  none(0)
        right(32767)    -->  right(1)


        joystick.get_hat(0) --> 
            (0,0)   --> Nothing
            (1,0)   --> Right
            (-1,0)  --> Left
            (0,1)   --> Up
            (0,-1)  --> Down
    
        These can be combined so a UP/DOWN and LEFT/RIGHT is done at the same time

        DPAD: UP/DOWN --> PITCH/(Move Forward/Backward)
        bottom  --> backwards(-5)       
        middle  --> none(0)
        top     --> forwards (5)

        DPAD:  LEFT/RIGHT  --> ROLL(Move left/right)
        left    -->  left(-5)
        middle  -->  none(0)
        right   -->  right(5)

        Button 0: Blue X         --> Clear States
        Button 1: Red Circle     --> AutoLand
        Button 2: Pink Square    --> Hold Alitude (thrust = 0.5)  (After release of button able to release Axis 0 with out throttle going to 0)
        Button 3: Green Triangle --> Lock/Release Target
        Button 4: Left Bumper    --> DisArm (Only when throttle is 0 and Drone is armed)
        Button 5: Right Bumper   --> Arm    (Only when drone is in DisArm State)
    '''

def controller_main():
    # Start the WebSocket client
    asyncio.get_event_loop().run_until_complete(send_message())

async def send_message():
    uri = "ws://10.42.0.1:8765"
    holdAlt = False
    lockTarg = False
    autoLand = False
    armed = False
    thrust_active = False

    MAX_ANGLE = 5
    MIN_THROTTLE =  .4
    MAX_THROTTLE = .75

    MULTIPLY_THROTTLE  = MAX_THROTTLE-MIN_THROTTLE

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
            joy_axis_5 = joystick.get_axis(5)
            for event in pygame.event.get():
                    if event.type == pygame.CONTROLLERBUTTONDOWN:
                        # Joystick button down event
                        if event.button == 1 and armed and thrust_active:
                            autoLand = True
                            lockTarg = False
                            holdAlt = False

                        elif event.button == 2 and armed and thrust_active:
                            holdAlt = True

                        elif event.button == 4 and joy_axis_5 == 0 and armed and not holdAlt and not lockTarg and not thrust_active:
                            armed = False

                        elif event.button == 5 and joy_axis_5 == 0 and not armed:
                            armed = True
                        break

                    elif event.type == pygame.CONTROLLERBUTTONUP:
                        # Joystick button up event
                        if event.button == 3 and armed and thrust_active: 
                            lockTarg = not lockTarg
                        elif event.button ==0 and armed:
                            autoLand = False
                            holdAlt = False
                            lockTarg = False
                            thrust_active = not thrust_active
                        break
            

            

            # Send a message to the server
            message = {
                "thrust": 0 if not thrust_active else 0.43 if autoLand else 0.5 if autoLand else ((joy_axis_5/32767)*MULTIPLY_THROTTLE)+MIN_THROTTLE,
                "yaw": joystick.get_axis(2),
                "pitch": joystick.get_hat(0)[1]*MAX_ANGLE,
                "roll": joystick.get_hat(0)[0]*MAX_ANGLE,
                "lockTarg": lockTarg,
                "armed": armed
            }

                    
            await websocket.send(json.dumps(message))

            # Receive and print the response from the server
            response = await websocket.recv()
            if len(response)>0:
                print(response)