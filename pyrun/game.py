# game.py
import pygame
import sys
import time
import webbrowser
from player import Player
from game_board import GameBoard
from trump import Trump
from meme_card import MemeCard
from projectile import Projectile
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, GREEN, RED, LIGHT_BLUE,
    TRUMP_MOVE_INTERVAL, WHITE_HOUSE_CELL_INDEX, TRUMP_SPAWN_CELL_INDEX, NUM_CELLS,
    BUTTON_WIDTH, BUTTON_HEIGHT, PREDEFINED_MEMES_POOL
)
from battle_config import MEME_ATTACK_INTERVAL

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()  # 初始化字体模块
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Meme vs Trump - Pygame Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)  # 一般字体
        self.small_font = pygame.font.SysFont(None, 30)

        self.player = Player()
        self.game_board = GameBoard()
        self.trump_character = None
        self.current_level = 0
        self.trump_score = 0
        self.game_running = True  # 游戏是否运行
        self.level_active = False  # 特定关卡是否进行中

        self.trump_move_timer_accumulator = 0  # 累计时间
        
        # UI元素
        self.draw_card_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 20, 20, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.next_level_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 
                                                 SCREEN_HEIGHT - BUTTON_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.open_browser_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 20, 20 + BUTTON_HEIGHT + 10, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.game_message = ""  # 显示消息如"Trump到达白宫"或"关卡完成"
        self.message_timer = 0  # 显示消息的时间
        
        # 新增投射物相关
        self.projectiles = pygame.sprite.Group()
        self.last_projectile_update = time.time()

    def setup_level(self, level):
        self.current_level = level
        self.game_board.clear_board_memes()
        self.trump_character = Trump(level, TRUMP_SPAWN_CELL_INDEX)
        self.trump_move_timer_accumulator = 0
        self.level_active = True
        self.player.selected_meme_from_collection_idx = None  # 取消选择任何meme
        self.game_message = f"Level {self.current_level} Start!"
        self.message_timer = FPS * 2  # 显示2秒
        print(f"\n--- Level {self.current_level} Starting ---")
        print(f"Trump has {self.trump_character.max_health} HP this level.")

    def initial_setup_phase(self):  # 游戏开始时调用一次
        print("Welcome to Meme vs Trump!")
        self.player.scan_inventory_for_initial_funds()  # 模拟扫描库存

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
                self.level_active = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()

                    # 1. 首先检查UI按钮
                    if self.draw_card_button_rect.collidepoint(mouse_pos):
                        print("Draw Card button clicked")
                        drawn_meme_template = self.player.blind_box_draw(cost=10)
                        if drawn_meme_template:
                            self.game_message = f"Drew: {drawn_meme_template['name']}!"
                        else:
                            self.game_message = f"Draw failed. Currency: {self.player.currency}"
                        self.message_timer = FPS * 2
                        return  # 消耗点击

                    if self.open_browser_button_rect.collidepoint(mouse_pos):
                        print("Open Browser button clicked")
                        try:
                            webbrowser.open("http://localhost:5173")
                            self.game_message = "Opening browser..."
                        except Exception as e:
                            self.game_message = f"Failed to open browser: {e}"
                        self.message_timer = FPS * 2
                        return

                    if not self.level_active and self.next_level_button_rect.collidepoint(mouse_pos):
                        if self.trump_score > 0 or self.player.score > 0:  # 如果一轮已经结束
                            print("Next Level button clicked")
                            self.setup_level(self.current_level + 1)
                        return  # 消耗点击

                    # 2. 处理玩家的meme收藏点击(选择一个meme放置)
                    if self.player.handle_collection_click(mouse_pos):
                        return  # 点击由收藏UI处理

                    # 3. 处理在游戏板上放置所选meme(如果关卡活动)
                    if self.level_active and self.player.selected_meme_from_collection_idx is not None:
                        cell_idx, target_cell = self.game_board.get_cell_at_pos(mouse_pos)
                        if target_cell and target_cell.is_placeable:
                            meme_to_place = self.player.get_selected_meme_for_placement()  # 获取新实例
                            if meme_to_place:
                                if target_cell.plant_meme(meme_to_place):
                                    print(f"Placed {meme_to_place.name} in cell {cell_idx}")
                                else:
                                    print(f"Could not place {meme_to_place.name} in cell {cell_idx}. Occupied?")
                                    self.game_message = "Cell occupied or not placeable."
                                    self.message_timer = FPS * 1.5
                            else:  # 如果selected_meme_from_collection_idx有效，不应该发生
                                print("Error: No meme instance to place despite selection.")
                        elif target_cell and not target_cell.is_placeable:
                            self.game_message = "Cannot place meme in this cell."
                            self.message_timer = FPS * 1.5

    def update_game_state(self, dt):
        current_time = time.time()
        
        if not self.level_active or not self.trump_character:
            return
        
        self.trump_move_timer_accumulator += dt
        
        # 1. 检查Trump前方是否有Meme，如果有则攻击
        next_cell_idx = self.trump_character.logical_position - 1
        if (not self.trump_character.is_retreating and 
            not self.trump_character.is_moving and 
            not self.trump_character.is_attacking and
            0 <= next_cell_idx < NUM_CELLS):
            
            next_cell = self.game_board.get_cell_by_index(next_cell_idx)
            if next_cell and next_cell.meme and next_cell.meme.is_alive():
                print(f"Trump encountered {next_cell.meme.name} at cell {next_cell_idx}!")
                self.trump_character.set_target_meme(next_cell.meme)
        
        # 2. 如果Trump正在攻击，执行攻击
        if self.trump_character.is_attacking:
            damage_done = self.trump_character.attack_meme(current_time)  # 修改这里，获取攻击结果
            if damage_done:  # 如果造成了伤害
                target_meme = self.trump_character.target_meme
                if target_meme and target_meme.take_damage(damage_done):  # 如果Meme死亡
                    # 找到并移除死亡的Meme
                    for cell_idx in range(NUM_CELLS):
                        cell = self.game_board.get_cell_by_index(cell_idx)
                        if cell and cell.meme == target_meme:
                            cell.meme = None  # 移除死亡的Meme
                            self.trump_character.target_meme = None  # 清除Trump的目标
                            self.trump_character.is_attacking = False  # 停止攻击
                            print(f"Meme in cell {cell_idx} has been defeated!")
                            break
        # 3. Trump移动(基于累计时间)
        if self.trump_move_timer_accumulator >= TRUMP_MOVE_INTERVAL:
            if not self.trump_character.is_moving and not self.trump_character.is_attacking:
                self.trump_character.move_logical()
                self.trump_move_timer_accumulator = 0  # 重置累计器
        
        # 更新Trump的平滑移动
        self.trump_character.update(dt)
        
        # 4. Meme射击逻辑 - 当Trump在场时，所有放置的Meme都会尝试攻击
        if not self.trump_character.is_retreating and self.trump_character.logical_position < NUM_CELLS:
            # 获取所有放置的Meme
            for cell_idx in range(NUM_CELLS):
                cell = self.game_board.get_cell_by_index(cell_idx)
                if cell and cell.meme:
                    meme = cell.meme
                    if hasattr(meme, 'can_attack') and meme.can_attack(current_time):
                        # 创建一个射向Trump的投射物
                        if hasattr(meme, 'create_projectile'):
                            projectile = meme.create_projectile(
                                self.trump_character.rect.centerx,
                                self.trump_character.rect.centery
                            )
                            self.projectiles.add(projectile)
                            print(f"{meme.name} in cell {cell_idx} fires at Trump!")
        
        # 5. 更新投射物并检查碰撞
        self.projectiles.update(dt)
        
        # 检查投射物碰撞
        collided_projectiles = pygame.sprite.spritecollide(self.trump_character, self.projectiles, True)
        for projectile in collided_projectiles:
            self.trump_character.take_damage(projectile.damage)
            if self.trump_character.current_health <= 0 and not self.trump_character.is_retreating:
                self.trump_character.is_retreating = True
                self.game_message = "Trump is retreating!"
                self.message_timer = FPS * 2
        
        # 移除超出屏幕的投射物
        for projectile in self.projectiles.sprites():
            if (projectile.rect.right < 0 or projectile.rect.left > SCREEN_WIDTH or
                projectile.rect.bottom < 0 or projectile.rect.top > SCREEN_HEIGHT):
                projectile.kill()
        
        # 6. 原始攻击逻辑 - Trump在格子上时，meme攻击
        if not self.trump_character.is_retreating and not self.trump_character.is_moving and \
        0 <= self.trump_character.logical_position < NUM_CELLS:
            cell_trump_is_on = self.game_board.get_cell_by_index(self.trump_character.logical_position)
            if cell_trump_is_on and cell_trump_is_on.meme:
                meme = cell_trump_is_on.meme
                if self.trump_move_timer_accumulator == 0:  # 当Trump刚移动或重置间隔
                    damage = meme.get_attack_damage()
                    print(f"{meme.name} in cell {self.trump_character.logical_position} attacks Trump for {damage} damage!")
                    self.trump_character.take_damage(damage)
                    if meme.current_health <= 0:  # 如果Meme死亡
                        cell_trump_is_on.meme = None  # 完全移除Meme
                        if self.trump_character.target_meme == meme:
                            self.trump_character.target_meme = None  # 清除Trump的目标
                            self.trump_character.is_attacking = False  # 停止攻击
                        print(f"Meme in cell {self.trump_character.logical_position} has been defeated!")
                    if self.trump_character.current_health <= 0 and not self.trump_character.is_retreating:
                        self.trump_character.is_retreating = True
                        self.game_message = "Trump is retreating!"
                        self.message_timer = FPS * 2
        
        # 7. 检查回合结束条件
        if self.level_active and not self.trump_character.is_moving:  # 仅在完全进入格子时检查
            # Trump到达白宫
            if not self.trump_character.is_retreating and self.trump_character.logical_position <= WHITE_HOUSE_CELL_INDEX:
                print("\nOh no! Trump reached the White House!")
                self.game_message = "Trump reached the White House!"
                self.message_timer = FPS * 3
                self.trump_score += 1
                self.level_active = False
            
            # Trump被击败(撤退出地图)
            if self.trump_character.is_retreating and self.trump_character.logical_position >= TRUMP_SPAWN_CELL_INDEX:
                print("\nSuccess! Trump has retreated from the map!")
                self.game_message = f"Level {self.current_level} Cleared! Trump Retreated!"
                self.message_timer = FPS * 3
                self.player.score += 1
                self.level_active = False
        
        if self.message_timer > 0:
            self.message_timer -= 1

    def draw_ui_elements(self):
        # 绘制"Draw Card"按钮
        pygame.draw.rect(self.screen, LIGHT_BLUE, self.draw_card_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.draw_card_button_rect, 2)  # 边框
        draw_text = self.small_font.render("Draw Meme (10)", True, BLACK)
        self.screen.blit(draw_text, (self.draw_card_button_rect.x + 10, self.draw_card_button_rect.y + 15))
        
        # 绘制"Open Browser"按钮
        pygame.draw.rect(self.screen, LIGHT_BLUE, self.open_browser_button_rect)
        pygame.draw.rect(self.screen, BLACK, self.open_browser_button_rect, 2)
        browser_text = self.small_font.render("Open WebApp", True, BLACK)
        self.screen.blit(browser_text, (self.open_browser_button_rect.x + 10, self.open_browser_button_rect.y + 15))
        
        # 绘制分数和货币
        score_text = self.small_font.render(f"Player: {self.player.score} | Trump: {self.trump_score}", True, BLACK)
        self.screen.blit(score_text, (20, 20))
        currency_text = self.small_font.render(f"Currency: {self.player.currency}", True, BLACK)
        self.screen.blit(currency_text, (20, 50))
        level_text = self.small_font.render(f"Level: {self.current_level}", True, BLACK)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 50, 20))
        
        # 绘制玩家的Meme收藏UI
        self.player.display_collection_ui(self.screen)
        
        # 如果关卡不活动且游戏已开始，绘制"Next Level"按钮
        if not self.level_active and (self.player.score > 0 or self.trump_score > 0 or self.current_level > 0):
            pygame.draw.rect(self.screen, GREEN, self.next_level_button_rect)
            pygame.draw.rect(self.screen, BLACK, self.next_level_button_rect, 2)
            next_level_text = self.small_font.render("Next Level", True, BLACK)
            self.screen.blit(next_level_text, (self.next_level_button_rect.x + 25, self.next_level_button_rect.y + 15))
        
        # 显示游戏消息
        if self.message_timer > 0 and self.game_message:
            msg_surf = self.font.render(self.game_message, True, RED if "Trump reached" in self.game_message else BLACK,
                                       WHITE if "Trump reached" in self.game_message else None)  # 重要消息白色背景
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(msg_surf, msg_rect)

    def render_game(self):
        self.screen.fill(WHITE)  # 背景
        
        # 绘制游戏板(包括白宫和带有Meme的格子)
        self.game_board.draw(self.screen)
        
        # 绘制Trump
        if self.trump_character and self.level_active:  # 只有在存在且关卡活动时绘制
            self.trump_character.draw(self.screen)
        
        # 绘制所有投射物
        self.projectiles.draw(self.screen)
        
        # 在顶部绘制UI元素
        self.draw_ui_elements()
        
        pygame.display.flip()  # 更新整个屏幕

    def game_loop(self):
        self.initial_setup_phase()
        # 自动开始第1关或等待"开始游戏"按钮
        self.setup_level(1)  # 现在自动开始第1关
        
        while self.game_running:
            dt = self.clock.tick(FPS) / 1000.0  # 秒为单位的增量时间
            
            self.handle_input()
            self.update_game_state(dt)
            self.render_game()
        
        self.display_final_scores()
        pygame.quit()
        sys.exit()

    def display_final_scores(self):  # 目前基于文本，可以是Pygame屏幕
        print("\n=== GAME OVER ===")
        print(f"Final Score - Player: {self.player.score} | Trump: {self.trump_score}")
        if self.player.score > self.trump_score:
            print("Congratulations! You have defeated Trump!")
        elif self.player.score < self.trump_score:
            print("Trump has won. Better luck next time!")
        else:
            print("It's a tie! The battle continues another day.")