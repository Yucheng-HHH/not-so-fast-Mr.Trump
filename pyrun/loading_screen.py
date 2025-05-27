# loading_screen.py
import pygame
import time
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, load_image

class LoadingScreen:
    def __init__(self, screen):
        """初始化加载页面
        
        Args:
            screen: pygame Surface对象，游戏的主屏幕
        """
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # 加载Trump图像
        script_dir = os.path.dirname(os.path.abspath(__file__))
        trump_path = os.path.join(script_dir, "assets", "trump.png")
        try:
            self.trump_image = load_image(trump_path, size=(150, 200))
        except:
            # 如果无法加载特定图像，创建一个占位符
            self.trump_image = pygame.Surface((150, 200))
            self.trump_image.fill((255, 215, 0))  # 金色背景
            text_surf = self.font.render("TRUMP", True, (0, 0, 0))
            self.trump_image.blit(text_surf, (30, 80))
        
        # 进度条属性
        self.progress = 0
        self.loading_steps = 100  # 加载步骤总数
        self.progress_bar_width = 400
        self.progress_bar_height = 20
        self.progress_bar_x = (SCREEN_WIDTH - self.progress_bar_width) // 2
        self.progress_bar_y = SCREEN_HEIGHT - 100
        
        # 加载动画属性
        self.dots_count = 0
        self.last_dot_time = 0
        self.dot_interval = 0.5  # 每0.5秒添加一个点
    
    def update(self, progress_value=None):
        """更新加载进度
        
        Args:
            progress_value: 可选，直接设置进度值(0-100)
        """
        if progress_value is not None:
            self.progress = min(100, max(0, progress_value))
        else:
            # 自动增加进度
            self.progress = min(100, self.progress + 1)
        
        # 更新动画点
        current_time = time.time()
        if current_time - self.last_dot_time > self.dot_interval:
            self.dots_count = (self.dots_count + 1) % 4
            self.last_dot_time = current_time
    
    def draw(self):
        """绘制加载页面"""
        # 清空屏幕
        self.screen.fill(BLACK)
        
        # 绘制Trump图像
        trump_x = (SCREEN_WIDTH - self.trump_image.get_width()) // 2
        trump_y = (SCREEN_HEIGHT - self.trump_image.get_height() - 150) // 2
        self.screen.blit(self.trump_image, (trump_x, trump_y))
        
        # 绘制"NOW LOADING"文本
        dots = "." * self.dots_count
        loading_text = f"NOW LOADING{dots}"
        loading_surf = self.font.render(loading_text, True, WHITE)
        loading_rect = loading_surf.get_rect(center=(SCREEN_WIDTH // 2, self.progress_bar_y - 30))
        self.screen.blit(loading_surf, loading_rect)
        
        # 绘制进度条背景
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (self.progress_bar_x, self.progress_bar_y, 
                         self.progress_bar_width, self.progress_bar_height))
        
        # 绘制进度条
        progress_width = int(self.progress_bar_width * (self.progress / 100))
        pygame.draw.rect(self.screen, WHITE, 
                        (self.progress_bar_x, self.progress_bar_y, 
                         progress_width, self.progress_bar_height))
        
        # 绘制进度条边框
        pygame.draw.rect(self.screen, WHITE, 
                        (self.progress_bar_x, self.progress_bar_y, 
                         self.progress_bar_width, self.progress_bar_height), 2)
        
        # 更新屏幕
        pygame.display.flip()
    
    def run(self, load_resources_func=None):
        """运行加载页面
        
        Args:
            load_resources_func: 可选，用于加载资源的函数
        
        Returns:
            bool: 加载是否完成
        """
        clock = pygame.time.Clock()
        
        # 如果提供了资源加载函数，则使用它
        if load_resources_func:
            try:
                for progress in load_resources_func():
                    self.update(progress)
                    self.draw()
                    
                    # 处理事件，允许用户退出
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                    
                    clock.tick(30)
            except Exception as e:
                print(f"Error loading resources: {e}")
                return False
        else:
            # 模拟加载过程
            while self.progress < 100:
                self.update()
                self.draw()
                
                # 处理事件，允许用户退出
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                
                # 控制加载速度
                pygame.time.delay(50)  # 50毫秒延迟
                clock.tick(30)
        
        # 完成加载后再显示一小段时间
        pygame.time.delay(500)
        return True

# 测试代码
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Loading Screen Test")
    
    loading = LoadingScreen(screen)
    loading.run()
    
    pygame.quit() 