import pygame
from abc import ABC, abstractmethod
from background.back_g import background
from player import Player
from boss import MinotaurBoss, BossUI
from menu import MainMenu, SettingsMenu, PauseMenu

# =====================================================================
# 1. Abstraction (นามธรรม)
# =====================================================================
# สร้าง Abstract Base Class (แบบร่าง) สำหรับพื้นที่ (Area)
class Area(ABC):
    def __init__(self, x, y, width, height):
        # =====================================================================
        # 2. Encapsulation (การห่อหุ้ม)
        # =====================================================================
        # ซ่อนแอตทริบิวต์ _rect เป็น protected มิดชิดไม่ให้แก้ตรงๆ เพื่อความปลอดภัย
        self._rect = pygame.Rect(x, y, width, height)

    @property
    def rect(self):
        """Getter สำหรับเข้าถึง rect อย่างปลอดภัย"""
        return self._rect
        
    @abstractmethod
    def draw(self, screen):
        """Method บังคับให้ Subclass ต้องมีเพื่อวาดตัวเองลงจอ"""
        pass

    @abstractmethod
    def is_walkable(self):
        """Method บังคับให้บอกว่าพื้นที่นี้เดินได้หรือไม่"""
        pass

# =====================================================================
# 3. Inheritance (การสืบทอด)
# =====================================================================
# WalkableArea และ ObstacleArea สืบทอดจาก Area
class WalkableArea(Area):
    def __init__(self, x, y, width, height, color=(0, 255, 0, 100)): # สีเขียวโปร่งใส
        super().__init__(x, y, width, height)
        self._color = color # Encapsulation ซ่อนข้อมูลสี

    # =====================================================================
    # 4. Polymorphism (พหุสัณฐาน)
    # =====================================================================
    # การตอบสนองต่อ draw แตกต่างกันไปตามแต่ละคลาส
    def draw(self, screen):
        # ปิดการแสดงผลแถบสี (ให้เป็นแค่พื้นที่ตรวจสอบการชน/เดินในระบบ)
        pass

    def is_walkable(self):
        return True # เป็นพื้นที่ที่เดินได้

class ObstacleArea(Area):
    def __init__(self, x, y, width, height, color=(255, 0, 0, 100)): # สีแดงโปร่งใส
        super().__init__(x, y, width, height)
        self._color = color
        
    # Polymorphism: รูปแบบการทำงานที่ต่างจาก WalkableArea ทั้งๆ ที่ชื่อ method เหมือนกัน
    def draw(self, screen):
        # ปิดการแสดงผลแถบสี
        pass

    def is_walkable(self):
        return False # เป็นพื้นที่จำกัด ไม่ให้เดินผ่าน

# =====================================================================
# Main Game Loop
# =====================================================================
pygame.init()

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("My Game")
screen.fill((255, 255, 255))

# อิงตามเดิมที่มีอยู่
bg = background(screen, "bg-1.jpg")

# =====================================================================
# ระบบเปลี่ยนแปลงฉาก (Scene Management)
# =====================================================================
# สร้างฟังก์ชันสำหรับโหลดฉากตามหมายเลข
def load_scene(scene_number):
    if scene_number == 1:
        # ฉากที่ 1
        new_bg = background(screen, "bg-1.jpg")
        new_areas = [
            WalkableArea(0, 450, 800, 50),       # พื้นดิน
            ObstacleArea(350, 320, 50, 80)       # กำแพงกั้นกลางฉาก
        ]
        return new_bg, new_areas
        
    elif scene_number == 2:
        # ฉากที่ 2
        new_bg = background(screen, "bg-2.jpg")
        new_areas = [
            # พื้นดินฉาก 2 อาจปรับระดับความสูงหรือสร้างสิ่งกีดขวางแบบใหม่ได้
            WalkableArea(0, 450, 800, 50),       # พื้นดิน
        ]
        return new_bg, new_areas
        
    elif scene_number == 3:
        # ฉากที่ 3
        new_bg = background(screen, "bg-3.jpg")
        new_areas = [
            # พื้นดินฉาก 3
            WalkableArea(0, 450, 800, 50),       # พื้นดิน
        ]
        return new_bg, new_areas
        
    elif scene_number == 4:
        # ฉากที่ 4
        new_bg = background(screen, "Dungeon - Pixel Art _ Animations, Mathieu Chauderlot.jpg")
        new_areas = [
            # พื้นดินฉาก 4
            WalkableArea(0, 450, 800, 50),       # พื้นดิน
        ]
        return new_bg, new_areas

