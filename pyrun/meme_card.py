# meme_card.py
import pygame
import time
from config import STAR_COEFFICIENTS, IMAGE_PATHS, load_image, MEME_CARD_UI_WIDTH, MEME_CARD_UI_HEIGHT, CELL_WIDTH, CELL_HEIGHT
from battle_config import MEME_BASE_HEALTH, MEME_HEALTH_PER_STAR, MEME_ATTACK_INTERVAL, MEME_BASE_DAMAGE, MEME_PROJECTILE_SPEED

class MemeCard:
    def __init__(self, name, base_damage, star_rating, image_key, is_preview=False):
        self.name = name
        self.base_damage = base_damage
        self.star_rating = star_rating
        self.damage_coefficient = STAR_COEFFICIENTS.get(star_rating, 1.0)
        self.image_key = image_key
        
        # 生命值相关
        self.max_health = MEME_BASE_HEALTH + (star_rating - 1) * MEME_HEALTH_PER_STAR
        self.current_health = self.max_health
        
        # 攻击相关
        self.last_attack_time = 0
        self.attack_interval = MEME_ATTACK_INTERVAL
        
        image_path = IMAGE_PATHS.get(self.image_key, IMAGE_PATHS["default_meme"])
        display_size = (MEME_CARD_UI_WIDTH, MEME_CARD_UI_HEIGHT) if is_preview else (CELL_WIDTH - 10, CELL_HEIGHT - 10)
        self.image = load_image(image_path, size=display_size)
        self.rect = self.image.get_rect()

    def get_attack_damage(self):
        return self.base_damage * self.damage_coefficient

    def get_details(self):
        return f"{self.name} ({self.star_rating}★) - DMG: {self.get_attack_damage()}"

    def can_attack(self, current_time):
        return current_time - self.last_attack_time >= self.attack_interval

    def create_projectile(self, target_x, target_y):
        from projectile import Projectile
        projectile = Projectile(
            self.rect.centerx, 
            self.rect.centery,
            target_x,
            target_y,
            self.get_attack_damage()
        )
        self.last_attack_time = time.time()
        return projectile
    
    def take_damage(self, damage):
        self.current_health -= damage
        if self.current_health < 0:
            self.current_health = 0
        return self.current_health <= 0

    def is_alive(self):
        return self.current_health > 0
    
    def draw(self, surface, x, y):
        self.rect.topleft = (x, y)
        surface.blit(self.image, self.rect)
        
        # 修改：总是显示血条，除非满血
        if self.current_health < self.max_health:  # 移除了 current_health > 0 的检查
            health_bar_width = self.rect.width
            health_bar_height = 5
            health_ratio = self.current_health / self.max_health
            current_health_width = int(health_bar_width * health_ratio)
            
            # 绘制血条背景（红色）
            pygame.draw.rect(surface, (255, 0, 0), (
                self.rect.left, self.rect.top - health_bar_height - 2, 
                health_bar_width, health_bar_height))
            
            # 绘制当前血量（绿色）
            if self.current_health > 0:  # 只在有血量时绘制绿色部分
                pygame.draw.rect(surface, (0, 255, 0), (
                    self.rect.left, self.rect.top - health_bar_height - 2, 
                    current_health_width, health_bar_height))

    def __str__(self):
        return f"{self.name}({self.star_rating}*)" 