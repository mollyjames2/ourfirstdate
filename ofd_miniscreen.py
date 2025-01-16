import pygame
import sys
import random
from PIL import Image
import textwrap
import os
import math


### INITIALISATION
# Pygame Initialization
pygame.init()
pygame.font.init()

if getattr(sys, 'frozen', False):
    # If running as a bundled executable
    BASE_PATH = sys._MEIPASS
else:
    # If running as a script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

scene = 0
actionable = False  # Whether the actionable game has started

# CONSTANTS
WIDTH, HEIGHT = 128, 128
SPRITE_SCALER = 0.28
SPRITE_WIDTH, SPRITE_HEIGHT = 50*SPRITE_SCALER, 70*SPRITE_SCALER
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0) # for the beers
FOLLOW_DISTANCE = 40 * SPRITE_SCALER
DELAY_FRAMES = 3
MOVEMENT_SPEED = 5 * SPRITE_SCALER
FPS = 30
font_large = pygame.font.SysFont("Verdana", int(35 * SPRITE_SCALER))
font_small = pygame.font.SysFont("Verdana", int(30 * SPRITE_SCALER))
font = font_small

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Date Adventure")
clock = pygame.time.Clock()

# Key State Initialization
key_states = {"up_pressed": False, "down_pressed": False}


###################################################

#--------------------SPRITES----------------------#
class SpriteManager:
    
    def __init__(self):
        """Initialize the sprite manager with an empty dictionary."""
        self.sprites = {}
        
    def load(self, name, path, size=None):
        """Load and optionally scale a sprite."""
        full_path = os.path.join(BASE_PATH, path)  # Construct the full path
        image = pygame.image.load(full_path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        self.sprites[name] = image
        
    def load_with_aspect_ratio(self, name, path, target_height):
        """Load a sprite and scale it while maintaining the aspect ratio."""
        image = pygame.image.load(path).convert_alpha()
        original_width, original_height = image.get_width(), image.get_height()
        aspect_ratio = original_width / original_height
        scaled_width = int(target_height * aspect_ratio)
        scaled_image = pygame.transform.scale(image, (scaled_width, target_height))
        self.sprites[name] = scaled_image

    def get(self, name):
        """Retrieve a sprite by name."""
        return self.sprites.get(name)

# Initialize Sprite Manager
sprites = SpriteManager()

# Load and scale sprites
sprites.load("sam", "assets/sprites/sam_sprite.png", (SPRITE_WIDTH, SPRITE_HEIGHT))
sprites.load("molly", "assets/sprites/molly_sprite.png", (SPRITE_WIDTH, SPRITE_HEIGHT))
sprites.load("pub", "assets/sprites/LHA.png", (150 * SPRITE_SCALER, 150 * SPRITE_SCALER))
sprites.load("bar", "assets/sprites/bar.png", (150 * SPRITE_SCALER, 150 * SPRITE_SCALER))
sprites.load("table", "assets/sprites/table.png", (200 * SPRITE_SCALER, 100 * SPRITE_SCALER))
sprites.load("door", "assets/sprites/door.png", (100 * SPRITE_SCALER, 100 * SPRITE_SCALER))
sprites.load("house", "assets/sprites/house.png", (150 * SPRITE_SCALER, 100 * SPRITE_SCALER))
sprites.load("maggie", "assets/sprites/mag.png", (SPRITE_WIDTH*1.5, SPRITE_HEIGHT*1.5))
sprites.load("mike", "assets/sprites/mike.png", (SPRITE_WIDTH*1.5, SPRITE_HEIGHT*1.5))
sprites.load("sofa", "assets/sprites/sofa.png", (200 * SPRITE_SCALER, 100 * SPRITE_SCALER))
sprites.load("heart", "assets/sprites/heart.png", (SPRITE_WIDTH, SPRITE_HEIGHT))



# Load the bike sprite with aspect ratio scaling
sprites.load_with_aspect_ratio("bike", "assets/sprites/bike.png", SPRITE_HEIGHT)


#call the sprites
sam = sprites.get("sam")
molly = sprites.get("molly")
bike = sprites.get("bike")
pub = sprites.get("pub")
bar = sprites.get("bar")
table = sprites.get("table")
door = sprites.get("door")
house = sprites.get("house")
maggie = sprites.get("maggie")
mike = sprites.get("mike")
sofa = sprites.get("sofa")
heart = sprites.get("heart")

# Adjusted starting positions for sprites on the 128x128 screen
sam_pos = pygame.Vector2(int(30 * SPRITE_SCALER), HEIGHT // 2 - int(40 * SPRITE_SCALER))  # Sam's position, slightly left and vertically centered

# Molly starts off-screen, much further left and above the screen (out of view)
molly_pos = pygame.Vector2((-SPRITE_WIDTH * SPRITE_SCALER)+2, -SPRITE_HEIGHT -5 * SPRITE_SCALER)  # Molly's off-screen starting position (out of view)

# Calculate bike position directly below Sam (scaled accordingly)
bike_pos = pygame.Vector2(
    sam_pos.x - 10 * SPRITE_SCALER,  # Align horizontally with Sam
    sam_pos.y + SPRITE_HEIGHT * SPRITE_SCALER // 2  # A sprite height below Sam
)

# Function to draw sprites
def draw_sprite(sprite, position):
    """Draw a sprite at a given position."""
    screen.blit(sprite, position)



#--------------------GRAPHICS----------------------#
# Function to load and display a GIF prior to actionable gameplay
import pygame
from PIL import Image
import os

def display_gif(screen, gif_path, duration=3000, center=None):
    """
    Displays an animated GIF on the screen for a specified duration.
    
    Args:
        screen (pygame.Surface): The screen to display the GIF on.
        gif_path (str): Path to the GIF file.
        duration (int): Duration to display the GIF in milliseconds.
        center (tuple): Center coordinates for the GIF display (default is screen center).
    
    Returns:
        None
    """
    # Load the GIF using Pillow
    gif = Image.open(gif_path)
    frames = []
    frame_durations = []

    # Extract each frame and its duration
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_surface = pygame.image.fromstring(
            gif.tobytes(), gif.size, gif.mode
        ).convert_alpha()
        frames.append(frame_surface)
        frame_durations.append(gif.info.get("duration", 400))  # Default 400ms per frame

    # Scale each frame to fit the screen size
    scaled_frames = []
    for frame in frames:
        scaled_frame = pygame.transform.scale(frame, (screen.get_width(), screen.get_height()))
        scaled_frames.append(scaled_frame)

    current_frame = 0
    start_time = pygame.time.get_ticks()
    gif_displayed = False

    # Set center to screen center if not specified
    if center is None:
        center = (screen.get_width() // 2, screen.get_height() // 2)

    # Display the animated GIF
    while not gif_displayed:
        current_time = pygame.time.get_ticks()

        # Determine elapsed time
        elapsed_time = current_time - start_time
        if elapsed_time < duration:
            # Determine the current frame to display
            total_duration = sum(frame_durations[: current_frame + 1])
            if elapsed_time > total_duration:
                current_frame = (current_frame + 1) % len(scaled_frames)

            # Display the current frame (scaled)
            screen.fill((0, 0, 0))  # Clear the screen
            screen.blit(scaled_frames[current_frame], (0, 0))  # Blit scaled frame to fill the screen
            pygame.display.flip()
        else:
            gif_displayed = True  # Mark the GIF as displayed

        # Handle events to allow quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

# Example usage
gif_path = os.path.join("assets", "GIFs", "LHA.gif")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Transition Function
# Animated transition between scenes
def scene_transition():
    for alpha in range(0, 256, 10):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    # Clear screen at the end of the transition
    screen.fill(BLACK)
    pygame.display.flip()
    clock.tick(30)
    
def draw_beers(beers, beer_states, bubbles):
    """
    Draws beers on the screen with their current states and animations.

    Args:
        beers (list): List of beer rectangles.
        beer_states (list): List of states for each beer (0: full, 1: 2/3 full, 2: 1/3 full, 3: empty).
        bubbles (list): List of bubble animations for each beer.

    Returns:
        None
    """
    # Positioning and scaling factors
    beer_width = int(60 * SPRITE_SCALER)  # Increase beer width (scaled)
    beer_height = int(120 * SPRITE_SCALER)  # Increase beer height (scaled)
    gap_between_beers = int(20 * SPRITE_SCALER)  # Increase gap between beers
    
    # Centering the beers horizontally
    total_beer_width = len(beers) * (beer_width + gap_between_beers) - gap_between_beers  # Total width of all beers including gaps
    start_x = (WIDTH - total_beer_width) // 2  # Starting x position to center the beers
    
    # Loop through each beer and draw it
    for i, beer in enumerate(beers):
        # Calculate the position for each beer
        beer_x = start_x + i * (beer_width + gap_between_beers)
        beer_y = HEIGHT // 2 - beer_height // 2  # Vertically center the beers
        
        # Scale the beer rectangle and its content
        scaled_beer = pygame.Rect(beer_x, beer_y, beer_width, beer_height)
        
        # Draw beer outline (scaled)
        pygame.draw.rect(screen, BLACK, scaled_beer, 2)  # Black outline
        state = beer_states[i]

        # Draw orange content and white line (scaled based on state)
        if state == 0:  # Full beer
            orange_top = scaled_beer.y
            orange_height = scaled_beer.height
            pygame.draw.rect(screen, ORANGE, scaled_beer.inflate(-2 * SPRITE_SCALER, -2 * SPRITE_SCALER))
            pygame.draw.rect(screen, WHITE, (scaled_beer.x + 2 * SPRITE_SCALER, scaled_beer.y + 2 * SPRITE_SCALER, scaled_beer.width - 4 * SPRITE_SCALER, 12 * SPRITE_SCALER))  # White line at the top
        elif state == 1:  # 2/3 full beer
            orange_top = scaled_beer.y + scaled_beer.height // 3
            orange_height = scaled_beer.height * 2 // 3
            pygame.draw.rect(screen, ORANGE, (scaled_beer.x + 2 * SPRITE_SCALER, orange_top, scaled_beer.width - 4 * SPRITE_SCALER, orange_height))
            pygame.draw.rect(screen, WHITE, (scaled_beer.x + 2 * SPRITE_SCALER, orange_top - 3 * SPRITE_SCALER, scaled_beer.width - 4 * SPRITE_SCALER, 12 * SPRITE_SCALER))  # White line just above orange
        elif state == 2:  # 1/3 full beer
            orange_top = scaled_beer.y + scaled_beer.height * 2 // 3
            orange_height = scaled_beer.height // 3
            pygame.draw.rect(screen, ORANGE, (scaled_beer.x + 2 * SPRITE_SCALER, orange_top, scaled_beer.width - 4 * SPRITE_SCALER, orange_height))
            pygame.draw.rect(screen, WHITE, (scaled_beer.x + 2 * SPRITE_SCALER, orange_top - 3 * SPRITE_SCALER, scaled_beer.width - 4 * SPRITE_SCALER, 12 * SPRITE_SCALER))  # White line just above orange
        elif state == 3:  # Empty beer
            orange_top = None  # No orange content
            orange_height = 0
            pygame.draw.rect(screen, BLACK, scaled_beer.inflate(-2 * SPRITE_SCALER, -2 * SPRITE_SCALER), 2)  # Thin black outline, no fill

        # Add and animate bubbles (scaled)
        if orange_top is not None:  # Only beers with orange content have bubbles
            # Add new bubbles randomly within the orange part
            if random.random() < 0.2:  # Probability of adding a bubble
                # Ensure bubbles spawn within the scaled beer bounds
                x = random.randint(int(scaled_beer.x + 3 * SPRITE_SCALER), int(scaled_beer.x + scaled_beer.width - 3 * SPRITE_SCALER))
                y = random.randint(int(orange_top), int(orange_top + orange_height - 3 * SPRITE_SCALER))
                dx = random.choice([-1, 0, 1])  # Random horizontal drift
                bubbles[i].append([x, y, dx])  # Bubble has x, y, and horizontal drift

            # Move bubbles upward and horizontally, remove those that leave the orange part
            for bubble in bubbles[i]:
                bubble[0] += bubble[2]  # Apply horizontal drift
                bubble[1] -= 1  # Move upward

                # Keep bubbles within the beer width and height (bounds check)
                if bubble[0] < scaled_beer.x + 3 * SPRITE_SCALER or bubble[0] > scaled_beer.x + scaled_beer.width - 3 * SPRITE_SCALER:
                    bubble[0] = max(scaled_beer.x + 3 * SPRITE_SCALER, min(bubble[0], scaled_beer.x + scaled_beer.width - 3 * SPRITE_SCALER))

                # Keep bubbles within the height of the beer's orange content
                if bubble[1] < orange_top:
                    bubble[1] = orange_top  # Stop bubbles from going below the orange content

            # Remove bubbles that leave the orange part
            bubbles[i] = [bubble for bubble in bubbles[i] if bubble[1] > orange_top]

            # Draw bubbles (scaled and larger)
            for x, y, _ in bubbles[i]:
                pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(4 * SPRITE_SCALER))  # Larger bubble size
        else:
            # Clear bubbles if the beer is empty
            bubbles[i] = []

beer_states = [1, 1, 1, 1, 1]  # All beers start as full

import pygame
import os

def take_picture():
    """
    Handles the process of taking a picture:
    - Displays an instruction to press ENTER.
    - Waits for ENTER to be pressed.
    - Flashes the screen white.
    - Displays the snapshot image on a white background with a black scene.
    """
    # Display the instruction (scaled font size)
    instruction = font_small.render("Press ENTER", True, WHITE)
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, int(20 * SPRITE_SCALER)))  # Centered at the top (scaled)

    pygame.display.flip()

    # Wait for the ENTER key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Flash the screen white
                screen.fill(WHITE)
                pygame.display.flip()
                pygame.time.wait(200)  # Wait 200ms
                waiting = False  # Exit the loop

    # Display the scene with a black background
    screen.fill(BLACK)

    # Create the white background for the picture (scaled box)
    box_width, box_height = int(WIDTH * (0.6 * SPRITE_SCALER)+20), int(HEIGHT * (0.6 * SPRITE_SCALER)+20)
    box_x, box_y = (WIDTH - box_width) // 2, (HEIGHT - box_height) // 2 - int(50 * SPRITE_SCALER)
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))

    # Load and display the snapshot image
    border_thickness = int(10 * SPRITE_SCALER)  # Scaled border thickness
    picture_x, picture_y = box_x + border_thickness, box_y + border_thickness
    picture_width, picture_height = box_width - 2 * border_thickness, box_height - 2 * border_thickness
    
    # Construct the full path to the snapshot image
    snapshot_path = os.path.join(BASE_PATH, "assets/pictures/snapshot.png")

    snapshot_image = pygame.image.load(snapshot_path)
    snapshot_image = pygame.transform.scale(snapshot_image, (picture_width, picture_height))
    screen.blit(snapshot_image, (picture_x, picture_y))
    pygame.display.flip()  # Update the screen to show the image


