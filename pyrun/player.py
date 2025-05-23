# player.py
import random
import pygame
from meme_card import MemeCard # Pygame version
from config import (
    PREDEFINED_MEMES_POOL, COLLECTION_UI_X, COLLECTION_UI_Y, MEME_CARD_UI_WIDTH,
    MEME_CARD_UI_HEIGHT, GREY, BLACK, WHITE
)

class Player:
    def __init__(self, initial_currency=100):
        self.meme_collection = [] # All actual MemeCard instances owned by the player for UI display
        self.currency = initial_currency
        self.score = 0
        self.font = pygame.font.SysFont(None, 30) # Font for UI text

        # For UI interaction with collection
        self.collection_rects = [] # Store rects for clicking owned memes
        self.selected_meme_from_collection_idx = None # Index of meme selected to place

    def add_meme_to_collection(self, meme_data):
        # Create a "preview" version for the collection UI
        meme = MemeCard(meme_data["name"], meme_data["base_damage"], meme_data["star"], meme_data["image_key"], is_preview=True)
        self.meme_collection.append(meme)
        print(f"Player acquired: {meme.get_details()}") # Console log
        self._update_collection_rects()

    def _update_collection_rects(self):
        self.collection_rects = []
        for i, meme_card in enumerate(self.meme_collection):
            x = COLLECTION_UI_X + i * (MEME_CARD_UI_WIDTH + 10) # 10 for spacing
            y = COLLECTION_UI_Y
            meme_card.rect.topleft = (x,y) # Update position of the card itself
            self.collection_rects.append(meme_card.rect)


    def display_collection_ui(self, surface):
        if not self.meme_collection:
            text_surf = self.font.render("Collection is empty.", True, BLACK)
            surface.blit(text_surf, (COLLECTION_UI_X, COLLECTION_UI_Y))
            return

        title_surf = self.font.render("Your Memes (Click to select, then click cell to place):", True, BLACK)
        surface.blit(title_surf, (COLLECTION_UI_X, COLLECTION_UI_Y - 30))

        for i, meme_card in enumerate(self.meme_collection):
            meme_card.draw(surface, meme_card.rect.x, meme_card.rect.y) # Draw the card
            # Highlight if selected
            if i == self.selected_meme_from_collection_idx:
                pygame.draw.rect(surface, (255,255,0), meme_card.rect, 3) # Yellow border

    def handle_collection_click(self, mouse_pos):
        for i, rect in enumerate(self.collection_rects):
            if rect.collidepoint(mouse_pos):
                if self.selected_meme_from_collection_idx == i:
                    self.selected_meme_from_collection_idx = None # Deselect
                else:
                    self.selected_meme_from_collection_idx = i
                print(f"Selected meme from collection: {self.meme_collection[i].name if self.selected_meme_from_collection_idx is not None else 'None'}")
                return True # Click was handled
        return False


    def blind_box_draw(self, cost=10):
        if self.currency < cost:
            print(f"Not enough currency to draw. Need {cost}, have {self.currency}.")
            return None # Potentially show this message on UI
        if not PREDEFINED_MEMES_POOL:
            print("No memes available in the pool to draw from.")
            return None

        self.currency -= cost
        meme_template = random.choice(PREDEFINED_MEMES_POOL)
        self.add_meme_to_collection(meme_template) # Adds UI version of the card
        return meme_template # Returns the template, or could return the instance

    def scan_inventory_for_initial_funds(self, num_initial_memes=3, initial_currency_boost=50):
        print("Scanning user inventory... (simulated)")
        self.currency += initial_currency_boost
        print(f"Granted {initial_currency_boost} initial currency. Total: {self.currency}")
        print("Granting initial memes...")
        for _ in range(num_initial_memes):
            if PREDEFINED_MEMES_POOL:
                meme_template = random.choice(PREDEFINED_MEMES_POOL)
                self.add_meme_to_collection(meme_template)
        self._update_collection_rects() # Ensure rects are set for initial memes
        print("Initial setup complete.")

    def get_selected_meme_for_placement(self):
        if self.selected_meme_from_collection_idx is not None:
            # Return a *new instance* of the selected meme for placement on the board
            # This means the collection represents blueprints, and you place copies.
            original_meme_card = self.meme_collection[self.selected_meme_from_collection_idx]
            # Create a new MemeCard instance that's sized for the game board, not for UI preview
            return MemeCard(
                original_meme_card.name,
                original_meme_card.base_damage,
                original_meme_card.star_rating,
                original_meme_card.image_key,
                is_preview=False # This will load the image at game board size
            )
        return None
