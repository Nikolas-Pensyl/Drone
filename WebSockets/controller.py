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

try:
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Joystick axis motion event
                print(f"Axis {event.axis}: {joystick.get_axis(event.axis)}")

            elif event.type == pygame.JOYBUTTONDOWN:
                # Joystick button down event
                print(f"Button {event.button} down")

            elif event.type == pygame.JOYBUTTONUP:
                # Joystick button up event
                print(f"Button {event.button} up")

            elif event.type == pygame.JOYHATMOTION:
                try:
                    print(joystick.get_hat(0))
                except:
                    pass
        

except KeyboardInterrupt:
    pass

finally:
    # Quit the pygame
    pygame.quit()
