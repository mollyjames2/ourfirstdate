import pygame
import numpy as np
import LCD_1in44
import time

# Initialize Pygame
pygame.init()

# Set the Pygame screen size to match the LCD display
screen = pygame.Surface((LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT))

# Initialize the LCD
disp = LCD_1in44.LCD()
Lcd_ScanDir = LCD_1in44.SCAN_DIR_DFT
disp.LCD_Init(Lcd_ScanDir)
disp.LCD_Clear()

# Load sprite (sam.png) from assets/sprites folder
sprite = pygame.image.load('assets/sprites/sam_sprite.png')

# Get the size of the sprite
sprite_rect = sprite.get_rect()

# Starting position for the sprite
x, y = 30, 30  # Position on the LCD

# Define the movement speed
move_speed = 5

# Main loop
try:
    while True:
        # Fill the screen with a color (optional)
        screen.fill((0, 0, 0))  # Black background

        # Check button presses to move the sprite
        if disp.digital_read(disp.GPIO_KEY_UP_PIN) == 0:
            y -= move_speed  # Move up
        if disp.digital_read(disp.GPIO_KEY_DOWN_PIN) == 0:
            y += move_speed  # Move down
        if disp.digital_read(disp.GPIO_KEY_LEFT_PIN) == 0:
            x -= move_speed  # Move left
        if disp.digital_read(disp.GPIO_KEY_RIGHT_PIN) == 0:
            x += move_speed  # Move right

        # Ensure the sprite stays within screen bounds
        x = max(0, min(x, LCD_1in44.LCD_WIDTH - sprite_rect.width))
        y = max(0, min(y, LCD_1in44.LCD_HEIGHT - sprite_rect.height))

        # Draw the sprite on the Pygame surface at the new position
        screen.blit(sprite, (x, y))

        # Convert Pygame surface to a numpy array (this is 3D, but we need a 2D color format)
        pygame_image = pygame.surfarray.pixels3d(screen)

        # Convert the image to the format required by your LCD driver (RGB565 or 16-bit color)
        img_data = np.zeros((LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT, 2), dtype=np.uint8)
        img_data[..., 0] = np.bitwise_and(pygame_image[..., 0], 0xF8) + np.right_shift(pygame_image[..., 1], 5)
        img_data[..., 1] = np.bitwise_and(np.left_shift(pygame_image[..., 1], 3), 0xE0) + np.right_shift(pygame_image[..., 2], 3)

        # Convert img_data into a 1D array of pixel data (as a list)
        img_data_flat = img_data.flatten()

        # Ensure compatibility and pass it correctly to LCD_ShowImage
        img_data_flat = np.array(img_data_flat)  # Ensure it's a numpy array

        # Show the image on the LCD
        disp.LCD_ShowImage(img_data_flat, 0, 0)

        # Delay to control the refresh rate
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")
    disp.module_exit()

