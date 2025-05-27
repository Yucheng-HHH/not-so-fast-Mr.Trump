# main.py

# It's crucial that all image paths in config_pygame.py are correct
# and the 'assets' folder (or whatever you named it) is in the same
# directory as main_pygame.py, and contains the necessary images.

import pygame
import time
import random
from game import Game
from loading_screen import LoadingScreen
from start_screen import StartScreen
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def load_game_resources():
    """模拟加载游戏资源的函数，生成进度值
    
    Yields:
        int: 当前进度值(0-100)
    """
    # 这里可以添加真实的资源加载逻辑
    # 例如预加载图像、音频等
    
    progress = 0
    while progress < 100:
        # 模拟不同的加载速度
        increment = random.randint(1, 5)
        progress = min(100, progress + increment)
        
        # 模拟加载延迟
        time.sleep(0.1)
        
        yield progress

if __name__ == "__main__":
    # 初始化Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Meme vs Trump (Pygame Edition)")
    
    print("Starting Meme vs Trump (Pygame Edition)...")
    print("Ensure you have an 'assets' folder with images as specified in config.py")
    
    # 显示加载页面
    loading = LoadingScreen(screen)
    if loading.run(load_game_resources):
        # 加载完成后，显示开始页面
        start_screen = StartScreen(screen)
        choice = start_screen.run()
        
        if choice != 'quit':
            # 根据用户选择启动游戏
            # 无论是'guest'还是'wallet'模式都启动游戏
            # 'wallet'模式已经在StartScreen中打开了浏览器
            main_game = Game(screen=screen)
            main_game.game_loop()
    else:
        # 如果加载被中断（例如用户关闭窗口）
        print("Game loading was interrupted.")
    
    # 清理Pygame
    pygame.quit()
