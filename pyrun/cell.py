# cell.py
import pygame
from config import CELL_WIDTH, CELL_HEIGHT, IMAGE_PATHS, load_image, GREY, WHITE


class Cell:
    def __init__(self, x, y, width, height, is_placeable=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.meme = None  # Stores a MemeCard object or None
        self.is_placeable = is_placeable
        self.bg_image = load_image(IMAGE_PATHS["cell_bg"], size=(width, height))  # Background for each cell

    def plant_meme(self, meme_card_instance):  # Expecting an actual MemeCard instance
        if self.is_placeable and self.meme is None:
            self.meme = meme_card_instance
            # Adjust meme's position to be centered within the cell
            self.meme.rect.center = self.rect.center
            return True
        return False

    def remove_meme(self):
        self.meme = None

    def draw(self, surface):
        # Draw cell background image or a simple rectangle
        if self.bg_image:
            surface.blit(self.bg_image, self.rect.topleft)
        else:  # Fallback to drawing a colored rectangle
            color = WHITE if self.is_placeable else GREY
            pygame.draw.rect(surface, color, self.rect)

        pygame.draw.rect(surface, (50, 50, 50), self.rect, 1)  # Border for the cell

        if self.meme:
            # The meme's rect should already be set correctly by plant_meme or externally
            self.meme.draw(surface, self.meme.rect.x, self.meme.rect.y)  # Draw meme if present
