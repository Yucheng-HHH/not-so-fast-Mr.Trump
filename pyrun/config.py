# config.py
import pygame

# --- Game Settings ---
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 30 # Frames per second

# --- Colors (RGB) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
LIGHT_BLUE = (173, 216, 230)

# --- Game Logic Constants (from previous config) ---
TRUMP_BASE_HEALTH = 100
TRUMP_HEALTH_PER_LEVEL_INCREASE = 50
TRUMP_MOVE_INTERVAL = 4  # seconds per cell (will translate to game ticks)
GAME_TICK_DURATION = 1   # Not directly used in Pygame loop same way, FPS controls timing

STAR_COEFFICIENTS = {1: 1.0, 2: 1.2, 3: 1.5, 4: 2.0, 5: 2.5}

NUM_CELLS = 7
PLACEABLE_CELLS = 5
WHITE_HOUSE_CELL_INDEX = -1 # Conceptually Trump wins if he reaches this logical position
TRUMP_SPAWN_CELL_INDEX = NUM_CELLS - 1

# --- UI Element Sizes and Positions (Example) ---
CELL_WIDTH = 100
CELL_HEIGHT = 100
WHITE_HOUSE_WIDTH = 120 # Width of the White House image/area
GAME_BOARD_START_X = WHITE_HOUSE_WIDTH + 20 # Start X for the first cell
GAME_BOARD_Y = SCREEN_HEIGHT // 2 - CELL_HEIGHT // 2

MEME_CARD_UI_WIDTH = 80
MEME_CARD_UI_HEIGHT = 100
COLLECTION_UI_X = 20
COLLECTION_UI_Y = SCREEN_HEIGHT - MEME_CARD_UI_HEIGHT - 20

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# --- Image Asset Paths (REPLACE WITH YOUR ACTUAL PATHS) ---
# Create an 'assets' folder in your project directory for these
ASSET_PATH = "assets/" # Make sure this folder exists
IMAGE_PATHS = {
    "white_house": ASSET_PATH + "white_house.png", # Placeholder
    "trump": ASSET_PATH + "trump.png",           # Placeholder
    "cell_bg": ASSET_PATH + "cell_bg.png",         # Placeholder
    # Add paths for your memes, e.g.:
    "Pepe": ASSET_PATH + "pepe.png",
    "Doge": ASSET_PATH + "doge.png",
    "Stonks": ASSET_PATH + "stonks.png",
    "Grumpy Cat": ASSET_PATH + "grumpy_cat.png",
    "Distracted BF": ASSET_PATH + "distracted_bf.png",
    # Default meme image if specific one not found
    "default_meme": ASSET_PATH + "default_meme.png"
}

# Predefined Meme types (name, base_damage, star_rating, image_key - refers to IMAGE_PATHS)
PREDEFINED_MEMES_POOL = [
    {"name": "Pepe", "base_damage": 15, "star": 4, "image_key": "Pepe"},
    {"name": "Doge", "base_damage": 10, "star": 3, "image_key": "Doge"},
    {"name": "Stonks", "base_damage": 20, "star": 5, "image_key": "Stonks"},
    {"name": "Grumpy Cat", "base_damage": 8, "star": 2, "image_key": "Grumpy Cat"},
    {"name": "Distracted BF", "base_damage": 5, "star": 1, "image_key": "Distracted BF"},
]

# Helper function to load images (and handle missing images)
def load_image(path, size=None):
    try:
        image = pygame.image.load(path)
        if path.endswith(".png"): # Ensure alpha transparency for PNGs
            image = image.convert_alpha()
        else:
            image = image.convert()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Warning: Could not load image at {path}: {e}")
        # Return a placeholder surface if image fails to load
        fallback_size = size if size else (50,50)
        surface = pygame.Surface(fallback_size)
        surface.fill(RED) # Fill with a noticeable color like red
        # Draw a small 'X' or '?' on the placeholder
        font = pygame.font.SysFont(None, fallback_size[0]//2)
        text_surf = font.render("X", True, BLACK)
        text_rect = text_surf.get_rect(center=(fallback_size[0]//2, fallback_size[1]//2))
        surface.blit(text_surf, text_rect)
        return surface

