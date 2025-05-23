# main.py

# It's crucial that all image paths in config_pygame.py are correct
# and the 'assets' folder (or whatever you named it) is in the same
# directory as main_pygame.py, and contains the necessary images.

from game import Game

if __name__ == "__main__":
    # Before starting the game, you might want to check if Pygame was imported successfully
    # and if essential assets can be loaded, though some loading is done within classes.

    # Create a dummy 'assets' folder and put some placeholder .png images in it:
    # assets/white_house.png
    # assets/trump.png
    # assets/cell_bg.png
    # assets/pepe.png
    # assets/doge.png
    # ... and others defined in config.IMAGE_PATHS
    # If images are missing, red squares will be drawn.

    print("Starting Meme vs Trump (Pygame Edition)...")
    print("Ensure you have an 'assets' folder with images as specified in config_pygame.py")

    main_game = Game()
    main_game.game_loop()
