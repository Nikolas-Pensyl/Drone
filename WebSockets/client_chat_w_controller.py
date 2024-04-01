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

async def send_message():
    uri = "ws://10.42.0.1:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            # Send a message to the server
            message = ''
            for event in pygame.event.get():
                if event.type == pygame.CONTROLLERAXISMOTION:
                    # Joystick axis motion event
                    message = f"Axis {event.axis}: {joystick.get_axis(event.axis)}"
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
            if response != '':
                print(response)

# Start the WebSocket client
asyncio.get_event_loop().run_until_complete(send_message())