#--------------------DIALOGUE----------------------#
    
# Function to draw the dialog box using a Surface

def text_box(*lines):
    line_height = int(45 * SPRITE_SCALER)  # Increase line height for readability
    max_line_width = int(WIDTH - 60 * SPRITE_SCALER)  # Slightly increase max line width
    box_x, box_y = int(50 * SPRITE_SCALER), int(HEIGHT - 150 * SPRITE_SCALER)  # Adjust box position

    # Adjust box size to make it bigger for more text
    box_width, box_height = int(WIDTH - 100 * SPRITE_SCALER), int(120 * SPRITE_SCALER)  # Increase height of the box

    # Create a Surface for the dialog box
    dialog_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)

    # Preprocess lines to handle wrapping and box splitting
    processed_boxes = []
    for line in lines:
        wrapped = textwrap.wrap(line, width=max_line_width // font.size("A")[0])
        for i in range(0, len(wrapped), 2):
            processed_boxes.append(wrapped[i:i + 2])

    # Scrolling variables
    current_box_index = 0
    box_active = True

    while box_active:
        # Clear the dialog surface
        dialog_surface.fill((0, 0, 0, 0))  # Transparent background

        # Draw the box on the surface
        pygame.draw.rect(dialog_surface, WHITE, (0, 0, box_width, box_height))
        pygame.draw.rect(dialog_surface, BLACK, (int(10 * SPRITE_SCALER), int(10 * SPRITE_SCALER), box_width - int(20 * SPRITE_SCALER), box_height - int(20 * SPRITE_SCALER)))

        # Render and display the current box's lines
        if current_box_index < len(processed_boxes):
            current_box = processed_boxes[current_box_index]
            for i, line in enumerate(current_box):
                text_surface = font.render(line, True, WHITE)
                dialog_surface.blit(text_surface, (int(20 * SPRITE_SCALER), int(20 * SPRITE_SCALER) + i * line_height))

        # Draw the down arrow if there are more boxes to display
        # Coordinates for a downward-pointing triangle
       # Smaller coordinates for the downward-pointing triangle (down arrow)
        down_arrow_coords = [
            (box_width - int(40 * SPRITE_SCALER), box_height - int((35 * SPRITE_SCALER) + 0)),  # Top point of the arrow
            (box_width - int(30 * SPRITE_SCALER), box_height - int((45 * SPRITE_SCALER) + 0)),  # Left corner of the arrow
            (box_width - int(50 * SPRITE_SCALER), box_height - int((45 * SPRITE_SCALER) + 0)),  # Right corner of the arrow
        ]

        # Draw the down arrow using a polygon
        pygame.draw.polygon(dialog_surface, WHITE, down_arrow_coords)

        
        #down_arrow = font.render("↓", True, WHITE)
        #dialog_surface.blit(down_arrow, (box_width - int(40 * SPRITE_SCALER), box_height - int((35 * SPRITE_SCALER)+5)))

        # Blit the dialog surface onto the main screen
        screen.blit(dialog_surface, (box_x, box_y))
        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if current_box_index + 1 < len(processed_boxes):
                        current_box_index += 1
                    else:
                        box_active = False
                elif event.key == pygame.K_UP:
                    if current_box_index > 0:
                        current_box_index -= 1

    # Clear the dialog box by not blitting the surface after the loop ends
    pygame.display.flip()

dialog_triggered = False  # Add a flag to control dialog triggering

def draw_fireworks(fireworks):
    """
    Draw and update fireworks on the screen.
    Args:
        fireworks (list): List of active fireworks, each with position, state, and particles.
    """
    for firework in fireworks[:]:
        if firework["state"] == "ascending":
            # Increase firework speed to make it ascend faster
            firework["position"][1] -= firework["speed"] * 3 * SPRITE_SCALER  # Increase speed for faster ascent
            x, y = firework["position"]
            pygame.draw.circle(screen, firework["color"], (int(x), int(y)), int(6 * SPRITE_SCALER))  # Scaled ascending firework

            # Transition to explosion if it reaches a certain height
            if firework["position"][1] <= firework["explosion_height"]:
                firework["state"] = "exploding"
                firework["particles"] = [
                    {
                        "position": firework["position"][:],
                        # Increase velocity for faster explosion
                        "velocity": [
                            random.uniform(-7 * SPRITE_SCALER, 7 * SPRITE_SCALER),  # Increased velocity range
                            random.uniform(-7 * SPRITE_SCALER, 7 * SPRITE_SCALER),
                        ],
                        # Decrease particle lifetime for faster explosion effect
                        "lifetime": random.randint(10, 30),  # Shorter lifetime for faster explosion
                    }
                    for _ in range(30)  # Number of particles in the explosion
                ]
 

        elif firework["state"] == "exploding":
            # Update and draw particles
            for particle in firework["particles"][:]:
                particle["position"][0] += particle["velocity"][0]
                particle["position"][1] += particle["velocity"][1]
                particle["lifetime"] -= 1

                x, y = particle["position"]
                pygame.draw.circle(screen, firework["color"], (int(x), int(y)), int(4 * SPRITE_SCALER))  # Increased size for better visibility



                # Remove particle if its lifetime ends
                if particle["lifetime"] <= 0:
                    firework["particles"].remove(particle)

            # Remove firework if all particles are gone
            if not firework["particles"]:
                fireworks.remove(firework)



def move_sam(keys, sam_pos):
    """
    Update Sam's position based on key inputs using pre-scaled movement speed.
    """
    if keys[pygame.K_UP]:
        sam_pos.y -= MOVEMENT_SPEED  # Use pre-scaled MOVEMENT_SPEED
    if keys[pygame.K_DOWN]:
        sam_pos.y += MOVEMENT_SPEED
    if keys[pygame.K_LEFT]:
        sam_pos.x -= MOVEMENT_SPEED
    if keys[pygame.K_RIGHT]:
        sam_pos.x += MOVEMENT_SPEED

def follow_sam(sam_pos, molly_pos, follow_distance=FOLLOW_DISTANCE, follow_speed=3):
    """
    Makes Molly follow Sam with smoother movement, using pre-scaled follow distance and speed.
    """
    # Horizontal follow logic with a buffer zone
    follow_threshold = 3  # Keep the threshold as is, already small enough for scaled screen
    if abs(molly_pos.x - (sam_pos.x - follow_distance)) > follow_threshold:  # Add a small threshold
        if molly_pos.x < sam_pos.x - follow_distance:
            molly_pos.x += follow_speed
        elif molly_pos.x > sam_pos.x - follow_distance:
            molly_pos.x -= follow_speed

    # Vertical follow logic with a buffer zone
    if abs(molly_pos.y - sam_pos.y) > follow_threshold:  # Add a small threshold
        if molly_pos.y < sam_pos.y:
            molly_pos.y += follow_speed
        elif molly_pos.y > sam_pos.y:
            molly_pos.y -= follow_speed

def apply_idle_sway_with_follow(
    sam_pos, molly_pos, sway_timer, sway_direction, sway_magnitude, sway_frequency, keys, follow_speed=0.25, max_sway=0.1
):
    """
    Handles idle sway for Sam and Molly with directional veering based on key presses, using pre-scaled values.
    """
    sway_timer += 1
    if sway_timer > sway_frequency:  # Change sway direction at intervals
        sway_timer = 0
        sway_direction *= -1

    sway = sway_direction * sway_magnitude

    # Track how long keys are held to increase veering
    hold_sway = {"UP": 0, "DOWN": 0, "LEFT": 0, "RIGHT": 0}

    # Detect key presses and update sway timers
    if keys[pygame.K_UP]:
        hold_sway["UP"] += 1
    if keys[pygame.K_DOWN]:
        hold_sway["DOWN"] += 1
    if keys[pygame.K_LEFT]:
        hold_sway["LEFT"] += 1
    if keys[pygame.K_RIGHT]:
        hold_sway["RIGHT"] += 1

    # Reset sway when a key is released
    for key in hold_sway:
        if not keys[getattr(pygame, f"K_{key}")]:
            hold_sway[key] = 0

    # Calculate sway based on duration, scaled for smaller screen
    directional_sway = {
        "UP": min(hold_sway["UP"] * 0.001, max_sway),  # Reduced sway for small screen
        "DOWN": min(hold_sway["DOWN"] * 0.001, max_sway),
        "LEFT": min(hold_sway["LEFT"] * 0.001, max_sway),
        "RIGHT": min(hold_sway["RIGHT"] * 0.001, max_sway),
    }

    # Sam's movement with directional controls and veering, using pre-scaled values
    if keys[pygame.K_UP]:
        sam_pos.y += (0.001 + directional_sway["UP"])  # Reduced movement to fit screen
        sam_pos.x += sway  # Veers RIGHT
    if keys[pygame.K_DOWN]:
        sam_pos.y -= (0.001 + directional_sway["DOWN"])  # Reduced movement
        sam_pos.x -= sway  # Veers LEFT
    if keys[pygame.K_LEFT]:
        sam_pos.x += (0.001 + directional_sway["LEFT"])  # Reduced movement
        sam_pos.y -= sway  # Veers UP
    if keys[pygame.K_RIGHT]:
        sam_pos.x -= (0.001 + directional_sway["RIGHT"])  # Reduced movement
        sam_pos.y += sway  # Veers DOWN

    # Apply idle sway if no keys are pressed
    if not any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
        sam_pos.x += sway
        molly_pos.x += sway

    # Molly follows Sam
    follow_sam(sam_pos, molly_pos)

    return sam_pos, molly_pos, sway_timer, sway_direction

#####################################################################

#-------------------------MINIGAMES---------------------------------#
def minigame_scene_3():
    global beers, states, bubbles, actionable

    # Show instructions screen
    screen.fill(BLACK)
    instructions = font_small.render("Follow directions to drink!", True, WHITE)
    prompt = font_small.render("Press ENTER to start", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2 - 50 * SPRITE_SCALER))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 10 * SPRITE_SCALER))
    pygame.display.flip()

    # Wait for ENTER to start
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

    # Initialize game state
    target_key = None
    prompt_time = pygame.time.get_ticks()
    sobriety_bar = 100  # Full at start
    beer_index = 0  # Current beer being consumed
    state_index = 0  # Current state of the beer (0: full, 1: two-thirds full, 2: one-third full, 3: empty)
    reaction_time_limit = 2.0  # Seconds to press the correct key

    # Ensure bubbles and states are initialized
    bubbles = [[] for _ in range(len(beers))]
    beer_states = [0, 0, 0, 0, 0]  # All beers start as full
    
    # Mini-game loop
    while beer_index < len(beers):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - prompt_time) / 1000.0  # In seconds

        # Generate a new key sequence if none is active
        if target_key is None:
            target_key = random.choice([pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
            prompt_time = pygame.time.get_ticks()

        # Clear the screen
        screen.fill(BLACK)

       
        # Draw beers using the draw_beers function (already scaled)
        draw_beers(beers, beer_states, bubbles)

        # Draw sobriety bar (scaled width)
        pygame.draw.rect(screen, (0, 255, 0), (50 * SPRITE_SCALER, 20 * SPRITE_SCALER, sobriety_bar * 3 * SPRITE_SCALER, 20 * SPRITE_SCALER))
        sobriety_text = font_small.render("Sobriety", True, WHITE)
        screen.blit(sobriety_text, (50 * SPRITE_SCALER, 50 * SPRITE_SCALER))

        # Draw the key prompt (scaled font size and position)
        prompt_text = font_large.render(f"{pygame.key.name(target_key)}", True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 100 * SPRITE_SCALER))
        pygame.display.flip()

        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == target_key:
                    # Correct key pressed
                    beer_states[beer_index] = state_index + 1
                    if state_index == 2:
                        beer_index += 1  # Move to the next beer
                        state_index = 0
                    else:
                        state_index += 1
                    target_key = None  # Reset target key
                    sobriety_bar -= 7  # Decrease sobriety bar
                elif event.key != target_key:
                    # Incorrect key pressed
                    sobriety_bar -= 5  # Penalize for mistakes

        # End game if all beers are consumed
        if beer_index >= len(beers):
            break

    # After the mini-game ends, set all beers to fully empty
    for i in range(len(beer_states)):
        beer_states[i] = 3  # Fully empty (state 3)

    # Clear all bubbles after the game
    bubbles = [[] for _ in range(len(beers))]

    # Draw the final state with all beers empty
    screen.fill(BLACK)
    #screen.blit(table, (table_rect.x * SPRITE_SCALER, table_rect.y * SPRITE_SCALER))
    draw_beers(beers, beer_states, bubbles)

    # Display the final empty beer state before proceeding
    pygame.display.flip()
    pygame.time.delay(500)  # Optional: Small delay for visual clarity

    # All levels completed
    
    screen.fill(BLACK)

    
    dialogue_text = font_large.render("Congratulations!", True, WHITE)
    prompt_text = font_small.render("you finished all the beers!", True, WHITE)
    prompt_text2 = font_small.render("Press ENTER to continue", True, WHITE)
    screen.blit(dialogue_text, (WIDTH // 2 - dialogue_text.get_width() // 2, HEIGHT // 2 - int(50 * SPRITE_SCALER)))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + (int((50 * SPRITE_SCALER)-10))))
    screen.blit(prompt_text2, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + (int((50 * SPRITE_SCALER)+10))))


    pygame.display.flip()

    # Wait for ENTER key to transition to Scene 2
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                actionable = True
                return
 

#-----------------------------------------------------------------------
def minigame_scene_5():
    global sam_pos, molly_pos, actionable, scene

    # Instructions screen (scaled)
    screen.fill(BLACK)
    instruction_lines = [
        "Get to the house!",
        "Arrow keys to move."
    ]
    for i, line in enumerate(instruction_lines):
        rendered_line = font_small.render(line, True, WHITE)
        screen.blit(rendered_line, (WIDTH // 2 - rendered_line.get_width() // 2, HEIGHT // 2 - 60 * SPRITE_SCALER + i * int(30 * SPRITE_SCALER)))
    
    prompt = font_small.render("Press ENTER to start", True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 50 * SPRITE_SCALER))
    pygame.display.flip()
    # Initialize player and partner positions lower down
    sam_pos = pygame.Vector2(WIDTH - int(200 * SPRITE_SCALER), HEIGHT // 2 + int(150 * SPRITE_SCALER))  # Move Sam lower
    molly_pos = pygame.Vector2(WIDTH - int(250 * SPRITE_SCALER), HEIGHT // 2 + int(150 * SPRITE_SCALER))  # Move Molly lower

    # Wait for ENTER to start
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

    # Initialize sway parameters (scaled for small screen)
    sway_timer = 0
    sway_direction = 1  # Positive or negative sway
    sway_magnitude = 0.03 * SPRITE_SCALER  # Reduced sway for subtle movement
    sway_frequency = int(500 * SPRITE_SCALER)  # Frames before sway direction changes (~2 seconds at 60 FPS)

    # Game loop
    while True:
        screen.fill(BLACK)
        # Set the positions of molly's house and the pub (scaled)
        pub_rect = pub.get_rect(midright=(WIDTH - int(40 * SPRITE_SCALER), HEIGHT // 2 + 45))  # Pub on the right, above the text box
        # Draw house and pub sprites (already scaled)
        draw_sprite(house, house_rect)
        draw_sprite(pub, pub_rect)

        # Draw player and partner sprites
        draw_sprite(sam, sam_pos)  # Draw Sam sprite at current position
        draw_sprite(molly, molly_pos)  # Draw Molly sprite at current position
        
        # Apply sway and following behavior for movement
        keys = pygame.key.get_pressed()
        sam_pos, molly_pos, sway_timer, sway_direction = apply_idle_sway_with_follow(
            sam_pos, molly_pos, sway_timer, sway_direction, sway_magnitude, sway_frequency, keys
        )

        # Check collision with the house
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if sam_rect.colliderect(house_rect):
            break

        pygame.display.flip()

        # Handle quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


#------------------------------------------------------------------
def minigame_scene_6():
    """
    Mini-game where the player stops a moving heart above Sam and Molly to make them kiss.
    Includes an instruction screen before starting.
    """
    def show_instructions():
        # Instruction screen (scaled)
        screen.fill(BLACK)
        instructions = [
            "Stop the heart on the red line",
            "",
            "Press SPACE to stop it.",
            "",
            "Press ENTER to start."
        ]
        for i, line in enumerate(instructions):
            rendered_line = font_small.render(line, True, WHITE)
            screen.blit(rendered_line, (WIDTH // 2 - rendered_line.get_width() // 2, HEIGHT // 2 - 40 + i * int(30 * SPRITE_SCALER)))
        pygame.display.flip()

        # Wait for ENTER to start
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    waiting = False

    # Show instructions only once
    if not hasattr(minigame_scene_6, "instructions_shown"):
        show_instructions()
        minigame_scene_6.instructions_shown = True

    while True:  # Restart mini-game loop if missed
        # Initialize the mini-game
        heart_size = (int(100 * SPRITE_SCALER), int(75 * SPRITE_SCALER))  # Increase heart size
        heart_pos_x = WIDTH // 2 - heart_size[0] // 2  # Center the heart horizontally
        heart_pos_y = (HEIGHT // 2) - 5 - heart_size[1] // 2  # Center the heart vertically
        heart_speed = int(15 * SPRITE_SCALER)  # Scale heart movement speed using the pre-defined SPRITE_SCALER
        heart_direction = 1  # 1 for moving right, -1 for moving left
        heart_image = pygame.image.load("assets/sprites/heart.png")  # Ensure this image is available
        heart_image = pygame.transform.scale(heart_image, heart_size)

        game_running = True
        success = False

        # Mini-game loop
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Check if the heart is within the center of the screen with a 15-pixel buffer on both sides
                    heart_left = heart_pos_x
                    heart_right = heart_pos_x + heart_size[0]

                    # Define the buffer range (15 pixels) around the center
                    if heart_left >= WIDTH // 2 - heart_size[0] // 2 - 15 and heart_right <= WIDTH // 2 + heart_size[0] // 2 + 15:
                        success = True
                    game_running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Only complete the game if the heart is fully inside the target area
                    if success:
                        break

            # Update heart position
            heart_pos_x += heart_speed * heart_direction

            # Reverse direction if the heart hits the screen edges
            if heart_pos_x <= 0 or heart_pos_x >= WIDTH - heart_size[0]:
                heart_direction *= -1

            # Clear the screen
            screen.fill(BLACK)

            # Draw the sofa and characters (already scaled)
            draw_sprite(sofa, scene_6.sofa_rect)
            draw_sprite(sam, (sam_pos.x, sam_pos.y))
            draw_sprite(molly, (molly_pos.x, molly_pos.y))

            # Draw the heart (now bigger and centered)
            screen.blit(heart_image, (heart_pos_x, heart_pos_y))

            # Draw the target area for visual feedback (scaled)
            target_area_width = int(120 * SPRITE_SCALER)  # Target area width (just for visual reference)
            target_area_x_start = WIDTH // 2 - target_area_width // 2
            target_area_x_end = target_area_x_start + target_area_width
            target_area_y = HEIGHT // 2 - int(20 * SPRITE_SCALER)  # Slightly above the heart

            pygame.draw.rect(screen, (255, 0, 0), (target_area_x_start, target_area_y, target_area_x_end - target_area_x_start, int(5 * SPRITE_SCALER)))  # Visual target

            pygame.display.flip()
            clock.tick(30)

        # Check result and handle restart if necessary
        if success:
            text_box("You shared your first kiss!")
            break  # Exit the function on success
        else:
            text_box("Missed! Let's try again!")  # Show brief feedback
            continue  # Automatically restart the mini-game

###########################################################################################
# End the game
def game_completed():
    fireworks = []  # Active fireworks
    colors = [(128, 0, 128), (0, 255, 0), (0, 0, 255), (255, 255, 255)]  # Purple, green, blue, white

    # Fireworks animation (scaled)
    fireworks_duration = 5  # Display fireworks for 5 seconds
    start_time = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start_time) / 1000 < fireworks_duration:
        screen.fill(BLACK)

        # Periodically launch new fireworks (scaled)
        if random.random() < 0.05:  # Adjust frequency of fireworks
            fireworks.append({
                "position": [random.randint(int(100 * SPRITE_SCALER), int(WIDTH - 100 * SPRITE_SCALER)), HEIGHT],
                "speed": random.uniform(4 * SPRITE_SCALER, 6 * SPRITE_SCALER),
                "explosion_height": random.randint(int(100 * SPRITE_SCALER), int(HEIGHT // 2)),
                "color": random.choice(colors),
                "state": "ascending",
                "particles": [],
            })

        # Draw and update fireworks
        draw_fireworks(fireworks)
        pygame.display.flip()
        clock.tick(75)

    # Black screen with text box
    screen.fill(BLACK)
    # Create the white background for the picture (scaled)
    box_width, box_height = int(WIDTH * 0.6 * SPRITE_SCALER * 3), int(HEIGHT * 0.6 * SPRITE_SCALER * 3)
    box_x, box_y = (WIDTH - box_width) // 2, (HEIGHT - box_height) // 2 - int(50 * SPRITE_SCALER)
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))

    # Load and display the snapshot image (scaled)
    border_thickness = int(10 * SPRITE_SCALER)
    picture_x, picture_y = box_x + border_thickness, box_y + border_thickness
    picture_width, picture_height = box_width - 2 * border_thickness, box_height - 2 * border_thickness

    # Construct the full path to the snapshot image
    snapshot_path = os.path.join(BASE_PATH, "assets/pictures/us.png")
    snapshot_image = pygame.image.load(snapshot_path)
    snapshot_image = pygame.transform.scale(snapshot_image, (picture_width, picture_height))
    screen.blit(snapshot_image, (picture_x, picture_y))
    pygame.display.flip()  # Update the screen to show the image

    # Display the text box (scaled)
    text_box(
        "And the rest was history!",
        "Thank you for a wonderful year, my gorgeous girl!",
        "I can't wait for many more!",
        "I love you so much!"
    )

    # Happy Anniversary screen (scaled text)
    screen.fill(BLACK)
    message = font_large.render("Happy Anniversary!", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)  # Display for 2 seconds

    # Fade to black (scaled overlay)
    for alpha in range(0, 256, 10):  # Gradual fade to black
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(30)

    # End the game
    pygame.quit()
    sys.exit()


###############################################################################################               
#                                    SCENES                                                   #
###############################################################################################

#----------------------------------SCENE 0 -----------------------------#
# Scene 0: Opening scene
def scene_0(keys):
    global scene
    screen.fill(BLACK)
    
    # Scale font sizes and adjust text positioning based on the 128x128 screen
    title_text = font_large.render("Where it all began", True, WHITE)
    subtitle_text = font_small.render("Sam and Molly's first date", True, WHITE)
    prompt_text = font_small.render("Press ENTER to start", True, WHITE)

    # Center text horizontally and adjust vertical spacing based on scaling
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - int(100 * SPRITE_SCALER)))
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 - int(50 * SPRITE_SCALER)))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + int(50 * SPRITE_SCALER)))

    # Detect ENTER key press to transition to next scene
    if keys[pygame.K_RETURN]:
        scene = 1

#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 1-----------------------------#      
# Scene 1: Cycling to the pub
def scene_1(keys):
    global scene, player, partner, player_pos, partner_pos, text_state, actionable

    if not hasattr(scene_1, "interacted"):
        scene_1.interacted = False
    if not hasattr(scene_1, "met_molly"):
        scene_1.met_molly = False
    if not hasattr(scene_1, "pub_reached"):
        scene_1.pub_reached = False
    scene_1.molly_near_sam = False  # Track if Molly has caught up to Sam  

    screen.fill(BLACK)
    
    # Get the sprites for the scene (already pre-scaled)
    sam = sprites.get("sam")
    molly = sprites.get("molly")
    bike = sprites.get("bike")
    pub = sprites.get("pub")
    
    # Create rectangles for interactions (scaled)
    pub_rect = pub.get_rect(midright=(WIDTH - int(40 * SPRITE_SCALER), (HEIGHT // 2) - 15))
    sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)

    # Draw the pub (replace rectangle with the LHA sprite)
    screen.blit(pub, (pub_rect.x, pub_rect.y))
   
    # Draw the player sprite
    draw_sprite(sam, (sam_pos.x, sam_pos.y))

    # Draw the partner sprite
    draw_sprite(molly, (molly_pos.x, molly_pos.y))
    
    
    
    if not actionable and not scene_1.pub_reached:
        text_box("Oh look at the time, it's nearly 7pm!", "Use the arrow keys to cycle to the pub for your date.")
        actionable = True
        scene_1.pub_reached = True
        
    else:
        move_sam(keys, sam_pos)
        
        # Update bike's position relative to Sam
        
        bike_pos.x = sam_pos.x - int(7 * SPRITE_SCALER)  # Adjust X offset relative to Sam (scaled)
        bike_pos.y = sam_pos.y + SPRITE_HEIGHT // 2
        # Draw sam's bike (scaled)
        draw_sprite(bike, (bike_pos.x, bike_pos.y))# Adjust Y offset relative to Sam
        
        # Molly moves down to meet Sam (scaled)
        if sam_pos.x > WIDTH - int(300 * SPRITE_SCALER) and not scene_1.met_molly:
            molly_pos.y += int(5 * SPRITE_SCALER)

            if molly_pos.y >= HEIGHT // 2 - int(25 * SPRITE_SCALER):
                scene_1.met_molly = True
                text_box("Is that Molly?", "I should go see if she wants to walk together")
                actionable = False
                
        if scene_1.met_molly and not scene_1.interacted:
            # Sam and Molly interaction (scaled rectangles)
            sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, molly.get_width(), molly.get_height())
            molly_rect = pygame.Rect(molly_pos.x, molly_pos.y, sam.get_width(), sam.get_height())

            if sam_rect.colliderect(molly_rect):
                actionable = False
                exclamation = font_small.render("!", True, WHITE)
                screen.blit(exclamation, (sam_pos.x + int(15 * SPRITE_SCALER), sam_pos.y - int(30 * SPRITE_SCALER)))
                screen.blit(exclamation, (molly_pos.x + int(15 * SPRITE_SCALER), molly_pos.y - int(30 * SPRITE_SCALER)))

                if not scene_1.interacted:
                    text_box(
                        "Sam: Molly, right?",
                        "Molly: Yep! You must be Sam!",
                        "Sam: Cool! Nice to meet you!",
                        "Molly: Shall we carry on walking? I'll follow you!"
                    )
                    scene_1.interacted = True
                    actionable = True
                    
        if scene_1.met_molly and scene_1.interacted:                   
            actionable = True
            
            # Smoothly make Molly follow Sam (scaled)
            follow_sam(sam_pos, molly_pos)
            
            # Check if Molly is near Sam (scaled)
            if molly_pos.distance_to(sam_pos) < int(50 * SPRITE_SCALER):  # Proximity threshold
                scene_1.molly_near_sam = True
            else:
                scene_1.molly_near_sam = False

            # Transition to the next scene when player collides with the pub (scaled)
            if sam_rect.colliderect(pub_rect) and scene_1.interacted and scene_1.molly_near_sam:
                actionable = False
                screen.fill(BLACK)

                # Display "You made it to the pub! Press ENTER to continue" (scaled text)
                dialogue_text = font_large.render("You made it to the pub!", True, WHITE)
                prompt_text = font_small.render("Press ENTER to continue", True, WHITE)

                screen.blit(dialogue_text, (WIDTH // 2 - dialogue_text.get_width() // 2, HEIGHT // 2 - int(50 * SPRITE_SCALER)))
                screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + int(50 * SPRITE_SCALER)))
                pygame.display.flip()

                # Wait for ENTER key to transition to Scene 2
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()

                        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                            scene_transition()  # Trigger transition
                            scene = 2  # Move to Scene 2
                            return

#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 2-----------------------------#
# Scene 2: Going to the bar
def scene_2(keys):
    global scene, sam, molly, bar, actionable, sam_pos, molly_pos

    # Initialize elements
    if not hasattr(scene_2, "initialized"):
        sam_pos = pygame.Vector2(int(30 * SPRITE_SCALER), HEIGHT // 2 - int(25 * SPRITE_SCALER))  # Player starting position (scaled)
        molly_pos = pygame.Vector2(int(50 * SPRITE_SCALER), HEIGHT // 2 - int(25 * SPRITE_SCALER))  # Partner starting position (scaled)
        actionable = False  # Disable gameplay during GIF display
        scene_2.initialized = True
        scene_2.gif_displayed = False
        scene_2.molly_near_sam = False  # Track if Molly has caught up to Sam

    # Display the animated GIF (scaled properly)
    if not scene_2.gif_displayed:
        display_gif(screen, gif_path, duration=2500)
        actionable = True
        scene_2.gif_displayed = True

    # Fill the screen with black
    screen.fill(BLACK)

    # Draw the bar sprite (scaled)
    bar_rect = bar.get_rect(midtop=(WIDTH - (int(150 * SPRITE_SCALER)) + 20, HEIGHT // 2 - int(100 * SPRITE_SCALER)))  # Adjusted to center vertically (scaled)
    draw_sprite(bar, (bar_rect.x, bar_rect.y))

    # Render instructional text (scaled font)
    instruction_text = font_small.render("Walk to the bar", True, WHITE)
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, int(20 * SPRITE_SCALER)))  # Centered at the top (scaled)

    # Draw the Sam and Molly sprites (scaled)
    draw_sprite(sam, (sam_pos.x, sam_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Allow Sam movement
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)

        # Check if Molly is near Sam (scaled proximity threshold)
        if molly_pos.distance_to(sam_pos) < int(50 * SPRITE_SCALER):  # Proximity threshold (scaled)
            scene_2.molly_near_sam = True
        else:
            scene_2.molly_near_sam = False       

        # Check for interaction with the bar
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if sam_rect.colliderect(bar_rect) and scene_2.molly_near_sam:
            actionable = False  # Disable movement
            text_box("Let's get some beers in!")
        
        # Transition to next scene
        if not actionable:
            scene_transition()  # Trigger transition
            scene = 3  # Move to Scene 3
         
#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 3-----------------------------#
 # Scene 3: Going to the bar
def scene_3(keys):
    global scene, sam, molly, actionable, sam_pos, molly_pos, scene3, beers, beer_states, bubbles, table, table_rect

    # Initialize elements
    if not hasattr(scene_3, "initialized"):
        sam_pos = pygame.Vector2(int(30 * SPRITE_SCALER), HEIGHT // 2 - int(25 * SPRITE_SCALER))  # Player starting position (scaled)
        molly_pos = pygame.Vector2(int(50 * SPRITE_SCALER), HEIGHT // 2 - int(25 * SPRITE_SCALER))  # Partner starting position (scaled)
        actionable = True
        scene_3.game_played = False
        scene_3.initialized = True
        scene_3.molly_burped = False
        scene_3.molly_near_sam = False

    # Fill the screen with black
    screen.fill(BLACK)
    
    # Set positions for the door and table (scaled)
    table_rect = table.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # Table centered
    door_rect = door.get_rect(midtop=(WIDTH - int(75 * SPRITE_SCALER), int(50 * SPRITE_SCALER)))  # Adjusted door position
    
    # Initialize the beers (scaled)
    beers =  [
        pygame.Rect(table_rect.x + int(40 * SPRITE_SCALER) + i * int(30 * SPRITE_SCALER), table_rect.y - int(22 * SPRITE_SCALER), int(20 * SPRITE_SCALER), int(50 * SPRITE_SCALER))
        for i in range(5)
    ]
    bubbles = [[] for _ in range(5)]  # List of bubbles for each beer

    # Ensure beer states are initialized
    if not hasattr(scene_3, "beer_states"):
        beer_states = [0, 0, 0, 0, 0]  # All beers are full initially

    # Draw table and door sprites (scaled)
    draw_sprite(table, (table_rect.x, table_rect.y))
    draw_sprite(door, (door_rect.x, door_rect.y))

    # Draw beers on the table (scaled)
    #draw_beers(beers, beer_states, bubbles)

    # Draw player and partner sprites (scaled)
    draw_sprite(sam, (sam_pos.x, sam_pos.y))  # Draw player sprite
    draw_sprite(molly, (molly_pos.x, molly_pos.y))  # Draw partner sprite

    # Movement logic
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)
        
         # Check if Molly is near Sam (scaled proximity threshold)
        if molly_pos.distance_to(sam_pos) < int(50 * SPRITE_SCALER):  # Proximity threshold (scaled)
            scene_3.molly_near_sam = True
        else:
            scene_3.molly_near_sam = False 
     
    # Interaction with table (scaled interaction zone)
    interaction_zone = table_rect.inflate(int(1 * SPRITE_SCALER), int(1 * SPRITE_SCALER))  # Expand interaction zone by 1 pixel
    if pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT).colliderect(interaction_zone) and not scene_3.game_played and scene_3.molly_near_sam:
        actionable = False  # Disable movement during interaction
        text_box("Dutch courage....?")
        # Play mini-game
        minigame_scene_3()
        scene_3.game_played = True
        
    if scene_3.game_played and not scene_3.molly_burped:
        actionable = False
        for i in range(len(beer_states)):
            beer_states[i] = 3  # All beers are empty
        for i in range(len(bubbles)):
            bubbles[i] = []  # Clear bubbles for each beer
        draw_beers(beers, beer_states, bubbles)
        
        # Redraw background and sprites before showing dialog
        screen.fill(BLACK)  # Ensure background is consistent
        draw_sprite(table, (table_rect.x, table_rect.y))
        draw_sprite(door, (door_rect.x, door_rect.y))
        draw_sprite(sam, (sam_pos.x, sam_pos.y))  # Draw Sam sprite
        draw_sprite(molly, (molly_pos.x, molly_pos.y))  # Draw Molly sprite
        pygame.display.flip()  # Ensure everything is rendered before dialog
        
        # Show the dialog box
        text_box("Molly: BURRPPPP!!", "Sam: Fancy some fresh air?")
        scene_3.molly_burped = True
        actionable = True
    
   
        # Interaction with door (scaled interaction zone for door)
    interaction_zone_door = door_rect.inflate(int(1 * SPRITE_SCALER), int(1 * SPRITE_SCALER))  # Expand interaction zone for the door
    if pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT).colliderect(interaction_zone_door):
        actionable = False  # Disable movement during interaction

        # If the mini-game has been completed
        if scene_3.game_played:
            # Transition to Scene 4
            text_box("Molly: Let's go outside!")
            scene_transition()  # Trigger transition
            scene = 4  # Move to Scene 4
        else:
            actionable = False
            # Show dialogue indicating the mini-game needs to be played first
            text_box("Maybe we should have a drink first?")
            actionable = True  # Re-enable movement

#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 4------------------------------------------#
def scene_4(keys):
    global sam_pos, molly_pos, actionable, scene

    # Initialize positions and elements
    if not hasattr(scene_4, "initialized"):
        # Initialize sam and molly's positions (scaled)
        sam_pos = pygame.Vector2(-50, HEIGHT // 2)  # Start sam off-screen (left)
        molly_pos = pygame.Vector2(-70, HEIGHT // 2)  # Start molly off-screen (left)

        scene_4.image_displayed = False
        scene_4.door_visible = True
        scene_4.choose_bird = False
        scene_4.bird_chosen = False
        scene_4.mollys_opinion = False
        scene_4.molly_opinion_done = False
        scene_4.selected_choice = None
        scene_4.not_selected_choice = None
        scene_4.movement_complete = False
        scene_4.pic_taken = False
        actionable = False
        scene_4.initialized = True

    # Fill the screen with black
    screen.fill(BLACK)

    # Set door position
    door_rect = door.get_rect(midtop=(WIDTH - int(75 * SPRITE_SCALER), int(50 * SPRITE_SCALER)))  # Adjusted door position
    
    # Draw door only if it's visible
    if scene_4.door_visible:
        draw_sprite(door, door_rect)

    # Automatic movement of characters into position
    if not scene_4.movement_complete:
        sam_pos.x += 5 * SPRITE_SCALER
        molly_pos.x += 5 * SPRITE_SCALER

        if sam_pos.x >= WIDTH // 2:
            molly_pos = pygame.Vector2(WIDTH // 2 - SPRITE_WIDTH // 2 - int(30 * SPRITE_SCALER), HEIGHT // 2 - SPRITE_HEIGHT // 2)  # molly stops slightly left of center
            sam_pos = pygame.Vector2(WIDTH // 2 + SPRITE_WIDTH // 2 + int(30 * SPRITE_SCALER), HEIGHT // 2 - SPRITE_HEIGHT // 2)  # sam stops slightly right of center

            scene_4.movement_complete = True  # Movement complete, proceed with dialogue
            actionable = False

    # Scale Sam and Molly based on whether they're actionable or not
    if not actionable:
        # Make Sam and Molly much bigger when they're not actionable
        sam_size = (int(75 * SPRITE_SCALER), int(100 * SPRITE_SCALER))  # Larger Sam
        molly_size = (int(75 * SPRITE_SCALER), int(100 * SPRITE_SCALER))  # Larger Molly
    else:
        sam_size = (SPRITE_WIDTH, SPRITE_HEIGHT)  # Normal Sam size
        molly_size = (SPRITE_WIDTH, SPRITE_HEIGHT)  # Normal Molly size

    # Manually scale Sam and Molly
    scaled_sam = pygame.transform.scale(sam, sam_size)
    scaled_molly = pygame.transform.scale(molly, molly_size)

    # Draw sam and molly sprites with updated size
    screen.blit(sam, (sam_pos.x, sam_pos.y))
    screen.blit(molly, (molly_pos.x, molly_pos.y))

    # Dialogue progression
    if scene_4.movement_complete and not scene_4.choose_bird:
         # Fill the screen with black
        screen.fill(BLACK)
        
        # Draw sam and molly sprites with updated size
        screen.blit(scaled_sam, (sam_pos.x, sam_pos.y))
        screen.blit(scaled_molly, (molly_pos.x, molly_pos.y))
        text_box(
            "Sam: Hey, what's your favourite bird?",
            "Molly: That's a hard question!",
            "I like loads of different birds!",
            "Which is your favourite?"
        )
        scene_4.choose_bird = True

    if scene_4.choose_bird and not scene_4.molly_opinion_done:
        
        screen.fill(BLACK)
        choice_text = font_small.render("Press 1 for seagull", True, WHITE)
        choice_text2 = font_small.render("Press 2 for pigeon", True, WHITE)
        screen.blit(choice_text2, (WIDTH // 2 - choice_text.get_width() // 2, HEIGHT - (150*SPRITE_SCALER)))
        screen.blit(choice_text, (WIDTH // 2 - choice_text.get_width() // 2, HEIGHT - ((150*SPRITE_SCALER)+15)))

        # Check for keypresses
        if keys[pygame.K_1]:
            scene_4.selected_choice = "seagull"
            scene_4.not_selected_choice = "pigeon"
            scene_4.bird_chosen = True
        elif keys[pygame.K_2]:
            scene_4.selected_choice = "pigeon"
            scene_4.not_selected_choice = "seagull"
            scene_4.bird_chosen = True

        if scene_4.bird_chosen and not scene_4.mollys_opinion:  # Dialogue based on choice
            screen.fill(BLACK)
            screen.blit(scaled_sam, (sam_pos.x, sam_pos.y))
            screen.blit(scaled_molly, (molly_pos.x, molly_pos.y))
            if scene_4.selected_choice == "seagull":
                text_box("Molly: Well, they're European Herring gulls", "actually!")
                scene_4.mollys_opinion = True
            elif scene_4.selected_choice == "pigeon":
                text_box("Molly: Pigeons are great! I hope to hear you defending their valiant war efforts to a woman that totally didn't realise what she was getting herself into one day!")
                scene_4.mollys_opinion = True
                
        if scene_4.mollys_opinion and not scene_4.molly_opinion_done:
            text_box(f"Molly: Want to hear my thoughts on {scene_4.not_selected_choice}s?","Sam: Sure!")
            if scene_4.not_selected_choice == "seagull":
                text_box("Molly: Well, they're European Herring gulls", "actually!")
                scene_4.molly_opinion_done = True
            elif scene_4.not_selected_choice == "pigeon":
                text_box("Molly: Pigeons are great! I hope to hear you defending their valiant war efforts to a woman that totally didn't realise what she was getting herself into one day!")
                scene_4.molly_opinion_done = True

        if scene_4.molly_opinion_done and not scene_4.image_displayed:  # Take a photo
            text_box("Molly: Hey, let's take a picture")
            take_picture()
            scene_4.image_displayed = True  # Mark that the picture has been displayed
            scene_4.door_visible = False  # Hide the door while showing the picture

        if scene_4.image_displayed and not scene_4.pic_taken:  # After the picture
            text_box("Molly: Aww, our first picture!")
            scene_4.pic_taken = True

        if scene_4.pic_taken:  # Proceed to the next dialogue
            
            # Fill the screen with black
            screen.fill(BLACK)
            scene_4.door_visible = True
            
            # Redraw sam and molly sprites
            screen.blit(sam, (sam_pos.x, sam_pos.y))
            screen.blit(molly, (molly_pos.x, molly_pos.y))
            draw_sprite(door, (door_rect.x, door_rect.y))
                   
            text_box("Molly: Hey, you fancy coming back to mine?",
                     "Sam: That would be nice!",
                     "Molly: Great! Let's go then! I don't live too far from here!"
                    )
            
            actionable = True

    # Interaction with door (with buffer zone)
    door_buffer = door_rect.inflate(0.1, 0.1)  # Expand the door's interaction zone by 20 pixels in all directions
    if sam_pos.x >= door_buffer.x and sam_pos.x <= door_buffer.x + door_buffer.width:
        actionable = False
        text_box("Molly: Just checking...", "you're alright with dogs yeah?!")
        scene_transition()
        scene = 5

    # Movement logic
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)


#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 5------------------------------------------#
       
def scene_5(keys):
    global sam_pos, molly_pos, actionable, scene, house_rect, pub_rect

    # Initialize elements and positions
    if not hasattr(scene_5, "initialized"):
        
        # State variables
        actionable = False
        scene_5.dialogue_started = False
        scene_5.minigame_launched = False
        scene_5.initialized = True

    # Fill the screen with black
    screen.fill(BLACK)
    
    # Set the positions of molly's house and the pub (scaled)
    pub_rect = pub.get_rect(midright=(WIDTH - int(40 * SPRITE_SCALER), HEIGHT // 4 + 30))  # Pub on the right, above the text box
    house_rect = house.get_rect(midleft=(int(1 * SPRITE_SCALER), int(40 * SPRITE_SCALER)))  # House in top left

    # Initialize player and partner positions next to the pub (scaled)
    sam_pos = pygame.Vector2(WIDTH - int(200 * SPRITE_SCALER), HEIGHT // 2 - int(10 * SPRITE_SCALER))
    molly_pos = pygame.Vector2(WIDTH - int(250 * SPRITE_SCALER), HEIGHT // 2 - int(10 * SPRITE_SCALER))

    # Draw the sprites for the pub and house (scaled)
    draw_sprite(pub, pub_rect)
    draw_sprite(house, house_rect)

    # Draw the sam and molly sprites (scaled)
    draw_sprite(sam, (sam_pos.x, sam_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Handle initial dialogue
    if not scene_5.dialogue_started:       
            text_box("Molly: Ossh, that was a lot of pints.", "The walk home will be interesting!")      
            scene_5.dialogue_started = True
            actionable = True
            
    if scene_5.dialogue_started and not scene_5.minigame_launched: # Launch the mini-game
        minigame_scene_5()
        scene_5.minigame_launched = True
        actionable = False
        
    # Post-mini-game dialogue and transition to scene 6
    if scene_5.minigame_launched:
        
        text_box(
            "Molly: This is my place, come on in!",
            "Sam: Thanks!"
        )

        scene_transition()
        scene = 6  # Progress to scene 6

#---------------------------------------------------------------------------------------------------------#

#----------------------------------SCENE 6------------------------------------------#
             
def scene_6(keys):
    global sam_pos, molly_pos, actionable, scene

    # Initialize elements
    if not hasattr(scene_6, "initialized"):
        actionable = True

        # Initialize sprite positions
        # Set door position
        door_rect = door.get_rect(midtop=(WIDTH - int(75 * SPRITE_SCALER), int(50 * SPRITE_SCALER)))  # Adjusted door position
        sofa_rect = sofa.get_rect(center=(WIDTH // 2, HEIGHT // 5))  # Sofa in the center near the top
        scene_6.door_rect = door_rect
        scene_6.sofa_rect = sofa_rect

        scene_6.maggie_rect = maggie.get_rect(center=(WIDTH // 4, HEIGHT // 2 + 10))  # Dog in the middle left
        scene_6.mike_rect = mike.get_rect(center=(3 * WIDTH // 4, HEIGHT // 2 + 10))  # Cat in the middle right

        sam_pos = pygame.Vector2(door_rect.centerx - SPRITE_WIDTH  // 2, door_rect.bottom -20)  # In front of the door
        molly_pos = pygame.Vector2(sam_pos.x + SPRITE_WIDTH - 65, sam_pos.y - 5)  # Slightly to the right of Sam
        scene_6.maggie_pos = pygame.Vector2(scene_6.maggie_rect.x, scene_6.maggie_rect.y)  # Start position of Maggie
        scene_6.mike_pos = pygame.Vector2(scene_6.mike_rect.x, scene_6.mike_rect.y)  # Start position of Mike
        scene_6.sofa_pos = pygame.Vector2(scene_6.sofa_rect.x, scene_6.sofa_rect.y)  # Start position of Mike
    
        scene_6.sam_moved = False  # Flag to track if Sam has started moving
        scene_6.interacted = False  # Flag to track if Maggie has interacted with Sam
        scene_6.returning = False  # Flag to track if Maggie is returning to her original position
        scene_6.met_mike = False
        scene_6.met_maggie = False
        scene_6.maggie_exclamation = False  # Flag to display exclamation mark above Maggie
        scene_6.moving_to_sofa = False  # Trigger movement to sofa
        scene_6.initialized = True

    # Fill the screen with a background color (e.g., black)
    screen.fill(BLACK)

    # Draw the sprites
    draw_sprite(door, scene_6.door_rect)  # Draw the door
    draw_sprite(sofa, scene_6.sofa_rect)  # Draw the sofa
    draw_sprite(maggie, (scene_6.maggie_pos.x, scene_6.maggie_pos.y))  # Draw Maggie
    draw_sprite(mike, (scene_6.mike_pos.x, scene_6.mike_pos.y))  # Draw Mike
    draw_sprite(sam, (sam_pos.x, sam_pos.y))  # Draw Sam
    draw_sprite(molly, (molly_pos.x, molly_pos.y))  # Draw Molly

    # Draw exclamation mark above Maggie if required
    if scene_6.maggie_exclamation:
        exclamation = font_small.render("!", True, WHITE)
        screen.blit(exclamation, (scene_6.maggie_pos.x + 5, scene_6.maggie_pos.y - 5))

    # Check if Sam has started moving
    if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
        scene_6.sam_moved = True

    # Movement logic for Sam and Molly
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)

        # Check for interaction between Mike and Sam
        mike_rect = pygame.Rect(scene_6.mike_pos.x, scene_6.mike_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        molly_rect = pygame.Rect(molly_pos.x, molly_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if sam_rect.colliderect(mike_rect) and not scene_6.met_mike and scene_6.interacted:
            actionable = False
            text_box("Mike: Ahh my love, my life!", "Sam: Your cat's...French?!", "Molly: Yeaaahh.. I think it's weird too!")
            scene_6.met_mike = True
            scene_6.maggie_exclamation = True  # Show exclamation mark above Maggie
            actionable = True

        maggie_rect = pygame.Rect(scene_6.maggie_pos.x, scene_6.maggie_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if maggie_rect.colliderect(sam_rect) and scene_6.maggie_exclamation:
            actionable = False
            text_box("Maggie: You got any of them floor burgers, Sam?!")
            scene_6.maggie_exclamation = False  # Remove exclamation mark after interaction
            scene_6.met_maggie = True
            text_box("Molly: Ignore her! Let's sit on the sofa!")
            scene_6.moving_to_sofa = True  # Trigger movement to sofa

    # Move Maggie to meet Sam if Sam has started moving
    if scene_6.sam_moved and not scene_6.interacted:
        maggie_speed = 1
        if scene_6.maggie_pos.x < sam_pos.x - 5:
            scene_6.maggie_pos.x += maggie_speed
        elif scene_6.maggie_pos.x > sam_pos.x - 5:
            scene_6.maggie_pos.x -= maggie_speed

        if scene_6.maggie_pos.y < sam_pos.y:
            scene_6.maggie_pos.y += maggie_speed
        elif scene_6.maggie_pos.y > sam_pos.y:
            scene_6.maggie_pos.y -= maggie_speed

        # Check for interaction between Maggie and Sam
        maggie_rect = pygame.Rect(scene_6.maggie_pos.x, scene_6.maggie_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if maggie_rect.colliderect(sam_rect):
            actionable = False
            text_box("Sam: Why is her head so massive?", "Maggie: Heyyyyy Sam! Are you my new best friend?")
            scene_6.interacted = True
            scene_6.returning = True

    # Move Maggie back to her original position
    if scene_6.returning:
        actionable = True  # Re-enable movement for Sam and Molly
        maggie_speed = 1
        original_x, original_y = scene_6.maggie_rect.x, scene_6.maggie_rect.y
        if scene_6.maggie_pos.x < original_x:
            scene_6.maggie_pos.x += maggie_speed
        elif scene_6.maggie_pos.x > original_x:
            scene_6.maggie_pos.x -= maggie_speed

        if scene_6.maggie_pos.y < original_y:
            scene_6.maggie_pos.y += maggie_speed
        elif scene_6.maggie_pos.y > original_y:
            scene_6.maggie_pos.y -= maggie_speed

        # Check if Maggie has reached her original position
        if abs(scene_6.maggie_pos.x - original_x) < 1 and abs(scene_6.maggie_pos.y - original_y) < 1:
            scene_6.returning = False
            scene_6.met_maggie = True
            
    # Automatically move Sam and Molly to the sofa if triggered
    if scene_6.moving_to_sofa:
        actionable = True
        
          # Assuming scene_6.sofa_rect is defined as the rectangle representing the sofa
        sofa_center = scene_6.sofa_rect.center  # Get the center of the sofa
        center_threshold = 15  # You can adjust this threshold to make it more sensitive or lenient

        # Calculate the distance between Sam and the sofa's center
        sam_distance_to_sofa = math.sqrt((sam_pos.x - sofa_center[0])**2 + (sam_pos.y - sofa_center[1])**2)
        molly_distance_to_sofa = math.sqrt((molly_pos.x - sofa_center[0])**2 + (molly_pos.y - sofa_center[1])**2)

        # If both Sam and Molly are close enough to the sofa center (within threshold)
        if sam_distance_to_sofa < center_threshold and molly_distance_to_sofa < center_threshold:
            actionable = False
            text_box("Molly: Hey, can I kiss you?")
            scene_6.moving_to_sofa = False  # Trigger movement to sofa
            minigame_scene_6()  # Trigger the mini-game
            game_completed()  # End the game

############################################################################################
        
### GAMEPLAY LOOP

#-----------------------------------------
# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                key_states["up_pressed"] = True
            if event.key == pygame.K_DOWN:
                key_states["down_pressed"] = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                key_states["up_pressed"] = False
            if event.key == pygame.K_DOWN:
                key_states["down_pressed"] = False

    keys = pygame.key.get_pressed()

    if scene == 0:
        scene_0(keys)
    elif scene == 1:
        scene_1(keys)
    elif scene == 2:
        scene_2(keys)
    elif scene == 3:
        scene_3(keys)
    elif scene == 4:
        scene_4(keys)
    elif scene == 5:
        scene_5(keys)
    elif scene == 6:
        scene_6(keys)
    elif scene == 7:
        scene_7(keys)



    pygame.display.flip()
    clock.tick(30)
    