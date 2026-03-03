import pygame
import os
from abc import ABC, abstractmethod
from background.back_g import background
from player import Player
from boss import MinotaurBoss, BossUI
from menu import MainMenu, SettingsMenu, PauseMenu, GameOverMenu, play_click_sound

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
pygame.mixer.init()

# โลดไฟล์เสียง
try:
    if os.path.exists("assets/sound/upside down grin2.ogg"):
        pygame.mixer.music.load("assets/sound/upside down grin2.ogg")
        pygame.mixer.music.set_volume(0.4)
    
    if os.path.exists("assets/sound/creatorshome-draw-a-sword-327726.mp3"):
        SPAWN_SOUND = pygame.mixer.Sound("assets/sound/creatorshome-draw-a-sword-327726.mp3")
        SPAWN_SOUND.set_volume(0.8)
    else:
        SPAWN_SOUND = None
except:
    SPAWN_SOUND = None

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("Jao ting nong")
screen.fill((255, 255, 255))

# อิงตามเดิมที่มีอยู่
bg = background(screen, "background/bg-1.jpg")

# =====================================================================
# ระบบเปลี่ยนแปลงฉาก (Scene Management)
# =====================================================================
# สร้างฟังก์ชันสำหรับโหลดฉากตามหมายเลข
def load_scene(scene_number, is_reset=False):
    if is_reset:
        return background(screen, "background/bg-1.jpg"), [
            WalkableArea(0, 410, 800, 90),
            ObstacleArea(350, 320, 50, 80)
        ]
        
    if scene_number == 1:
        # ฉากที่ 1
        new_bg = background(screen, "background/bg-1.jpg")
        new_areas = [
            WalkableArea(0, 410, 800, 90),       # พื้นดิน
            ObstacleArea(350, 320, 50, 80)       # กำแพงกั้นกลางฉาก
        ]
        return new_bg, new_areas
        
    elif scene_number == 2:
        # ฉากที่ 2
        new_bg = background(screen, "background/bg-2.jpg")
        new_areas = [
            # พื้นดินฉาก 2 อาจปรับระดับความสูงหรือสร้างสิ่งกีดขวางแบบใหม่ได้
            WalkableArea(0, 410, 800, 90),       # พื้นดิน
        ]
        return new_bg, new_areas
        
    elif scene_number == 3:
        # ฉากที่ 3
        new_bg = background(screen, "background/bg-3.jpg")
        new_areas = [
            # พื้นดินฉาก 3
            WalkableArea(0, 430, 800, 70),       # พื้นดิน
        ]
        return new_bg, new_areas
        
    elif scene_number == 4:
        # ฉากที่ 4
        new_bg = background(screen, "background/bg-4.jpg")
        new_areas = [
            # พื้นดินฉาก 4 (สะพานศิลาและฐาน)
            WalkableArea(0, 395, 800, 105),       # พื้นดิน
        ]
        return new_bg, new_areas

current_scene = 1
bg, game_areas = load_scene(current_scene)
current_boss = None
current_boss_ui = None
current_monsters = []  # OCP: รองรับมอนสเตอร์อื่นๆ นอกจากบอส
health_potions = [] # ลิสต์เก็บขวดเลือดที่ดรอปในฉาก