current_scene = 1
bg, game_areas = load_scene(current_scene)
current_boss = None
current_boss_ui = None

# สร้างตัวละครผู้เล่น (Abstaction & Encapsulation จาก Player class)
player = Player(50, 100) # เริ่มต้นที่ขอบซ้ายของจอ

clock = pygame.time.Clock() # สร้างตัวควบคุมเวลา (FPS)
running = True

# จัดการ Scene/State หลักของหน้าจอ
game_state = "MENU" 
prev_game_state = "MENU" # ไว้จำว่าต้องกด back ไปไหนเมื่ออยู่หน้า settings
main_menu = MainMenu(800, 500)
settings_menu = SettingsMenu(800, 500)
pause_menu = PauseMenu(800, 500)
player_name = ""

# ปุ่มเมนู/หยุดเกมชั่วคราวขณะเล่น (อยู่บนขวา)
in_game_menu_btn = pygame.Rect(710, 10, 80, 35)

while running:
    # 1. การจัดการ Event ปิดเกม
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # จัดการอีเวนต์ตามหน้าจอ
        if game_state == "MENU":
            action, data = main_menu.handle_event(event)
            if action == "play":
                player_name = data 
                player.name = player_name
                game_state = "GAME"
            elif action == "settings":
                game_state = "SETTINGS"
            elif action == "quit":
                running = False
        elif game_state == "PAUSED":
            action = pause_menu.handle_event(event)
            if action == "resume":
                game_state = "GAME"
            elif action == "settings":
                prev_game_state = "PAUSED"
                game_state = "SETTINGS"
            elif action == "quit":
                running = False # หรือสลับไปเป็น "MENU" ก็ได้ถ้าต้องการ
        elif game_state == "SETTINGS":
            action = settings_menu.handle_event(event)
            if action == "back":
                game_state = prev_game_state
        elif game_state == "GAME":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_game_menu_btn.collidepoint(event.pos):
                    game_state = "PAUSED"

    # ระบบกด ESC เพื่อสลับหยุดเกม/เล่นต่อ
    if event.type == pygame.KEYDOWN and game_state in ["GAME", "PAUSED"]:
        if event.key == pygame.K_ESCAPE:
            if game_state == "GAME":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                game_state = "GAME"

    # วาดหน้าเมนูถ้ายังไม่เริ่มเกม
    if game_state == "MENU":
        main_menu.draw(screen)
        pygame.display.update()
        clock.tick(settings_menu.fps)
        continue
    elif game_state == "SETTINGS":
        settings_menu.draw(screen)
        pygame.display.update()
        clock.tick(settings_menu.fps)
        continue
    elif game_state == "PAUSED":
        # ตอนพอกันกับวาดกรอบเกม
        pass # วาดเกมค้างไว้แล้วทับด้วย PauseMenu ด้านล่าง

    if game_state == "GAME":
        # 2. การจัดการ Input การกดค้างของผู้เล่น (เดินซ้าย, ขวา, สเปซบาร์, คลิก)
        keys = pygame.key.get_pressed()
        mouse_btns = pygame.mouse.get_pressed()
        
        # เก็บพิกัดเดิมไว้เช็คการชน (ไม่ให้เดินทะลุบอส)
        old_x = player.rect.x
        
        player.handle_input(keys, mouse_btns)
        
        # ป้องกันเดินทะลุบอสในฉาก 4
        if current_scene == 4 and current_boss and current_boss.is_alive and player.is_alive:
            if player.rect.colliderect(current_boss.rect):
                player._rect.x = old_x
                if hasattr(player, '_x'):
                    player._x = old_x

        # กด Z หรือ คลึกเมาส์ซ้าย เพื่อโจมตี
        if keys[pygame.K_z] or mouse_btns[0]:
            target = current_boss if current_scene == 4 else None
            player.attack(target)

        # 3. อัปเดตตรรกะและฟิสิกส์ต่างๆ ในเกม
        player.update(game_areas)
        if current_boss:
            current_boss.update(game_areas, player)

        old_scene = current_scene

    # การเปลี่ยนฉาก (ทะลุขวา) ไปฉากถัดไป
    if player.rect.right >= 820:
        if current_scene == 1:
            current_scene = 2
            bg, game_areas = load_scene(current_scene)
            player._rect.x = 10 
        elif current_scene == 2:
            current_scene = 3
            bg, game_areas = load_scene(current_scene)
            player._rect.x = 10 
        elif current_scene == 3:
            current_scene = 4
            bg, game_areas = load_scene(current_scene)
            player._rect.x = 10
            
        # การเดินย้อนกลับเปลี่ยนฉาก (ทะลุซ้าย)
        elif player.rect.left <= 0:
            if current_scene == 2:
                current_scene = 1
                bg, game_areas = load_scene(current_scene)
                player._rect.right = 790 
            elif current_scene == 3:
                current_scene = 2
                bg, game_areas = load_scene(current_scene)
                player._rect.right = 790
            elif current_scene == 4:
                current_scene = 3
                bg, game_areas = load_scene(current_scene)
                player._rect.right = 790

        # สร้าง Boss เมื่อเข้าสู่ฉาก 4 
        if current_scene != old_scene and current_scene == 4:
            if current_boss is None or not current_boss.is_alive:
                current_boss = MinotaurBoss(550, 0) # เกิดหล่นลงมาจากฟ้า
                current_boss_ui = BossUI(current_boss)

    # 4. วาดทุกอย่างลงบนหน้าจอ (เรียงลำดับจากหลังมาหน้า)
    # วาดฉากหลัง
    bg.draw()
    
    # วาดพื้นที่ทั้งหมด โดยใช้หลักการ Polymorphism เรียก method draw ทีเดียว
    for area in game_areas:
        area.draw(screen)

    # วาดตัวละครผู้เล่น
    player.draw(screen)

    # วาดบอสและ UI เมื่ออยู่ฉาก 4
    if current_scene == 4 and current_boss:
        current_boss.draw(screen)
        if current_boss_ui:
            current_boss_ui.draw(screen)

    # วาดปุ่มเข้าป๊อบอับเมนู (Pause Button)
    if game_state == "GAME":
        pygame.draw.rect(screen, (80, 80, 80), in_game_menu_btn, border_radius=5)
        btn_surf = pygame.font.SysFont("Arial", 16, bold=True).render("MENU", True, (255, 255, 255))
        screen.blit(btn_surf, btn_surf.get_rect(center=in_game_menu_btn.center))

    # แสดงผลแพ้ชนะ
    if not player.is_alive:
        font = pygame.font.SysFont("Arial", 60, bold=True)
        text = font.render("You Loose!", True, (255, 0, 0))
        text_rect = text.get_rect(center=(400, 250))
        screen.blit(text, text_rect)
    elif current_scene == 4 and current_boss and not current_boss.is_alive:
        font = pygame.font.SysFont("Arial", 60, bold=True)
        text = font.render("You Win!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(400, 250))
        screen.blit(text, text_rect)
        
    # วาดเมนูหยุดเกมทับถ้าอยู่ใน State PAUSED
    if game_state == "PAUSED":
        pause_menu.draw(screen)

    # อัปเดตหน้าจอหลักรวม
    pygame.display.update()
    
    # ควบคุมความเร็วของเกมให้อยู่ที่เฟรมเรตที่ตั้งค่าไว้
    clock.tick(settings_menu.fps)

pygame.quit()