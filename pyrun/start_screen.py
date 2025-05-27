import pygame
import os
import webbrowser
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, load_image

class StartScreen:
    def __init__(self, screen):
        """初始化开始页面
        
        Args:
            screen: pygame Surface对象，游戏的主屏幕
        """
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        
        # 加载背景图像
        script_dir = os.path.dirname(os.path.abspath(__file__))
        begin_path = os.path.join(script_dir, "assets", "begin", "begin.png")
        try:
            self.begin_image = load_image(begin_path)
            # 调整图像大小以适应屏幕中央区域
            image_width = int(SCREEN_WIDTH * 0.8)
            image_height = int(SCREEN_HEIGHT * 0.5)
            self.begin_image = pygame.transform.scale(self.begin_image, (image_width, image_height))
        except Exception as e:
            print(f"无法加载开始页面图像: {e}")
            # 创建一个占位符
            self.begin_image = pygame.Surface((int(SCREEN_WIDTH * 0.8), int(SCREEN_HEIGHT * 0.5)))
            self.begin_image.fill((200, 200, 200))  # 灰色背景
        
        # 标题
        self.title_text = "NOT SO FAST MR. TRUMP"
        self.title_color = (180, 0, 0)  # 红色
        
        # 按钮属性
        self.button_width = 200
        self.button_height = 50
        
        # Guest Mode按钮
        self.guest_button_rect = pygame.Rect(
            SCREEN_WIDTH // 4 - self.button_width // 2,
            120,
            self.button_width,
            self.button_height
        )
        self.guest_button_color = (23, 71, 91)  # 深蓝色
        self.guest_button_text = "Guest Mode"
        
        # Connect Wallet按钮
        self.wallet_button_rect = pygame.Rect(
            3 * SCREEN_WIDTH // 4 - self.button_width // 2,
            120,
            self.button_width,
            self.button_height
        )
        self.wallet_button_color = (180, 60, 30)  # 红棕色
        self.wallet_button_text = "Connect Wallet"
        
        # 图像位置 - 放在按钮下方
        self.image_rect = self.begin_image.get_rect()
        self.image_rect.centerx = SCREEN_WIDTH // 2
        self.image_rect.top = 180
        
        # 关闭按钮
        self.close_button_rect = pygame.Rect(SCREEN_WIDTH - 40, 10, 30, 30)
        self.close_button_text = "X"
    
    def handle_events(self):
        """处理用户输入事件
        
        Returns:
            str: 'guest' 表示选择Guest Mode，'wallet' 表示选择Connect Wallet，None 表示无选择
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 检查是否点击了关闭按钮
                    if self.close_button_rect.collidepoint(mouse_pos):
                        return 'quit'
                    
                    # 检查是否点击了Guest Mode按钮
                    if self.guest_button_rect.collidepoint(mouse_pos):
                        return 'guest'
                    
                    # 检查是否点击了Connect Wallet按钮
                    if self.wallet_button_rect.collidepoint(mouse_pos):
                        # 尝试打开Web应用
                        try:
                            webbrowser.open("http://localhost:5173")
                        except Exception as e:
                            print(f"无法打开浏览器: {e}")
                        return 'wallet'
        
        return None
    
    def draw(self):
        """绘制开始页面"""
        # 清空屏幕
        self.screen.fill((255, 255, 204))  # 浅黄色背景，与图片中背景色相匹配
        
        # 绘制标题
        title_surf = self.font.render(self.title_text, True, self.title_color)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # 绘制Guest Mode按钮
        pygame.draw.rect(self.screen, self.guest_button_color, self.guest_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.guest_button_rect, 2)  # 白色边框
        guest_text = self.button_font.render(self.guest_button_text, True, WHITE)
        guest_text_rect = guest_text.get_rect(center=self.guest_button_rect.center)
        self.screen.blit(guest_text, guest_text_rect)
        
        # 绘制Connect Wallet按钮
        pygame.draw.rect(self.screen, self.wallet_button_color, self.wallet_button_rect)
        pygame.draw.rect(self.screen, WHITE, self.wallet_button_rect, 2)  # 白色边框
        wallet_text = self.button_font.render(self.wallet_button_text, True, WHITE)
        wallet_text_rect = wallet_text.get_rect(center=self.wallet_button_rect.center)
        self.screen.blit(wallet_text, wallet_text_rect)
        
        # 绘制图像 - 在按钮下方
        self.screen.blit(self.begin_image, self.image_rect)
        
        # 绘制关闭按钮
        pygame.draw.rect(self.screen, (0, 0, 0), self.close_button_rect)
        close_text = self.button_font.render(self.close_button_text, True, WHITE)
        close_text_rect = close_text.get_rect(center=self.close_button_rect.center)
        self.screen.blit(close_text, close_text_rect)
        
        # 更新屏幕
        pygame.display.flip()
    
    def run(self):
        """运行开始页面
        
        Returns:
            str: 'guest' 表示选择Guest Mode，'wallet' 表示选择Connect Wallet，'quit' 表示退出游戏
        """
        clock = pygame.time.Clock()
        running = True
        
        while running:
            result = self.handle_events()
            if result:
                return result
            
            self.draw()
            clock.tick(30)
        
        return 'quit'

# 测试代码
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Start Screen Test")
    
    start_screen = StartScreen(screen)
    choice = start_screen.run()
    print(f"选择: {choice}")
    
    pygame.quit() 