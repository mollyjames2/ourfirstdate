import pygame
import sys
import random
from PIL import Image
import textwrap
import os
import asyncio


### INITIALISATION
# Pygame Initialization
pygame.init()
pygame.font.init()

if getattr(sys, "frozen", False):
    # If running as a bundled executable
    BASE_PATH = sys._MEIPASS
else:
    # If running as a script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

scene = 0
actionable = False  # Whether the actionable game has started

# CONSTANTS
WIDTH, HEIGHT = 800, 600
SPRITE_SCALER = 1.1
SPRITE_WIDTH, SPRITE_HEIGHT = 50 * SPRITE_SCALER, 70 * SPRITE_SCALER
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)  # for the beers
FOLLOW_DISTANCE = 40
DELAY_FRAMES = 3
MOVEMENT_SPEED = 8
FPS = 30

try:
    font_path = os.path.join(BASE_PATH, "assets/fonts/Monospace.ttf")
    font_large = pygame.font.Font(font_path, 50)
    font_small = pygame.font.Font(font_path, 25)
except FileNotFoundError:
    print("Error: Font file not found. Falling back to default fonts.")
    font_large = pygame.font.SysFont("monospace", 50)
    font_small = pygame.font.SysFont("monospace", 25)


font = font_small

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("First Date Adventure")
clock = pygame.time.Clock()

# Key State Initialization
key_states = {"up_pressed": False, "down_pressed": False}


###################################################


# --------------------SPRITES----------------------#
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
sprites.load("pub", "assets/sprites/LHA.png", (150, 150))
sprites.load("bar", "assets/sprites/bar.png", (150, 150))
sprites.load("table", "assets/sprites/table.png", (200, 100))
sprites.load("door", "assets/sprites/door.png", (100, 100))
sprites.load("house", "assets/sprites/house.png", (200, 150))
sprites.load("maggie", "assets/sprites/mag.png", (SPRITE_WIDTH, SPRITE_HEIGHT))
sprites.load("mike", "assets/sprites/mike.png", (SPRITE_WIDTH, SPRITE_HEIGHT))
sprites.load("sofa", "assets/sprites/sofa.png", (200, 100))
sprites.load("heart", "assets/sprites/heart.png", (SPRITE_WIDTH, SPRITE_HEIGHT))


# Load the bike sprite with aspect ratio scaling
sprites.load_with_aspect_ratio("bike", "assets/sprites/bike.png", SPRITE_HEIGHT)


# call the sprites
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

