# game_board.py
import pygame
from cell import Cell # Use the Pygame version
from config import (
    NUM_CELLS, PLACEABLE_CELLS, CELL_WIDTH, CELL_HEIGHT,
    GAME_BOARD_Y, GAME_BOARD_START_X, IMAGE_PATHS, load_image, WHITE_HOUSE_WIDTH, SCREEN_HEIGHT
)

class GameBoard:
    def __init__(self):
        self.cells = []
        # Load White House image
        self.white_house_image = load_image(IMAGE_PATHS["white_house"], size=(WHITE_HOUSE_WIDTH, CELL_HEIGHT * 2)) # Example size
        self.white_house_rect = self.white_house_image.get_rect(
            left=10, # Small padding from screen edge
            centery=GAME_BOARD_Y + CELL_HEIGHT / 2 # Align with cell row
        )

        for i in range(NUM_CELLS):
            cell_x = GAME_BOARD_START_X + (i * CELL_WIDTH)
            cell_y = GAME_BOARD_Y
            is_placeable = i < PLACEABLE_CELLS
            self.cells.append(Cell(cell_x, cell_y, CELL_WIDTH, CELL_HEIGHT, is_placeable))

    def draw(self, surface, trump_object=None):
        # Draw White House
        surface.blit(self.white_house_image, self.white_house_rect)

        # Draw cells
        for cell in self.cells:
            cell.draw(surface)

        # Draw Trump (handled by Game class draw method to ensure correct layering if needed)
        # if trump_object:
        #     trump_object.draw(surface)

    def get_cell_at_pos(self, screen_pos): # For mouse clicks
        for i, cell in enumerate(self.cells):
            if cell.rect.collidepoint(screen_pos) and cell.is_placeable:
                return i, cell # Return index and cell object
        return None, None

    def get_cell_by_index(self, index):
        if 0 <= index < NUM_CELLS:
            return self.cells[index]
        return None

    def clear_board_memes(self):
        for cell in self.cells:
            cell.remove_meme()
    # game_board.py 中的 Cell 类
    def remove_meme(self):
        self.meme = None