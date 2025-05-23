# projectile.py
import pygame
from battle_config import MEME_PROJECTILE_SPEED, PROJECTILE_SIZE

class Projectile(pygame.sprite.Sprite):
    """Meme发射的投射物类"""
    
    def __init__(self, x, y, target_x, target_y, damage):
        pygame.sprite.Sprite.__init__(self)
        # 创建一个简单的圆形投射物
        self.image = pygame.Surface(PROJECTILE_SIZE, pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 0), 
                          (PROJECTILE_SIZE[0]//2, PROJECTILE_SIZE[1]//2), 
                          PROJECTILE_SIZE[0]//2)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        
        # 计算移动方向
        dx = target_x - x
        dy = target_y - y
        distance = max(1, (dx**2 + dy**2)**0.5)  # 避免除以零
        self.dx = dx / distance * MEME_PROJECTILE_SPEED
        self.dy = dy / distance * MEME_PROJECTILE_SPEED
        
        # 存储精确位置（浮点数）
        self.x = float(x)
        self.y = float(y)
        
        # 投射物伤害
        self.damage = damage
        
    def update(self, dt):
        # 更新位置
        self.x += self.dx * dt
        self.y += self.dy * dt
        
        # 更新rect位置
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)