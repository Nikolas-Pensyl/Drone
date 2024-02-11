import pygame

pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Check if any joystick is connected
if pygame.joystick.get_count() == 0:
    print("No joystick connected.")
    pygame.quit()
    exit()

# Initialize the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick Name: {joystick.get_name()}")

try:
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:
                # Joystick axis motion event
                print(f"Axis {event.axis} and {joystick.get_id()}: {joystick.get_axis(event.axis)}")

            elif event.type == pygame.JOYBUTTONDOWN:
                # Joystick button down event
                print(f"Button {event.button} down")

            elif event.type == pygame.JOYBUTTONUP:
                # Joystick button up event
                print(f"Button {event.button} up")

except KeyboardInterrupt:
    pass

finally:
    # Quit the pygame
    pygame.quit()