# ฟังก์ชันหุ้มสำหรับการเปลี่ยนฉากพร้อมเอฟเฟกต์
def change_scene(scene_num, player_new_x=None, player_new_right=None):
    global bg, game_areas, current_scene, health_potions
    
    # 1. เล่นไฟล์เสียงเปลี่ยนฉาก (ถ้ามี)
    try:
        if os.path.exists("assets/sound/Menu Selection Click.wav"):
            pygame.mixer.Sound("assets/sound/Menu Selection Click.wav").play()
    except:
        pass
        
    # 2. ทำเอฟเฟกต์ Fade Out
    fade_surf = pygame.Surface((800, 500))
    fade_surf.fill((0, 0, 0))
    for alpha in range(0, 255, 15):
        fade_surf.set_alpha(alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)
        
    # 3. โหลดข้อมูลฉากใหม่
    current_scene = scene_num
    bg, game_areas = load_scene(current_scene)
    health_potions = [] # ล้างไอเทมฉากเก่า
    
    if player_new_x is not None:
        player._rect.x = player_new_x
    if player_new_right is not None:
        player._rect.right = player_new_right
        
    # 4. ทำเอฟเฟกต์ Fade In
    for alpha in range(255, 0, -15):
        bg.draw()
        for area in game_areas: area.draw(screen)
        player.draw(screen)
        fade_surf.set_alpha(alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

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

game_over_menu = None  # สต็อกเก็บเมนูจบเกมเมื่อเกิดเหตุการณ์

# ฟังก์ชันรีเซ็ตเกม
def reset_game():
    global current_scene, bg, game_areas, player, current_boss, current_boss_ui, game_state, game_over_menu
    current_scene = 1
    bg, game_areas = load_scene(1, is_reset=True)
    player = Player(50, 100)
    if player_name != "":
        player.name = player_name
    current_boss = None
    current_boss_ui = None
    current_monsters = []
    game_state = "GAME"
    game_over_menu = None
    
    # เกิดใหม่เล่นเสียงชักดาบ และเริ่มเพลงใหม่
    if settings_menu.sound_on:
        if SPAWN_SOUND:
            SPAWN_SOUND.play()
        try:
            pygame.mixer.music.play(-1)
        except:
            pass

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
                
                # เริ่มเกมเล่นเสียงชักดาบ และเปิดเพลงฉากหลัง (Loop бесконечно)
                if settings_menu.sound_on:
                    if SPAWN_SOUND:
                        SPAWN_SOUND.play()
                    try:
                        pygame.mixer.music.play(-1)
                    except:
                        pass
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
                    play_click_sound()
                    game_state = "PAUSED"
        elif game_state == "GAME_OVER":
            if game_over_menu:
                action = game_over_menu.handle_event(event)
                if action == "play_again":
                    reset_game()
                elif action == "quit":
                    running = False

    # ระบบกด ESC เพื่อสลับหยุดเกม/เล่นต่อ
    if event.type == pygame.KEYDOWN and game_state in ["GAME", "PAUSED"]:
        if event.key == pygame.K_ESCAPE:
            if game_state == "GAME":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                game_state = "GAME"

    # ระบบจัดการเสียงจากเมนูตั้งค่า
    if not settings_menu.sound_on:
        pygame.mixer.music.pause()
    else:
        if game_state in ["GAME", "PAUSED"]:
            pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause() # ไม่เล่นเพลงในหน้าเมนูหลัก

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
                    
        # ป้องกันเดินทะลุมอนสเตอร์ตัวอื่นๆ 
        for m in current_monsters:
            if m.is_alive and player.is_alive and player.rect.colliderect(m.rect):
                player._rect.x = old_x
                if hasattr(player, '_x'):
                    player._x = old_x


        # เลือกท่าโจมตี (SRP: หน้าที่รับคำสั่งคีย์บอร์ดแล้วส่งให้ Player ดำเนินการ)
        # ทำการหาเป้าหมายโจมตี (Polymorphism: เป้าหมายอะไรก็ได้ที่สืบทอดจาก Enemy/Character และมี take_damage)
        target = None
        if current_scene == 4:
            target = current_boss
        elif current_monsters:
            # เลือกเป้าหมายตัวแรกที่ยังมีชีวิต (อาจขยายเป็นเลือกตัวที่ใกล้ที่สุดภายหลัง)
            target = next((m for m in current_monsters if m.is_alive), None)

        if keys[pygame.K_c] or (keys[pygame.K_LSHIFT] and mouse_btns[0]):
            # ท่าที่ 2: กด C หรือ Shift+คลิกซ้าย
            player.attack(target, attack_type=2)
        elif keys[pygame.K_z] or mouse_btns[0]:
            # ท่าที่ 1: กด Z หรือ คลิกซ้ายปกติ
            player.attack(target, attack_type=1)

        # 3. อัปเดตตรรกะและฟิสิกส์ต่างๆ ในเกม
        player.update(game_areas)
        if current_boss:
            current_boss.update(game_areas, player)
            
        for m in current_monsters:
            m_was_alive = m.is_alive
            m.update(game_areas, player)
            # ระบบดรอปขวดเลือดเมื่อมอนสเตอร์ตาย (ข้อ 4)
            if m_was_alive and not m.is_alive:
                import random
                if random.random() < 0.5: # โอกาสดรอป 50%
                    health_potions.append(pygame.Rect(m.rect.centerx, m.rect.bottom - 20, 20, 20))

        # ตรวจสอบการเก็บขวดเลือด
        for potion in health_potions[:]:
            if player.rect.colliderect(potion):
                player.heal(30) # เพิ่มเลือด 30 หน่วย
                health_potions.remove(potion)
                try:
                    if os.path.exists("assets/sound/Inventory_Open_01.wav"):
                        pygame.mixer.Sound("assets/sound/Inventory_Open_01.wav").play()
                except:
                    pass

        old_scene = current_scene

    # การเปลี่ยนฉาก (ทะลุขวา) ไปฉากถัดไป
    if player.rect.right >= 820:
        if current_scene == 1:
            change_scene(2, player_new_x=10)
        elif current_scene == 2:
            change_scene(3, player_new_x=10)
        elif current_scene == 3:
            change_scene(4, player_new_x=10)
            
    # เดินย้อนกลับเปลี่ยนฉาก (ทะลุซ้าย)
    elif player.rect.left <= 0:
        if current_scene == 2:
            change_scene(1, player_new_right=790)
        elif current_scene == 3:
            change_scene(2, player_new_right=790)
        if current_scene == 4:
            change_scene(3, player_new_right=790)

    # สร้าง Boss เมื่อเข้าสู่ฉาก 4 
    if current_scene != old_scene and current_scene == 4:
        if current_boss is None or not current_boss.is_alive:
            from boss import MinotaurBoss, BossUI
            current_boss = MinotaurBoss(550, 0) # เกิดหล่นลงมาจากฟ้า
            current_boss_ui = BossUI(current_boss)

    # สร้างมอนสเตอร์ตัวอื่นๆ ตามฉากต่างๆ 
    if current_scene != old_scene and current_scene == 3:
        if not any(m.is_alive for m in current_monsters):
            from monster import Necromancer
            # สร้าง Necromancer มาโผล่ที่ฉาก 3
            current_monsters = [Necromancer(600, 300)]

    # 4. วาดทุกอย่างลงบนหน้าจอ (เรียงลำดับจากหลังมาหน้า)
    # วาดฉากหลัง
    bg.draw()
    
    # วาดพื้นที่ทั้งหมด โดยใช้หลักการ Polymorphism เรียก method draw ทีเดียว
    for area in game_areas:
        area.draw(screen)

    # วาดมอนสเตอร์ปกติทั่วๆ ไป (Polymorphism: วาดด้วย pattern เดียวกัน)
    for m in current_monsters:
        m.draw(screen)

    # วาดขวดเลือด (ข้อ 4)
    for potion in health_potions:
        pygame.draw.rect(screen, (255, 0, 0), potion, border_radius=5) # ขวดสีแดง
        pygame.draw.rect(screen, (255, 255, 255), potion, 1, border_radius=5) # ขอบสีขาว

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

    # ตรวจสอบการพ่ายแพ้และชัยชนะ (เปลี่ยน State ไปที่ GAME_OVER)
    if not player.is_alive and game_state == "GAME":
        if not game_over_menu: # สร้างเมนูเมื่อตายครั้งแรก
            game_over_menu = GameOverMenu(800, 500, title="You Loose!", color=(255, 0, 0))
            game_state = "GAME_OVER"
    elif current_scene == 4 and current_boss and not current_boss.is_alive and game_state == "GAME":
        if not game_over_menu: # สร้างเมนูเมื่อขนะครั้งแรก
            game_over_menu = GameOverMenu(800, 500, title="You Win!", color=(0, 255, 0))
            game_state = "GAME_OVER"

    # วาดเมนู Game Over ถ้าอยู่ใน State GAME_OVER
    if game_state == "GAME_OVER" and game_over_menu:
        game_over_menu.draw(screen)
        
    # วาดเมนูหยุดเกมทับถ้าอยู่ใน State PAUSED
    if game_state == "PAUSED":
        pause_menu.draw(screen)

    # อัปเดตหน้าจอหลักรวม
    pygame.display.update()
    
    # ควบคุมความเร็วของเกมให้อยู่ที่เฟรมเรตที่ตั้งค่าไว้
    clock.tick(settings_menu.fps)

pygame.quit()