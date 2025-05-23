# trump.py
import pygame
import time
from config import (
    NUM_CELLS, IMAGE_PATHS, load_image, CELL_WIDTH, CELL_HEIGHT, 
    TRUMP_SPAWN_CELL_INDEX, GAME_BOARD_START_X, GAME_BOARD_Y, FPS
)
from battle_config import (
    TRUMP_BASE_HEALTH, TRUMP_HEALTH_PER_LEVEL_INCREASE, TRUMP_BASE_MOVE_SPEED,
    TRUMP_SLOW_DOWN_RATE, TRUMP_MIN_MOVE_SPEED, MAX_SLOW_DOWN_EFFECT,
    WHITE_HOUSE_CELL_INDEX, TRUMP_ATTACK_DAMAGE, TRUMP_ATTACK_INTERVAL
)

class Trump:
    def __init__(self, level, spawn_cell_index):
        self.level = level
        self.max_health = TRUMP_BASE_HEALTH + (level - 1) * TRUMP_HEALTH_PER_LEVEL_INCREASE
        self.current_health = self.max_health
        self.logical_position = spawn_cell_index
        self.is_retreating = False
        
        # 平滑移动相关属性
        self.target_position = spawn_cell_index
        self.pixel_x = self.calculate_x_position(spawn_cell_index)
        self.base_move_speed = TRUMP_BASE_MOVE_SPEED
        self.current_move_speed = self.base_move_speed
        self.is_moving = False
        self.slow_down_factor = 1.0  # 减速因子，1.0表示无减速
        
        # 攻击相关属性
        self.attack_damage = TRUMP_ATTACK_DAMAGE
        self.attack_interval = TRUMP_ATTACK_INTERVAL
        self.last_attack_time = 0
        self.is_attacking = False
        self.target_meme = None
        
        # 加载图片
        self.image = load_image(IMAGE_PATHS["trump"], size=(CELL_WIDTH - 10, CELL_HEIGHT - 10))
        self.rect = self.image.get_rect()
        self.update_screen_position()
    
    def calculate_x_position(self, position):
        return GAME_BOARD_START_X + (position * CELL_WIDTH) + CELL_WIDTH // 2
    
    def update_screen_position(self):
        self.rect.centery = GAME_BOARD_Y + CELL_HEIGHT // 2
        self.rect.centerx = self.pixel_x
    
    def move_logical(self):
        # 如果正在攻击，不能移动
        if self.is_attacking:
            return
            
        if not self.is_moving:
            if self.is_retreating:
                if self.logical_position < TRUMP_SPAWN_CELL_INDEX:
                    self.target_position = self.logical_position + 1
                    self.is_moving = True
            else:
                if self.logical_position > WHITE_HOUSE_CELL_INDEX:
                    self.target_position = self.logical_position - 1
                    self.is_moving = True
    
    def set_target_meme(self, meme):
        """设置Trump当前攻击的目标"""
        self.target_meme = meme
        self.is_attacking = meme is not None
        
    def can_attack(self, current_time):
        """检查Trump是否可以攻击"""
        return current_time - self.last_attack_time >= self.attack_interval
        
    def attack_meme(self, current_time):
        """攻击当前目标Meme"""
        if not self.target_meme or not self.is_attacking:
            return False
            
        if not self.can_attack(current_time):
            return False
            
        # 执行攻击
        is_meme_dead = self.target_meme.take_damage(self.attack_damage)
        self.last_attack_time = current_time
        
        print(f"Trump attacks {self.target_meme.name} for {self.attack_damage} damage! Meme health: {self.target_meme.current_health}/{self.target_meme.max_health}")
        
        # 如果Meme已死亡，停止攻击
        if is_meme_dead:
            print(f"{self.target_meme.name} has been defeated!")
            self.is_attacking = False
            self.target_meme = None
            return True
            
        return False
    
    def update(self, dt):
        if self.is_moving:
            # 计算当前实际移动速度
            actual_speed = max(TRUMP_MIN_MOVE_SPEED, self.current_move_speed * self.slow_down_factor)
            
            target_x = self.calculate_x_position(self.target_position)
            current_x = self.pixel_x
            
            # 计算移动方向
            direction = 1 if target_x > current_x else -1
            
            # 计算这一帧要移动的距离
            move_amount = actual_speed * dt
            
            # 更新位置
            self.pixel_x += direction * move_amount
            
            # 检查是否到达目标位置
            if (direction == 1 and self.pixel_x >= target_x) or \
               (direction == -1 and self.pixel_x <= target_x):
                self.pixel_x = target_x
                self.logical_position = self.target_position
                self.is_moving = False
            
            self.update_screen_position()
    
    def take_damage(self, damage):
        if self.is_retreating:
            return
        
        self.current_health -= damage
        
        # 降低移动速度
        self.slow_down_factor *= (1 - TRUMP_SLOW_DOWN_RATE)
        
        # 确保减速不超过最大限制
        if self.slow_down_factor < 1 - MAX_SLOW_DOWN_EFFECT:
            self.slow_down_factor = 1 - MAX_SLOW_DOWN_EFFECT
        
        print(f"Trump took {damage} damage! Health: {self.current_health}/{self.max_health}, Speed: {self.slow_down_factor:.2f}x")
        
        if self.current_health <= 0:
            self.current_health = 0
            print("Trump's health is empty! He's turning back!")
            self.is_retreating = True
    
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.current_health > 0 and not self.is_retreating:
            health_bar_width = self.rect.width
            health_bar_height = 10
            health_ratio = self.current_health / self.max_health
            current_health_width = int(health_bar_width * health_ratio)
            
            pygame.draw.rect(surface, (255, 0, 0), (
                self.rect.left, self.rect.top - health_bar_height - 2, 
                health_bar_width, health_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), (
                self.rect.left, self.rect.top - health_bar_height - 2, 
                current_health_width, health_bar_height))
    
    def __str__(self):
        return "Trump"