# Set starting positions for sprites in the first scene they are visible
sam_pos = pygame.Vector2(100, HEIGHT // 2 - 25)  # Use a vector for the sam's position
molly_pos = pygame.Vector2(WIDTH // 4 - SPRITE_WIDTH // 2, -SPRITE_HEIGHT)  # molly starts off-screen, centered horizontally

# Calculate bike position below sam
bike_pos = pygame.Vector2(
    sam_pos.x - 7, sam_pos.y + SPRITE_HEIGHT // 2  # Align horizontally with the player  # A sprite height below the player
)


# Function to draw sprites
def draw_sprite(sprite, position):
    """Draw a sprite at a given position."""
    screen.blit(sprite, position)


# --------------------GRAPHICS----------------------#
# Function to load and display a GIF prior to actionable gameplay
async def display_gif(screen, gif_path, duration=3000, center=None):
    """
    Displays an animated GIF on the screen for a specified duration asynchronously.

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
        frame_surface = pygame.image.fromstring(gif.tobytes(), gif.size, gif.mode).convert_alpha()
        frames.append(frame_surface)
        frame_durations.append(gif.info.get("duration", 400))  # Default 400ms per frame

    current_frame = 0
    start_time = pygame.time.get_ticks()

    # Set center to screen center if not specified
    if center is None:
        center = (screen.get_width() // 2, screen.get_height() // 2)

    # Display the animated GIF asynchronously
    while pygame.time.get_ticks() - start_time < duration:
        # Determine the current frame to display
        elapsed_time = pygame.time.get_ticks() - start_time
        total_duration = sum(frame_durations[: current_frame + 1])

        if elapsed_time > total_duration:
            current_frame = (current_frame + 1) % len(frames)

        # Display the current frame
        screen.fill((0, 0, 0))  # Clear the screen
        gif_rect = frames[current_frame].get_rect(center=center)
        screen.blit(frames[current_frame], gif_rect)
        pygame.display.flip()

        # Handle events to allow quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Pause asynchronously to allow other tasks to run
        await asyncio.sleep(frame_durations[current_frame] / 1000.0)


# Construct the full path to the GIF
gif_path = os.path.join(BASE_PATH, "assets/GIFs/LHA.gif")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Asynchronous Transition Function
async def scene_transition():
    """
    Animated transition between scenes with a fade-in effect.
    """
    for alpha in range(0, 256, 10):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.033)  # Approximately 30 FPS (1/30 seconds per frame)

    # Clear screen at the end of the transition
    screen.fill(BLACK)
    pygame.display.flip()
    await asyncio.sleep(0.033)  # Small delay to ensure smooth transition


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
    for i, beer in enumerate(beers):
        # Draw beer outline
        pygame.draw.rect(screen, BLACK, beer, 2)  # Black outline
        state = beer_states[i]

        # Draw orange content and white line
        if state == 0:  # Full beer
            orange_top = beer.y
            orange_height = beer.height
            pygame.draw.rect(screen, ORANGE, beer.inflate(-2, -2))
            pygame.draw.rect(screen, WHITE, (beer.x + 2, beer.y + 2, beer.width - 4, 5))  # White line at the top
        elif state == 1:  # 2/3 full beer
            orange_top = beer.y + beer.height // 3
            orange_height = beer.height * 2 // 3
            pygame.draw.rect(screen, ORANGE, (beer.x + 2, orange_top, beer.width - 4, orange_height))
            pygame.draw.rect(screen, WHITE, (beer.x + 2, orange_top - 3, beer.width - 4, 5))  # White line just above orange
        elif state == 2:  # 1/3 full beer
            orange_top = beer.y + beer.height * 2 // 3
            orange_height = beer.height // 3
            pygame.draw.rect(screen, ORANGE, (beer.x + 2, orange_top, beer.width - 4, orange_height))
            pygame.draw.rect(screen, WHITE, (beer.x + 2, orange_top - 3, beer.width - 4, 5))  # White line just above orange
        elif state == 3:  # Empty beer
            orange_top = None  # No orange content
            orange_height = 0
            pygame.draw.rect(screen, BLACK, beer.inflate(-2, -2), 2)  # Thin black outline, no fill

        # Add and animate bubbles
        if orange_top is not None:  # Only beers with orange content have bubbles
            # Add new bubbles randomly within the orange part
            if random.random() < 0.2:  # Probability of adding a bubble
                x = random.randint(beer.x + 3, beer.x + beer.width - 3)
                y = random.randint(orange_top, orange_top + orange_height - 3)
                dx = random.choice([-1, 0, 1])  # Random horizontal drift
                bubbles[i].append([x, y, dx])  # Bubble has x, y, and horizontal drift

            # Move bubbles upward and horizontally, remove those that leave the orange part
            for bubble in bubbles[i]:
                bubble[0] += bubble[2]  # Apply horizontal drift
                bubble[1] -= 1  # Move upward
                # Keep bubbles within the beer width
                if bubble[0] < beer.x + 3 or bubble[0] > beer.x + beer.width - 3:
                    bubble[0] = max(beer.x + 3, min(bubble[0], beer.x + beer.width - 3))
            # Remove bubbles that leave the orange part
            bubbles[i] = [bubble for bubble in bubbles[i] if bubble[1] > orange_top]

            # Draw bubbles
            for x, y, _ in bubbles[i]:
                pygame.draw.circle(screen, WHITE, (x, y), 2)
        else:
            # Clear bubbles if the beer is empty
            bubbles[i] = []


beer_states = [1, 1, 1, 1, 1]  # All beers start as full


async def take_picture():
    """
    Handles the process of taking a picture:
    - Displays an instruction to press ENTER.
    - Waits for ENTER to be pressed.
    - Flashes the screen white.
    - Displays the snapshot image on a white background with a black scene.
    """
    # Display the instruction
    instruction = font_small.render("Press ENTER to take the picture!", True, WHITE)
    screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT - 200))
    pygame.display.flip()

    # Wait for the ENTER key asynchronously
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
                await asyncio.sleep(0.2)  # Wait asynchronously
                waiting = False  # Exit the loop

        await asyncio.sleep(0)  # Allow other tasks to run

    # Display the scene with a black background
    screen.fill(BLACK)

    # Create the white background for the picture
    box_width, box_height = int(WIDTH * 0.6), int(HEIGHT * 0.6)
    box_x, box_y = (WIDTH - box_width) // 2, (HEIGHT - box_height) // 2 - 50
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))

    # Load and display the snapshot image
    border_thickness = 10
    picture_x, picture_y = box_x + border_thickness, box_y + border_thickness
    picture_width, picture_height = box_width - 2 * border_thickness, box_height - 2 * border_thickness

    # Construct the full path to the snapshot image
    snapshot_path = os.path.join(BASE_PATH, "assets/pictures/snapshot.png")

    snapshot_image = pygame.image.load(snapshot_path)
    snapshot_image = pygame.transform.scale(snapshot_image, (picture_width, picture_height))
    screen.blit(snapshot_image, (picture_x, picture_y))
    pygame.display.flip()  # Update the screen to show the image


# --------------------DIALOGUE----------------------#


# Function to draw the dialog box using a Surface
async def text_box(*lines):
    """
    Displays a dialog box with text, supports scrolling through multiple boxes.
    Args:
        *lines: Variable number of lines to display in the dialog box.
    """
    line_height = 40
    max_line_width = WIDTH - 140
    box_x, box_y = 50, HEIGHT - 150
    box_width, box_height = WIDTH - 100, 100

    # Create a Surface for the dialog box
    dialog_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)

    # Preprocess lines to handle wrapping and box splitting
    processed_boxes = []
    for line in lines:
        wrapped = textwrap.wrap(line, width=max_line_width // font.size("A")[0])
        for i in range(0, len(wrapped), 2):
            processed_boxes.append(wrapped[i : i + 2])

    # Scrolling variables
    current_box_index = 0
    box_active = True

    while box_active:
        # Clear the dialog surface
        dialog_surface.fill((0, 0, 0, 0))  # Transparent background

        # Draw the box on the surface
        pygame.draw.rect(dialog_surface, WHITE, (0, 0, box_width, box_height))
        pygame.draw.rect(dialog_surface, BLACK, (10, 10, box_width - 20, box_height - 20))

        # Render and display the current box's lines
        if current_box_index < len(processed_boxes):
            current_box = processed_boxes[current_box_index]
            for i, line in enumerate(current_box):
                text_surface = font.render(line, True, WHITE)
                dialog_surface.blit(text_surface, (20, 20 + i * line_height))

        # Draw the down arrow if there are more boxes to display
        down_arrow = font.render("\u25BC", True, WHITE)
        dialog_surface.blit(down_arrow, (box_width - 40, box_height - 35))

        # Blit the dialog surface onto the main screen
        screen.blit(dialog_surface, (box_x, box_y))
        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    if current_box_index + 1 < len(processed_boxes):
                        current_box_index += 1
                    else:
                        box_active = False
                elif event.key == pygame.K_UP and current_box_index > 0:
                    current_box_index -= 1

        # Yield control to the event loop
        await asyncio.sleep(0)

    # Clear the dialog box by not blitting the surface after the loop ends
    pygame.display.flip()


dialog_triggered = False  # Add a flag to control dialog triggering


async def draw_fireworks(fireworks):
    """
    Draw and update fireworks on the screen asynchronously with faster and more explosive effects.
    Args:
        fireworks (list): List of active fireworks, each with position, state, and particles.
    """
    for firework in fireworks[:]:
        if firework["state"] == "ascending":
            # Update the firework's position
            firework["position"][1] -= firework["speed"]  # Move upward faster
            x, y = firework["position"]
            pygame.draw.circle(screen, firework["color"], (int(x), int(y)), 4)  # Larger firework dot

            # Transition to explosion if it reaches a certain height
            if firework["position"][1] <= firework["explosion_height"]:
                firework["state"] = "exploding"
                firework["particles"] = [
                    {
                        "position": firework["position"][:],
                        "velocity": [
                            random.uniform(-8, 8),  # Wider spread
                            random.uniform(-8, 8),
                        ],
                        "lifetime": random.randint(20, 40),  # Shorter particle lifetime for quicker effects
                    }
                    for _ in range(60)  # Increased particle count
                ]

        elif firework["state"] == "exploding":
            for particle in firework["particles"][:]:
                particle["position"][0] += particle["velocity"][0]
                particle["position"][1] += particle["velocity"][1]
                particle["lifetime"] -= 1

                x, y = particle["position"]
                pygame.draw.circle(screen, firework["color"], (int(x), int(y)), 3)  # Smaller particle dots

            # Remove expired particles
            firework["particles"] = [particle for particle in firework["particles"] if particle["lifetime"] > 0]

            # Remove firework if all particles are gone
            if not firework["particles"]:
                fireworks.remove(firework)

    # Yield control to the asyncio loop
    await asyncio.sleep(0)


# --------------------MOVEMENT----------------------#
def move_sam(keys, sam_pos):
    """
    Update Sam's position based on key inputs.

    Args:
        keys: The current state of the keyboard keys.
        sam_pos: The position of Sam as a Vector2.
    """
    if keys[pygame.K_UP]:
        sam_pos.y -= 5
    if keys[pygame.K_DOWN]:
        sam_pos.y += 5
    if keys[pygame.K_LEFT]:
        sam_pos.x -= 5
    if keys[pygame.K_RIGHT]:
        sam_pos.x += 5


def follow_sam(sam_pos, molly_pos, follow_distance=40, follow_speed=3):
    """
    Makes Molly follow Sam with smoother movement.

    Args:
        sam_pos (pygame.Vector2): The position of Sam as a Vector2.
        molly_pos (pygame.Vector2): The position of Molly as a Vector2.
        follow_distance (int): The distance Molly maintains from Sam.
        follow_speed (int): The speed at which Molly moves to follow Sam.
    """
    # Horizontal follow logic with a buffer zone
    if abs(molly_pos.x - (sam_pos.x - follow_distance)) > 5:  # Add a small threshold
        if molly_pos.x < sam_pos.x - follow_distance:
            molly_pos.x += follow_speed
        elif molly_pos.x > sam_pos.x - follow_distance:
            molly_pos.x -= follow_speed

    # Vertical follow logic with a buffer zone
    if abs(molly_pos.y - sam_pos.y) > 5:  # Add a small threshold
        if molly_pos.y < sam_pos.y:
            molly_pos.y += follow_speed
        elif molly_pos.y > sam_pos.y:
            molly_pos.y -= follow_speed


async def apply_idle_sway_with_follow(
    sam_pos, molly_pos, sway_timer, sway_direction, sway_magnitude, sway_frequency, keys, follow_speed=2.5, max_sway=5
):
    """
    Handles idle sway for Sam and Molly with directional veering based on key presses.

    Args:
        sam_pos (pygame.Vector2): Position of Sam.
        molly_pos (pygame.Vector2): Position of Molly.
        sway_timer (int): Timer for swaying effect.
        sway_direction (int): Direction of sway (-1 or 1).
        sway_magnitude (float): Magnitude of the sway effect.
        sway_frequency (int): Frequency of sway direction changes.
        keys (list): Key states from pygame.key.get_pressed().
        follow_speed (float): Speed at which Molly follows Sam.
        max_sway (float): Maximum magnitude for directional sway.

    Returns:
        (pygame.Vector2, pygame.Vector2, int, int): Updated positions and sway state.
    """
    # Update sway timer and direction
    sway_timer += 1
    if sway_timer > sway_frequency:
        sway_timer = 0
        sway_direction *= -1

    sway = sway_direction * sway_magnitude

    # Handle directional movement for Sam
    if keys[pygame.K_UP]:  # Pressing UP moves Sam DOWN
        sam_pos.y += follow_speed  # Invert: DOWN instead of UP
        sam_pos.x -= sway  # Adjust sway for realism
    if keys[pygame.K_DOWN]:  # Pressing DOWN moves Sam UP
        sam_pos.y -= follow_speed  # Invert: UP instead of DOWN
        sam_pos.x += sway
    if keys[pygame.K_LEFT]:  # Pressing LEFT moves Sam RIGHT
        sam_pos.x += follow_speed  # Invert: RIGHT instead of LEFT
    if keys[pygame.K_RIGHT]:  # Pressing RIGHT moves Sam LEFT
        sam_pos.x -= follow_speed  # Invert: LEFT instead of RIGHT

    # Idle sway if no keys are pressed
    if not any(keys[key] for key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]):
        sam_pos.x += sway

    # Molly follows Sam
    dx = sam_pos.x - molly_pos.x
    dy = sam_pos.y - molly_pos.y
    distance = (dx**2 + dy**2) ** 0.5
    if distance > 40:  # Maintain a follow distance of 40 pixels
        molly_pos.x += follow_speed * (dx / distance)
        molly_pos.y += follow_speed * (dy / distance)

    await asyncio.sleep(0)  # Allow other tasks to run
    return sam_pos, molly_pos, sway_timer, sway_direction


#####################################################################

# -------------------------MINIGAMES---------------------------------#


async def minigame_scene_3():
    global beers, states, bubbles, actionable

    # Show instructions screen
    screen.fill(BLACK)
    instructions = font_small.render("Match the keys to drink the beers!", True, WHITE)
    prompt = font_small.render("Press ENTER to start", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 10))
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
        await asyncio.sleep(0)  # Yield control to the event loop

    # Initialize game state
    target_key = None
    prompt_time = pygame.time.get_ticks()
    sobriety_bar = 100  # Full at start
    beer_index = 0  # Current beer being consumed
    state_index = 0  # Current state of the beer (0: full, 1: two-thirds full, 2: one-third full, 3: empty)
    reaction_time_limit = 2.0  # Seconds to press the correct key

    beer_states = [0, 0, 0, 0, 0]

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
        screen.blit(table, (table_rect.x, table_rect.y))

        # Draw beers and the sobriety bar
        draw_beers(beers, beer_states, bubbles)
        pygame.draw.rect(screen, (0, 255, 0), (50, 20, sobriety_bar * 3, 20))
        sobriety_text = font_small.render("Sobriety", True, WHITE)
        screen.blit(sobriety_text, (50, 50))

        # Draw the key prompt
        prompt_text = font_small.render(f"Press: {pygame.key.name(target_key)}", True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 50))
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
                        # Last sip of the current beer
                        beer_states[beer_index] = 3  # Empty the current beer
                        bubbles[beer_index] = []  # Clear bubbles for the current beer
                        beer_index += 1  # Move to the next beer
                        state_index = 0  # Reset state for the next beer
                    else:
                        state_index += 1
                    target_key = None
                    sobriety_bar = max(0, sobriety_bar - 7)  # Reduce sobriety bar
                elif event.key != target_key:
                    sobriety_bar = max(0, sobriety_bar - 5)  # Incorrect key press reduces the bar

        await asyncio.sleep(0)  # Yield control to the event loop

    # Ensure all beers are empty before displaying the message
    for i in range(len(beer_states)):
        beer_states[i] = 3
    bubbles = [[] for _ in range(len(beers))]

    # Final display update for the last sip
    screen.fill(BLACK)
    screen.blit(table, (table_rect.x, table_rect.y))
    draw_beers(beers, beer_states, bubbles)
    pygame.draw.rect(screen, (0, 255, 0), (50, 20, sobriety_bar * 3, 20))
    sobriety_text = font_small.render("Sobriety", True, WHITE)
    screen.blit(sobriety_text, (50, 50))
    pygame.display.flip()

    # Show congratulations message
    await asyncio.sleep(0.5)  # Pause briefly for the final update
    await text_box("Congratulations! You finished all the beers!")
    actionable = True


# -----------------------------------------------------------------------


async def minigame_scene_5():
    global sam_pos, molly_pos, actionable, scene

    # Instructions screen
    screen.fill(BLACK)
    instruction_lines = ["Get to the house!", "Arrow keys to move."]
    for i, line in enumerate(instruction_lines):
        rendered_line = font_small.render(line, True, WHITE)
        screen.blit(rendered_line, (WIDTH // 2 - rendered_line.get_width() // 2, HEIGHT // 2 - 60 + i * 30))
    prompt = font_small.render("Press ENTER to start", True, WHITE)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    # Wait for ENTER to start asynchronously
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
        await asyncio.sleep(0)  # Allow the event loop to continue processing

    # Initialize sway parameters
    sway_timer = 0
    sway_direction = 1
    sway_magnitude = 0.5
    sway_frequency = 100

    # Game loop
    while True:
        screen.fill(BLACK)

        # Draw house and pub sprites
        draw_sprite(house, house_rect)
        draw_sprite(pub, pub_rect)

        # Draw Sam and Molly
        draw_sprite(sam, (sam_pos.x, sam_pos.y))
        draw_sprite(molly, (molly_pos.x, molly_pos.y))

        # Apply sway and following behavior
        keys = pygame.key.get_pressed()
        sam_pos, molly_pos, sway_timer, sway_direction = await apply_idle_sway_with_follow(
            sam_pos, molly_pos, sway_timer, sway_direction, sway_magnitude, sway_frequency, keys
        )

        # Check collision with the house
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if sam_rect.colliderect(house_rect):
            break

        pygame.display.flip()
        await asyncio.sleep(0)  # Allow other tasks to run


# ------------------------------------------------------------------
async def minigame_scene_6():
    async def show_instructions():
        # Instruction screen
        screen.fill(BLACK)
        instructions = [
            "Stop the heart on the red line",
            "The heart moves left and right automatically.",
            "Press SPACE to stop it.",
            "",
            "Press ENTER to start.",
        ]
        for i, line in enumerate(instructions):
            rendered_line = font_small.render(line, True, WHITE)
            screen.blit(rendered_line, (WIDTH // 2 - rendered_line.get_width() // 2, HEIGHT // 2 - 60 + i * 30))
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
            await asyncio.sleep(0)  # Allow event loop to continue

    # Show instructions once
    if not hasattr(minigame_scene_6, "instructions_shown"):
        await show_instructions()
        minigame_scene_6.instructions_shown = True

    # Mini-game setup
    heart_pos_x = WIDTH // 2
    heart_speed = 13
    heart_direction = 1
    heart_size = (80, 80)  # Larger heart size
    heart_image = pygame.image.load("assets/sprites/heart.png")  # Replace with your heart image path
    heart_image = pygame.transform.scale(heart_image, heart_size)

    # Define the target area for the heart
    target_area_width = 100  # Width of the target area
    target_area_x_start = WIDTH // 2 - target_area_width // 2
    target_area_x_end = WIDTH // 2 + target_area_width // 2
    target_area_y = HEIGHT // 2 + heart_size[1] // 2  # Align line with the center of the heart

    while True:  # Restart mini-game loop if missed
        success = False

        # Mini-game loop
        while not success:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Check if the heart is within the target area
                    if target_area_x_start <= heart_pos_x <= target_area_x_end:
                        success = True
                    break

            # Update heart position
            heart_pos_x += heart_speed * heart_direction

            # Reverse direction if the heart hits the screen edges
            if heart_pos_x <= 0 or heart_pos_x >= WIDTH - heart_size[0]:
                heart_direction *= -1

            # Clear the screen
            screen.fill(BLACK)

            # Draw the red target line
            pygame.draw.rect(
                screen,
                (255, 0, 0),  # Red
                (target_area_x_start, target_area_y, target_area_x_end - target_area_x_start, 10),  # Larger line
            )

            # Draw the heart
            screen.blit(heart_image, (heart_pos_x, target_area_y - heart_size[1] // 2))  # Center heart over the line

            pygame.display.flip()
            await asyncio.sleep(0)  # Allow event loop to process

        # Post-mini-game outcome
        if success:
            await text_box("Sam and Molly share their first kiss!")
            break
        else:
            await text_box("Missed! Let's try again!")


###########################################################################################
async def game_completed():
    """
    End the game with a faster and more explosive fireworks animation, display a thank-you message, and fade to black.
    """
    fireworks = []  # Active fireworks
    colors = [(128, 0, 128), (0, 255, 0), (0, 0, 255), (255, 255, 255)]  # Purple, green, blue, white

    # Fireworks animation
    fireworks_duration = 5  # Display fireworks for 3 seconds
    start_time = pygame.time.get_ticks()
    while (pygame.time.get_ticks() - start_time) / 1000 < fireworks_duration:
        screen.fill(BLACK)

        # Launch new fireworks more frequently
        if random.random() < 0.35:  # Higher frequency of fireworks
            fireworks.append(
                {
                    "position": [random.randint(int(100 * SPRITE_SCALER), int(WIDTH - 100 * SPRITE_SCALER)), HEIGHT],
                    "speed": random.uniform(10 * SPRITE_SCALER, 15 * SPRITE_SCALER),  # Faster ascent
                    "explosion_height": random.randint(int(100 * SPRITE_SCALER), int(HEIGHT // 2)),
                    "color": random.choice(colors),
                    "state": "ascending",
                    "particles": [],
                }
            )

        # Draw and update fireworks
        await draw_fireworks(fireworks)
        pygame.display.flip()
        await asyncio.sleep(0.016)  # ~60 FPS

    # Proceed to thank-you message
    screen.fill(BLACK)
    await asyncio.sleep(0.5)  # Brief pause before showing the picture

    # Display the picture
    box_width, box_height = int(WIDTH * 0.6), int(HEIGHT * 0.6)
    box_x, box_y = (WIDTH - box_width) // 2, (HEIGHT - box_height) // 2 - 50
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height))

    border_thickness = 10
    picture_x, picture_y = box_x + border_thickness, box_y + border_thickness
    picture_width, picture_height = box_width - 2 * border_thickness, box_height - 2 * border_thickness

    snapshot_path = os.path.join(BASE_PATH, "assets/pictures/us.png")
    snapshot_image = pygame.image.load(snapshot_path)
    snapshot_image = pygame.transform.scale(snapshot_image, (picture_width, picture_height))
    screen.blit(snapshot_image, (picture_x, picture_y))
    pygame.display.flip()
    await asyncio.sleep(0.2)  # Display the picture for 2 seconds

    # Display the text box
    await text_box(
        "And the rest was history!",
        "Thank you for a wonderful year, my gorgeous girl!",
        "I can't wait for many more!",
        "I love you so much!",
    )

    # Happy Anniversary screen
    screen.fill(BLACK)
    message = font_large.render("Happy Anniversary!", True, WHITE)
    screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - message.get_height() // 2))
    pygame.display.flip()
    await asyncio.sleep(2)

    # Fade to black
    for alpha in range(0, 256, 10):
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.03)

    # End the game
    pygame.quit()
    sys.exit()


###############################################################################################
#                                    SCENES                                                   #
###############################################################################################


# ----------------------------------SCENE 0 -----------------------------#
# Scene 0: Opening Screen
async def scene_0(keys, event):
    global scene
    screen.fill(BLACK)

    # Render text
    title_text = font_large.render("Where it all began", True, WHITE)
    subtitle_text = font_small.render("Sam and Molly's first date", True, WHITE)
    prompt_text = font_small.render("Press ENTER to start", True, WHITE)

    # Center text on the screen
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 50))

    # Handle key press for scene transition
    if event and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        await asyncio.sleep(0.2)  # Optional delay for smoother transition
        scene = 1


# ---------------------------------------------------------------------------------------------------------#


# ----------------------------------SCENE 1-----------------------------#
# Scene 1: Cycling to the pub
async def scene_1(keys):
    global scene, player, partner, player_pos, partner_pos, text_state, actionable

    if not hasattr(scene_1, "interacted"):
        scene_1.interacted = False
    if not hasattr(scene_1, "met_molly"):
        scene_1.met_molly = False
    if not hasattr(scene_1, "pub_reached"):
        scene_1.pub_reached = False
    scene_1.molly_near_sam = False  # Track if Molly has caught up to Sam

    screen.fill(BLACK)

    # Get the sprites for the scene
    sam = sprites.get("sam")
    molly = sprites.get("molly")
    bike = sprites.get("bike")
    pub = sprites.get("pub")

    # Create rectangles for interactions
    pub_rect = pub.get_rect(midright=(WIDTH - 40, HEIGHT // 2))
    sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)

    # Draw the pub
    screen.blit(pub, (pub_rect.x, pub_rect.y))

    # Draw the player sprite
    draw_sprite(sam, (sam_pos.x, sam_pos.y))

    # Draw the partner sprite
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Draw Sam's bike
    draw_sprite(bike, (bike_pos.x, bike_pos.y))

    if not actionable and not scene_1.pub_reached:
        await text_box("USE THE DOWN ARROW TO SCROLL THROUGH THE TEXT", "Oh look at the time, it's nearly 7pm!", "Use the arrow keys to cycle to the pub for your date.")
        actionable = True
        scene_1.pub_reached = True
    else:
        move_sam(keys, sam_pos)

        # Update bike's position relative to Sam
        bike_pos.x = sam_pos.x - 7
        bike_pos.y = sam_pos.y + SPRITE_HEIGHT // 2

        # Molly moves down to meet Sam
        if sam_pos.x > WIDTH - 300 and not scene_1.met_molly:
            molly_pos.y += 5

            if molly_pos.y >= HEIGHT // 2 - 25:
                scene_1.met_molly = True
                await text_box("Is that Molly?", "Maybe I should go and ask if she wants to walk with me?")
                actionable = False

        if scene_1.met_molly and not scene_1.interacted:
            # Sam and Molly interaction
            sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, molly.get_width(), molly.get_height())
            molly_rect = pygame.Rect(molly_pos.x, molly_pos.y, sam.get_width(), sam.get_height())

            if sam_rect.colliderect(molly_rect):
                actionable = False
                exclamation = font_small.render("!", True, WHITE)
                screen.blit(exclamation, (sam_pos.x + 15, sam_pos.y - 30))
                screen.blit(exclamation, (molly_pos.x + 15, molly_pos.y - 30))

                if not scene_1.interacted:
                    await text_box(
                        "Sam: Molly, right?",
                        "Molly: Yep! You must be Sam!",
                        "Sam: Cool! Nice to meet you!",
                        "Want to walk together?",
                        "Molly: Yeah sure! I'll follow you!",
                    )
                    scene_1.interacted = True
                    actionable = True

        if scene_1.met_molly and scene_1.interacted:
            actionable = True

            # Smoothly make Molly follow Sam
            follow_sam(sam_pos, molly_pos)

            # Check if Molly is near Sam
            if molly_pos.distance_to(sam_pos) < 50:  # Proximity threshold
                scene_1.molly_near_sam = True
            else:
                scene_1.molly_near_sam = False

            # Transition to the next scene when player collides with the pub
            if sam_rect.colliderect(pub_rect) and scene_1.interacted and scene_1.molly_near_sam:
                actionable = False
                screen.fill(BLACK)

                # Display "You made it to the pub! Press ENTER to continue"
                dialogue_text = font_large.render("You made it to the pub!", True, WHITE)
                prompt_text = font_small.render("Press ENTER to continue", True, WHITE)

                screen.blit(dialogue_text, (WIDTH // 2 - dialogue_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 50))
                pygame.display.flip()

                # Wait for ENTER key to transition to Scene 2
                if keys[pygame.K_RETURN]:
                    await scene_transition()  # Trigger transition
                    scene = 2  # Move to Scene 2


# ---------------------------------------------------------------------------------------------------------#


# ----------------------------------SCENE 2-----------------------------#
# Scene 2: Going to the bar
async def scene_2(keys):
    global scene, sam, molly, bar, actionable, sam_pos, molly_pos

    # Initialize elements
    if not hasattr(scene_2, "initialized"):
        sam_pos = pygame.Vector2(100, HEIGHT // 2 - 25)  # Player starting position
        molly_pos = pygame.Vector2(50, HEIGHT // 2 - 25)  # Partner starting position
        actionable = False  # Disable gameplay during GIF display
        scene_2.initialized = True
        scene_2.gif_displayed = False
        scene_2.molly_near_sam = False  # Track if Molly has caught up to Sam

    # Display the animated GIF
    if not scene_2.gif_displayed:
        await display_gif(screen, gif_path, duration=2500)
        actionable = True
        scene_2.gif_displayed = True

    # Fill the screen with black
    screen.fill(BLACK)

    # Draw the bar sprite
    bar_rect = bar.get_rect(midtop=(WIDTH - 150, HEIGHT // 2 - 100))  # Adjusted to center vertically
    draw_sprite(bar, (bar_rect.x, bar_rect.y))

    # Render instructional text
    instruction_text = font_small.render("Walk to the bar", True, WHITE)
    screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, 20))  # Centered at the top

    # Draw the sam and molly sprites
    draw_sprite(sam, (sam_pos.x, sam_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Allow Sam movement
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)

        # Check if Molly is near Sam
        if molly_pos.distance_to(sam_pos) < 50:  # Proximity threshold
            scene_2.molly_near_sam = True
        else:
            scene_2.molly_near_sam = False

        # Check for interaction with the bar
        sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
        if sam_rect.colliderect(bar_rect) and scene_2.molly_near_sam:
            actionable = False  # Disable movement
            await text_box("Let's get some beers in, shall we?")

        # Transition to the next scene if interaction is complete
        if not actionable:
            await scene_transition()  # Trigger transition asynchronously
            scene = 3  # Move to Scene 3


# ---------------------------------------------------------------------------------------------------------#

# ----------------------------------SCENE 3-----------------------------#


async def scene_3(keys):
    global scene, sam, molly, actionable, sam_pos, molly_pos, scene3, beers, beer_states, bubbles, table, table_rect

    # Initialize elements
    if not hasattr(scene_3, "initialized"):
        sam_pos = pygame.Vector2(100, HEIGHT // 2)
        molly_pos = pygame.Vector2(200, HEIGHT // 2)
        actionable = True
        scene_3.game_played = False
        scene_3.initialized = True
        scene_3.molly_burped = False
        scene_3.molly_near_sam = False

    # Fill the screen with black
    screen.fill(BLACK)

    # Set positions for the door and table
    table_rect = table.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    door_rect = door.get_rect(midtop=(WIDTH - 75, 50))

    # Initialize the beers
    beers = [pygame.Rect(table_rect.x + 40 + i * 30, table_rect.y - 22, 20, 50) for i in range(5)]
    bubbles = [[] for _ in range(5)]  # List of bubbles for each beer

    # Draw table and door sprites
    draw_sprite(table, (table_rect.x, table_rect.y))
    draw_sprite(door, (door_rect.x, door_rect.y))

    # Draw beers on the table
    draw_beers(beers, beer_states, bubbles)

    # Draw player and partner sprites
    draw_sprite(sam, (sam_pos.x, sam_pos.y))  # Draw player sprite
    draw_sprite(molly, (molly_pos.x, molly_pos.y))  # Draw partner sprite

    # Movement logic
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)

        # Check if Molly is near Sam
        if molly_pos.distance_to(sam_pos) < 50:  # Proximity threshold
            scene_3.molly_near_sam = True
        else:
            scene_3.molly_near_sam = False

    # Interaction with table
    interaction_zone = table_rect.inflate(1, 1)  # Expand interaction zone by 1 pixel on all sides
    if (
        pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT).colliderect(interaction_zone)
        and not scene_3.game_played
        and scene_3.molly_near_sam
    ):
        actionable = False  # Disable movement during interaction
        await text_box("Dutch courage...?")
        await minigame_scene_3()  # Await the asynchronous mini-game function
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
        draw_beers(beers, beer_states, bubbles)
        draw_sprite(sam, (sam_pos.x, sam_pos.y))  # Draw sam sprite
        draw_sprite(molly, (molly_pos.x, molly_pos.y))  # Draw molly sprite
        pygame.display.flip()  # Ensure everything is rendered before dialog

        # Show the dialog box
        await text_box("Molly: BURRPPPP!!", "Sam: Fancy some fresh air?")
        scene_3.molly_burped = True
        actionable = True

    if scene_3.molly_burped:
        for i in range(len(beer_states)):
            beer_states[i] = 3  # All beers are empty
        for i in range(len(bubbles)):
            bubbles[i] = []  # Clear bubbles for each beer
        draw_beers(beers, beer_states, bubbles)

    # Interaction with door
    interaction_zone_door = door_rect.inflate(1, 1)  # Expand interaction zone for the door
    if pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT).colliderect(interaction_zone_door):
        actionable = False  # Disable movement during interaction

        # If the mini-game has been completed
        if scene_3.game_played:
            # Transition to Scene 4
            await text_box("Molly: Let's go outside!")
            await scene_transition()  # Trigger transition asynchronously
            scene = 4  # Move to Scene 4
        else:
            actionable = False
            # Show dialogue indicating the mini-game needs to be played first
            await text_box("Maybe we should have a drink first?")
            actionable = True  # Re-enable movement


# ---------------------------------------------------------------------------------------------------------#

# ----------------------------------SCENE 4------------------------------------------#


async def scene_4(keys):
    global sam_pos, molly_pos, actionable, scene

    # Initialize positions and elements
    if not hasattr(scene_4, "initialized"):
        # Initialize sam and molly's positions
        sam_pos = pygame.Vector2(-50, HEIGHT // 2 - 25)  # Start sam off-screen (left)
        molly_pos = pygame.Vector2(-150, HEIGHT // 2 - 25)  # Start molly off-screen (left)

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
    door_rect = door.get_rect(midtop=(WIDTH - 75, 50))  # Door at the top right

    # Draw door only if it's visible
    if scene_4.door_visible:
        draw_sprite(door, door_rect)

    # Automatic movement of characters into position
    if not scene_4.movement_complete:
        sam_pos.x += 5
        molly_pos.x += 5

        if sam_pos.x >= WIDTH // 2 + 50:
            molly_pos = pygame.Vector2(WIDTH // 2 - 100, HEIGHT // 2 - 25)  # Molly stops at center left
            sam_pos = pygame.Vector2(WIDTH // 2 + 50, HEIGHT // 2 - 25)  # Sam stops at center right
            scene_4.movement_complete = True  # Movement complete, proceed with dialogue
            actionable = False

    # Draw sam and molly sprites
    draw_sprite(sam, (sam_pos.x, sam_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Dialogue progression
    if scene_4.movement_complete and not scene_4.choose_bird:
        await text_box(
            "Sam: Hey, what's your favourite bird?",
            "Molly: That's a hard question!",
            "I like loads of different birds!",
            "Which is your favourite?",
        )
        scene_4.choose_bird = True

    if scene_4.choose_bird and not scene_4.molly_opinion_done:
        choice_text = font_small.render("Press 1 for Seagull or 2 for Pigeon", True, WHITE)
        screen.blit(choice_text, (WIDTH // 2 - choice_text.get_width() // 2, HEIGHT - 150))

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
            if scene_4.selected_choice == "seagull":
                await text_box("Molly: Well, they're European Herring gulls", "actually!")
                scene_4.mollys_opinion = True
            elif scene_4.selected_choice == "pigeon":
                await text_box(
                    "Molly: Pigeons are great! I hope to hear you defending their valiant war efforts to a woman that totally didn't realise what she was getting herself into one day!"
                )
                scene_4.mollys_opinion = True

        if scene_4.mollys_opinion and not scene_4.molly_opinion_done:
            await text_box(f"Molly: Want to hear my thoughts on {scene_4.not_selected_choice}s?", "Sam: Sure!")
            if scene_4.not_selected_choice == "seagull":
                await text_box("Molly: Well, they're European Herring gulls", "actually!")
                scene_4.molly_opinion_done = True
            elif scene_4.not_selected_choice == "pigeon":
                await text_box(
                    "Molly: Pigeons are great! I hope to hear you defending their valiant war efforts to a woman that totally didn't realise what she was getting herself into one day!"
                )
                scene_4.molly_opinion_done = True

        if scene_4.molly_opinion_done and not scene_4.image_displayed:  # Take a photo
            await text_box("Molly: Hey, let's take a picture")
            await take_picture()  # Await the asynchronous take_picture function
            scene_4.image_displayed = True  # Mark that the picture has been displayed
            scene_4.door_visible = False  # Hide the door while showing the picture

        if scene_4.image_displayed and not scene_4.pic_taken:  # After the picture
            await text_box("Molly: Aww, our first picture!")
            scene_4.pic_taken = True

        if scene_4.pic_taken:  # Proceed to the next dialogue
            # Fill the screen with black
            screen.fill(BLACK)
            scene_4.door_visible = True

            # Redraw sam and molly sprites
            draw_sprite(sam, (sam_pos.x, sam_pos.y))
            draw_sprite(molly, (molly_pos.x, molly_pos.y))
            draw_sprite(door, (door_rect.x, door_rect.y))

            await text_box(
                "Molly: Hey, you fancy coming back to mine?",
                "Sam: That would be nice!",
                "Molly: Great! Let's go then! I don't live too far from here!",
            )
            actionable = True

    # Interaction with door (with buffer zone)
    door_buffer = door_rect.inflate(0.1, 0.1)  # Expand the door's interaction zone slightly
    if sam_pos.x >= door_buffer.x and sam_pos.x <= door_buffer.x + door_buffer.width:
        actionable = False
        await text_box("Molly: Just checking...", "you're alright with dogs yeah?!")
        await scene_transition()  # Await the asynchronous transition
        scene = 5

    # Movement logic
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)


# ---------------------------------------------------------------------------------------------------------#

# ----------------------------------SCENE 5------------------------------------------#


async def scene_5(keys):
    global sam_pos, molly_pos, actionable, scene, house_rect, pub_rect

    # Initialize elements and positions
    if not hasattr(scene_5, "initialized"):
        actionable = False
        scene_5.dialogue_started = False
        scene_5.minigame_launched = False
        scene_5.sway_timer = 0
        scene_5.sway_direction = 1
        scene_5.initialized = True

        # Set positions
        sam_pos = pygame.Vector2(WIDTH - 200, HEIGHT // 2 - 10)
        molly_pos = pygame.Vector2(WIDTH - 250, HEIGHT // 2 - 10)
        pub_rect = pub.get_rect(midright=(WIDTH - 40, HEIGHT // 2))
        house_rect = house.get_rect(midleft=(40, HEIGHT // 5))

    # Fill screen
    screen.fill(BLACK)

    # Draw sprites
    draw_sprite(pub, pub_rect)
    draw_sprite(house, house_rect)
    draw_sprite(sam, (sam_pos.x, sam_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))

    # Initial dialogue
    if not scene_5.dialogue_started:
        await text_box("Molly: Ossh, that was a lot of pints.", "The walk home will be interesting!")
        scene_5.dialogue_started = True
        actionable = True

    # Launch mini-game
    if scene_5.dialogue_started and not scene_5.minigame_launched:
        await minigame_scene_5()
        scene_5.minigame_launched = True
        actionable = False

    # Post-mini-game transition
    if scene_5.minigame_launched:
        await text_box("Molly: This is my place, come on in!", "Sam: Thanks!")
        await scene_transition()
        scene = 6


# ---------------------------------------------------------------------------------------------------------#

# ----------------------------------SCENE 6------------------------------------------#


async def scene_6(keys):
    global sam_pos, molly_pos, actionable, scene

    # Initialize elements
    if not hasattr(scene_6, "initialized"):
        actionable = True

        # Initialize sprite positions
        door_rect = door.get_rect(midtop=(WIDTH - int(75 * SPRITE_SCALER), int(50 * SPRITE_SCALER)))
        sofa_rect = sofa.get_rect(center=(WIDTH // 2, HEIGHT // 5))
        scene_6.door_rect = door_rect
        scene_6.sofa_rect = sofa_rect

        scene_6.maggie_rect = maggie.get_rect(center=(WIDTH // 4, HEIGHT // 2 + 10))
        scene_6.mike_rect = mike.get_rect(center=(3 * WIDTH // 4, HEIGHT // 2 + 10))

        sam_pos = pygame.Vector2(door_rect.centerx - SPRITE_WIDTH // 2, door_rect.bottom - 20)
        molly_pos = pygame.Vector2(sam_pos.x + SPRITE_WIDTH - 65, sam_pos.y - 30)
        scene_6.maggie_pos = pygame.Vector2(scene_6.maggie_rect.x, scene_6.maggie_rect.y)
        scene_6.mike_pos = pygame.Vector2(scene_6.mike_rect.x, scene_6.mike_rect.y)

        scene_6.sam_moved = False
        scene_6.maggie_interacted = False
        scene_6.mike_interacted = False
        scene_6.returning = False
        scene_6.maggie_exclamation = False
        scene_6.sofa_unlocked = False
        scene_6.initialized = True

    # Fill the screen with a background color (e.g., black)
    screen.fill(BLACK)

    # Draw sprites
    draw_sprite(door, scene_6.door_rect)
    draw_sprite(sofa, scene_6.sofa_rect)
    draw_sprite(maggie, (scene_6.maggie_pos.x, scene_6.maggie_pos.y))
    draw_sprite(mike, (scene_6.mike_pos.x, scene_6.mike_pos.y))
    draw_sprite(molly, (molly_pos.x, molly_pos.y))
    draw_sprite(sam, (sam_pos.x, sam_pos.y))

    # Draw exclamation mark above Maggie if required
    if scene_6.maggie_exclamation:
        exclamation = font_small.render("!", True, WHITE)
        screen.blit(exclamation, (scene_6.maggie_pos.x + 10, scene_6.maggie_pos.y - 20))

    # Handle movement logic for Sam and Molly
    if actionable:
        move_sam(keys, sam_pos)
        follow_sam(sam_pos, molly_pos)

    # Handle Maggie's movement toward Sam
    if not scene_6.maggie_interacted:
        maggie_speed = 2
        dx = sam_pos.x - scene_6.maggie_pos.x
        dy = sam_pos.y - scene_6.maggie_pos.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 10:  # Keep moving until close
            scene_6.maggie_pos.x += maggie_speed * (dx / distance)
            scene_6.maggie_pos.y += maggie_speed * (dy / distance)

    # Check interactions
    sam_rect = pygame.Rect(sam_pos.x, sam_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
    maggie_rect = pygame.Rect(scene_6.maggie_pos.x, scene_6.maggie_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)
    mike_rect = pygame.Rect(scene_6.mike_pos.x, scene_6.mike_pos.y, SPRITE_WIDTH, SPRITE_HEIGHT)

    # Interaction with Maggie
    if actionable and sam_rect.colliderect(maggie_rect) and not scene_6.maggie_interacted:
        actionable = False
        await text_box("Sam: Woah! Why is her head so massive?!", "Maggie: Heyyyyy Sam! Are you my new best friend?")
        scene_6.maggie_interacted = True
        scene_6.returning = True
        actionable = True

    # Return Maggie to her original position
    if scene_6.returning:
        maggie_speed = 2
        original_x, original_y = scene_6.maggie_rect.x, scene_6.maggie_rect.y
        dx = original_x - scene_6.maggie_pos.x
        dy = original_y - scene_6.maggie_pos.y
        distance = (dx**2 + dy**2) ** 0.5

        if distance > 2:
            scene_6.maggie_pos.x += maggie_speed * (dx / distance)
            scene_6.maggie_pos.y += maggie_speed * (dy / distance)
        else:
            scene_6.returning = False

    # Interaction with Mike
    if actionable and sam_rect.colliderect(mike_rect) and scene_6.maggie_interacted and not scene_6.mike_interacted:
        actionable = False
        await text_box("Mike: Ahh my love, my life!", "Sam: Your cat's...French?!", "Molly: Yeaaahh.. I think it's weird too!")
        scene_6.mike_interacted = True
        scene_6.maggie_exclamation = True
        actionable = True

    # Second interaction with Maggie
    if actionable and sam_rect.colliderect(maggie_rect) and scene_6.maggie_exclamation:
        actionable = False
        await text_box("Maggie: You got any of them floor burgers, Sam?!", "Molly: Ignore her, let's sit on the sofa!")
        scene_6.maggie_exclamation = False
        scene_6.sofa_unlocked = True
        actionable = True

    # Interaction with the sofa (wait for Sam and Molly to be near the center)
    if actionable and scene_6.sofa_unlocked:
        sofa_center = pygame.Vector2(scene_6.sofa_rect.center)  # Center of the sofa

        # Check if both Sam and Molly are close to the sofa center
        sam_near_sofa = sam_pos.distance_to(sofa_center) < 60
        molly_near_sofa = molly_pos.distance_to(sofa_center) < 60

        if sam_near_sofa and molly_near_sofa:
            actionable = False
            await text_box("Molly: Hey, can I kiss you?")
            await minigame_scene_6()
            await game_completed()


############################################################################################

### GAMEPLAY LOOP


# -----------------------------------------
# Game loop
async def main():
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

        # Handle asynchronous scenes with await
        if scene == 0:
            await scene_0(keys, event)
        elif scene == 1:
            await scene_1(keys)
        elif scene == 2:
            await scene_2(keys)
        elif scene == 3:
            await scene_3(keys)
        elif scene == 4:
            await scene_4(keys)
        elif scene == 5:
            await scene_5(keys)
        elif scene == 6:
            await scene_6(keys)
        elif scene == 7:
            await scene_7(keys)

        # Refresh the display and enforce frame rate
        pygame.display.flip()
        clock.tick(30)
        await asyncio.sleep(0)  # Allow the event loop to run


# Start the game loop
if __name__ == "__main__":
    asyncio.run(main())
