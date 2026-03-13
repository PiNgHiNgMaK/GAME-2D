import pygame
import os
import random
from abc import ABC, abstractmethod
from background.back_g import background
from player import Player
from boss import DemonSlimeBoss, BossUI
from menu import MainMenu, SettingsMenu, PauseMenu, GameOverMenu, play_click_sound
from puzzle import DeflectorPuzzleManager
from story import DialogueManager, STORY_DATA
from effects import FloatingText, Particle, ScreenShake, AmbientParticle, SlashFX, ImpactParticle # เพิ่ม SlashFX และ ImpactParticle
import math

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
        # แผนที่ปกติไม่ต้องการให้เห็น Area (ใช้อันดับพิกัดในการคำนวณเดิน)
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
# ลด Audio Latency (ความดีเลย์ของเสียง) ให้เหลือน้อยที่สุด
pygame.mixer.pre_init(44100, -16, 2, 128) 
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(64) # เพิ่มช่องสัญญาณเสียงให้มากขึ้น

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
        
    if os.path.exists("assets/sound/1.mp3"):
        HIT_SOUND = pygame.mixer.Sound("assets/sound/1.mp3")
        HIT_SOUND.set_volume(0.6)
    else:
        HIT_SOUND = None

    if os.path.exists("assets/sound/2.mp3"):
        PLAYER_HURT_SOUND = pygame.mixer.Sound("assets/sound/2.mp3")
        PLAYER_HURT_SOUND.set_volume(0.7)
    else:
        PLAYER_HURT_SOUND = None
except:
    SPAWN_SOUND = None
    HIT_SOUND = None
    PLAYER_HURT_SOUND = None

screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption("The Echo of the Abyss: Reversed Fate")
game_surface = pygame.Surface((800, 500)) # พื้นผิวจำลองสำหรับวาดเอฟเฟกต์ Screen Shake
screen.fill((255, 255, 255))

# อิงตามเดิมที่มีอยู่
bg = background(screen, [("background/bg-1.jpg", 1.0)])
current_bgm = ""

def change_bgm(file_path, volume=0.4):
    global current_bgm
    if current_bgm == file_path:
        return
    try:
        if os.path.exists(file_path):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            current_bgm = file_path
    except:
        pass

def apply_game_settings():
    """อัปเดตเสียงและค่าต่างๆ ตาม Settings Menu"""
    pygame.mixer.music.set_volume(settings_menu.music_volume)
    vol = settings_menu.sfx_volume
    if SPAWN_SOUND: SPAWN_SOUND.set_volume(vol)
    if HIT_SOUND: HIT_SOUND.set_volume(vol)
    if PLAYER_HURT_SOUND: PLAYER_HURT_SOUND.set_volume(vol)
    
    # อัปเดตเสียงมอนสเตอร์ที่มีอยู่
    for m in current_monsters:
        if hasattr(m, '_attack_sound') and m._attack_sound:
            m._attack_sound.set_volume(vol * 0.7)


def create_monster(m_class, x, y):
    """สร้างมอนสเตอร์สแตนดาร์ด"""
    m = m_class(x, y)
    if hasattr(m, '_attack_sound') and m._attack_sound:
        m._attack_sound.set_volume(settings_menu.sfx_volume * 0.7)
    return m

# =====================================================================
# ระบบเปลี่ยนแปลงฉาก (Scene Management)
# =====================================================================
def load_scene(scene_number, is_reset=False):
    # ลบส่วน is_reset เดิมทิ้งเพื่อให้ใช้ Logic ของฉากที่ 1 แบบ Parallax เหมือนเดิม
    if scene_number == 1:
        # ฉากที่ 1: NightForest Parallax (เลื่อนตามกล้อง)
        new_bg = background(game_surface, [
            ("background/NightForest/Layers/1.png", 0.05),
            ("background/NightForest/Layers/2.png", 0.1),
            ("background/NightForest/Layers/3.png", 0.2),
            ("background/NightForest/Layers/4.png", 0.3),
            ("background/NightForest/Layers/5.png", 0.4),
            ("background/NightForest/Layers/6.png", 0.6)
        ])
        new_areas = [
            WalkableArea(0, 410, 2000, 90),       # ขยายพื้นดินให้ยาวออกไปนอกจอ
            ObstacleArea(350, 320, 50, 80)
        ]
        return new_bg, new_areas
        
    elif scene_number == 2:
        # ฉากที่ 2: กลับมาใช้พื้นระนาบเดียวเพื่อความสะอาดในการแก้พัซเซิลรูน
        new_bg = background(game_surface, [("background/bg-2.jpg", 1.0)]) 
        new_areas = [
            WalkableArea(0, 410, 800, 90),
        ]
        return new_bg, new_areas
        
    elif scene_number == 3:
        # ฉากที่ 3: ปรับพื้นขึ้นสูง (y=360) และตั้งความเร็วเป็น 1.0
        new_bg = background(game_surface, [("background/bg-3.jpg", 1.0)])
        new_areas = [
            WalkableArea(0, 360, 800, 140), # พื้นท้องพระโรง
        ]
        return new_bg, new_areas
        
    elif scene_number == 4:
        # ฉากที่ 4: ปรับพื้น (y=380) และตั้งความเร็วเป็น 1.0
        new_bg = background(game_surface, [("background/bg-4.jpg", 1.0)])
        new_areas = [
            WalkableArea(0, 380, 800, 120),
        ]
        return new_bg, new_areas

current_scene = 1
bg, game_areas = load_scene(current_scene)
current_boss = None
current_boss_ui = None
current_monsters = []  
health_potions = [] 
scene_monster_data = {}   
scene_monsters_cleared = set()  
current_puzzle = None 
old_scene = -1  
dialogue_manager = DialogueManager(800, 500) 

# ฟังก์ชันหุ้มสำหรับการเปลี่ยนฉากพร้อมเอฟเฟกต์
def change_scene(scene_num, player_new_x=None, player_new_right=None):
    global bg, game_areas, current_scene, health_potions, current_monsters, current_boss, current_boss_ui, scene_monster_data, scene_monsters_cleared, current_puzzle
    
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
        pygame.event.pump() # ป้องกัน "Not Responding"
        pygame.time.delay(10)
        
    # 3. บันทึกมอนที่ยังมีชีวิตก่อนออกจากฉาก
    alive_mons = [m for m in current_monsters if m.is_alive]
    if alive_mons:
        scene_monster_data[current_scene] = alive_mons  # เก็บมอนที่ยังอยู่
    else:
        scene_monster_data.pop(current_scene, None)  # ไม่มีมอนเหลือ
        scene_monsters_cleared.add(current_scene)    # ล็อค ไม่ให้ respawn

    # โหลดข้อมูลฉากใหม่
    current_scene = scene_num
    bg, game_areas = load_scene(current_scene)
    
    # แสดงข้อความเนื้อเรื่องตามฉาก
    story_key = f"SCENE_{current_scene}_START"
    if story_key in STORY_DATA:
        dialogue_manager.show_message(STORY_DATA[story_key])
    health_potions = []    # ล้างไอเทมฉากเก่า
    current_monsters = []  # ล้างมอนสเตอร์ฉากเก่า
    current_puzzle = None  # ล้างพัซเซิลฉากเก่า
    health_potions = []    # ล้างไอเทมฉากเก่า
    # ล้างบอสถ้าออกจากฉาก 4 
    if scene_num != 4:
        current_boss = None
        current_boss_ui = None
    
    if player_new_x is not None:
        player._rect.x = player_new_x
    if player_new_right is not None:
        player._rect.right = player_new_right
        
    # 4. ทำเอฟเฟกต์ Fade In
    for alpha in range(255, 0, -15):
        bg.draw(player.rect.x)
        for area in game_areas: area.draw(screen)
        player.draw(screen)
        fade_surf.set_alpha(alpha)
        screen.blit(fade_surf, (0, 0))
        pygame.display.update()
        pygame.event.pump() # ป้องกัน "Not Responding"
        pygame.time.delay(10)

# สร้างตัวละครผู้เล่น (Abstaction & Encapsulation จาก Player class)
player = Player(50, 350) # เริ่มต้นที่พื้น (410 - 60)
old_player_hp = player.current_hp

# ระบบเอฟเฟกต์ (Juice)
floating_texts = []
particles = []
impact_particles = [] # สำหรับเลือดและประกายไฟ
ambient_particles = [] # เพิ่มรายการอนุภาคบรรยากาศ
slash_fx_list = [] # เพิ่มวิถีดาบ
shockwaves = [] # คลื่นกระแทก parry
dust_particles = [] # ฝุ่นกระโดด/ลงพื้น
screen_shake = ScreenShake()

# ระบบ Lighting (Vignette Spotlight)
vignette_overlay = pygame.Surface((800, 500), pygame.SRCALPHA)
light_mask = pygame.Surface((600, 600), pygame.SRCALPHA)
# วาด mask เตรียมไว้ (วงกลมสว่างกลางจางไปหาขอบ)
for r in range(300, 0, -2):
    # ยิ่งเข้าใกล้จุดศูนย์กลาง (รัศมีน้อย) ยิ่งลบความมืดออกมาก
    alpha = int(180 * (1 - (r / 300)**2)) 
    pygame.draw.circle(light_mask, (0, 0, 0, alpha), (300, 300), r)

# ระบบ Hit Stop (ตัวเกมหยุดนิ่งชั่วขณะเมื่อมีการปะทะ)
hit_stop_timer = 0
# ระบบ Slow Motion (สโลว์จังหวะสังหาร)
slow_mo_timer = 0
boss_slomo_triggered = False

# ตัวแปรสำหรับฉากจบ
ending_step = 0
ending_timer = 0
ending_fade_alpha = 0
morning_bg = None

# ระบบเปลี่ยนฉากแบบนุ่มนวล (Smooth Transition)
is_scene_fading = False
scene_fade_mode = "out" # "out" สำหรับมืดลง, "in" สำหรับสว่างขึ้น
scene_fade_alpha = 0

# ระบบ Low HP Pulse (ขอบแดงกระพริบเมื่อเลือดต่ำ)
low_hp_overlay = pygame.Surface((800, 500), pygame.SRCALPHA)
low_hp_timer = 0
transition_player_new_right = None

# ระบบ Camera Focus (สำหรับสั่นหรือเคลื่อนตาม)
camera_scroll = [0, 0]

# ระบบ Cinematic & Pause Effect
death_cinematic_timer = 0
pause_bg_surf = None # เก็บภาพเบลอตอนหยุดเกม

clock = pygame.time.Clock() # สร้างตัวควบคุมเวลา (FPS)
running = True

# จัดการ Scene/State หลักของหน้าจอ
game_state = "MENU" 
prev_game_state = "MENU" # ไว้จำว่าต้องกด back ไปไหนเมื่ออยู่หน้า settings
main_menu = MainMenu(800, 500)
settings_menu = SettingsMenu(800, 500)
pause_menu = PauseMenu(800, 500)
apply_game_settings() 
player_name = ""

# ปุ่มเมนู/หยุดเกมชั่วคราวขณะเล่น (อยู่บนขวา)
in_game_menu_btn = pygame.Rect(710, 10, 80, 35)

game_over_menu = None  # สต็อกเก็บเมนูจบเกมเมื่อเกิดเหตุการณ์

# ฟังก์ชันรีเซ็ตเกม
def reset_game():
    global current_scene, bg, game_areas, player, current_boss, current_boss_ui, game_state, game_over_menu, current_monsters, scene_monster_data, scene_monsters_cleared, old_scene, current_puzzle, health_potions
    current_scene = 1
    bg, game_areas = load_scene(1, is_reset=True)
    player = Player(50, 350)
    if player_name != "":
        player.name = player_name
    current_boss = None
    current_boss_ui = None
    current_monsters = []
    scene_monster_data = {}          # รีเซ็ตข้อมูลมอนเมื่อเริ่มเกมใหม่
    scene_monsters_cleared = set()   # รีเซ็ต flag เมื่อเริ่มเกมใหม่
    current_puzzle = None            # รีเซ็ตพัซเซิล
    health_potions = []             # ล้างขวดเลือด
    global old_scene
    old_scene = -1                   # บังคับให้ระบบมองว่าเปลี่ยนฉาก เพื่อเสกมอนฉาก 1
    
    game_state = "GAME"
    game_over_menu = None
    
    # แสดงเนื้อเรื่องเปิดตอนเริ่มเกมใหม่
    dialogue_manager.show_message(STORY_DATA["SCENE_1_START"])
    
    # เกิดใหม่เล่นเสียงชักดาบ และเริ่มเพลงใหม่
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
            
        # จัดการอีเวนต์ของ Dialogue (ถ้ามีบทพูดอยู่)
        # ถ้ากดปิด จะได้ค่า True กลับมา (แต่เราใช้เช็คใน update ด้านล่างแทน)
        dialogue_manager.handle_event(event)
            
        # จัดการอีเวนต์ตามหน้าจอ
        if game_state == "MENU":
            action, data = main_menu.handle_event(event)
            if action == "play":
                player_name = data 
                player.name = player_name
                game_state = "GAME"
                
                # เริ่มเกมเล่นเสียงชักดาบ และเปิดเพลงฉากหลัง (Loop бесконечно)
                if SPAWN_SOUND:
                    SPAWN_SOUND.play()
                try:
                    pygame.mixer.music.play(-1)
                except:
                    pass
                
                # แสดงเนื้อเรื่องเปิดตอนเริ่มเกม
                dialogue_manager.show_message(STORY_DATA["SCENE_1_START"])
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
                apply_game_settings() 
                game_state = prev_game_state
        elif game_state == "GAME":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_game_menu_btn.collidepoint(event.pos):
                    play_click_sound()
                    game_state = "PAUSED"
                    # สร้างภาพเบลอทันทีที่กดหยุด
                    small_surf = pygame.transform.smoothscale(game_surface, (160, 100))
                    pause_bg_surf = pygame.transform.smoothscale(small_surf, (800, 500))
                    # เพิ่มความมืดลงในภาพเบลอ
                    dark = pygame.Surface((800, 500), pygame.SRCALPHA)
                    dark.fill((0, 0, 0, 100))
                    pause_bg_surf.blit(dark, (0, 0))
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
                    # สร้างภาพเบลอ
                    small_surf = pygame.transform.smoothscale(game_surface, (160, 100))
                    pause_bg_surf = pygame.transform.smoothscale(small_surf, (800, 500))
                    dark = pygame.Surface((800, 500), pygame.SRCALPHA)
                    dark.fill((0, 0, 0, 100))
                    pause_bg_surf.blit(dark, (0, 0))
                elif game_state == "PAUSED":
                    game_state = "GAME"

    # ระบบจัดการเสียง (จัดการ Pause/Unpause ตามสถานะเกม)
    if game_state in ["GAME", "PAUSED", "ENDING"]:
        try:
            # ถ้าเพลงหยุดอยู่ ให้เล่นต่อ (ยกเว้นกด Mute ใน slider ที่วอลลุ่มจะเป็น 0)
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
        except: pass
    else:
        # ในหน้าเมนูอื่นๆ ปล่อยให้ระบบ BGM จัดการเอง
        pass

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

    # อัปเดตอนุภาคบรรยากาศ (Ambient Particles)
    if game_state in ["GAME", "ENDING"]:
        # สุ่มเกิดตามฉาก
        if len(ambient_particles) < 30:
            if game_state == "ENDING":
                ambient_particles.append(AmbientParticle(random.randint(0, 800), random.randint(0, 500), "sparkle"))
            elif current_scene == 1:
                ambient_particles.append(AmbientParticle(random.randint(-50, 850), -20, "leaf"))
            elif current_scene == 2:
                ambient_particles.append(AmbientParticle(random.randint(0, 800), random.randint(0, 500), "glow_orb"))
            elif current_scene == 3:
                ambient_particles.append(AmbientParticle(random.randint(0, 800), 520, "magic"))
            elif current_scene == 4:
                # บอส: ละอองเถ้าถ่านสีเทา/แดง
                color = (100, 100, 100) if random.random() > 0.2 else (200, 50, 0)
                ambient_particles.append(AmbientParticle(random.randint(0, 800), 520, "magic", color=color))

    for ap in ambient_particles[:]:
        ap.update()
        if not ap.alive: ambient_particles.remove(ap)

    # จัดการการเล่นเพลงตามสถานะ
    if game_state == "MENU":
        change_bgm("assets/sound/upside down grin2.ogg", 0.3)
    elif game_state == "ENDING":
        # ถ้ามีเพลงอื่นให้เปลี่ยนตรงนี้
        pass
    elif game_state == "GAME":
        if hit_stop_timer > 0:
            hit_stop_timer -= 1
        # ตรวจสอบว่ามีบทสนทนาเด้งอยู่หรือไม่ ถ้ามีให้ Freeze เกม (ข้ามการทำ Input และ Update)
        elif not dialogue_manager.is_showing:
            # 2. การจัดการ Input การกดค้างของผู้เล่น (เดินซ้าย, ขวา, สเปซบาร์, คลิก)
            keys = pygame.key.get_pressed()
            mouse_btns = pygame.mouse.get_pressed()
            
            player.handle_input(keys, mouse_btns)

            # เลือกท่าโจมตี (SRP: หน้าที่รับคำสั่งคีย์บอร์ดแล้วส่งให้ Player ดำเนินการ)
            target = None
            if current_scene == 4:
                target = current_boss
            elif current_monsters:
                # เลือกเป้าหมายที่อยู่ใกล้ที่สุดและไม่ได้กำลังตาย
                living_monsters = [m for m in current_monsters if m.is_alive and getattr(m, '_action', '') != "dead"]
                if living_monsters:
                    # หาตัวที่อยู่ใกล้ที่สุด
                    target = min(living_monsters, key=lambda m: abs(m.rect.centerx - player.rect.centerx))

            if keys[pygame.K_c] or (keys[pygame.K_LSHIFT] and mouse_btns[0]):
                if player.attack(target, attack_type=2):
                    slash_fx_list.append(SlashFX(player.rect.centerx, player.rect.centery, player._facing_right))
            elif keys[pygame.K_z] or mouse_btns[0]:
                if player.attack(target, attack_type=1):
                    slash_fx_list.append(SlashFX(player.rect.centerx, player.rect.centery, player._facing_right))

            # 3. อัปเดตตรรกะและฟิสิกส์ทั้งหมด
            player_old_hp = player.current_hp
            player.update(game_areas, dust_list=dust_particles)
            
            # อัปเดตบอส
            if current_boss and current_scene == 4:
                if not hasattr(current_boss, '_last_hp'): current_boss._last_hp = current_boss.current_hp
                boss_old_hp = current_boss._last_hp
                current_boss.update(game_areas, player, shockwave_list=shockwaves)
                
                if current_boss.current_hp < boss_old_hp:
                    hit_stop_timer = 5 
                    if HIT_SOUND: HIT_SOUND.play()
                    for _ in range(8):
                        impact_particles.append(ImpactParticle(current_boss.rect.centerx, current_boss.rect.centery, color=(150, 0, 200)))
                
                current_boss._last_hp = current_boss.current_hp
                
            # อัปเดตมอนสเตอร์
            for m in current_monsters:
                if not hasattr(m, '_last_hp'): m._last_hp = m.current_hp
                m_old_hp = m._last_hp
                m.update(game_areas, player, shockwave_list=shockwaves)
                
                if m.current_hp < m_old_hp:
                    hit_stop_timer = 3 
                    if HIT_SOUND: HIT_SOUND.play()
                    p_color = (255, 0, 0) if "Wizard" in m.name else (50, 0, 50)
                    for _ in range(5):
                        impact_particles.append(ImpactParticle(m.rect.centerx, m.rect.centery, color=p_color))
                
                    screen_shake.trigger(10, 0.3)
                    
                    # ระบบดรอปขวดเลือด (Health Potion) เมื่อมอนสเตอร์ตาย
                    if m.current_hp <= 0 and m_old_hp > 0:
                        # การันตี Evil Wizard ดรอป 100%, มอนสเตอร์ทั่วไปดรอป 20%
                        drop_chance = 1.0 if "Wizard" in m.name else 0.2
                        if random.random() < drop_chance:
                            # บันทึกตำแหน่งดรอป (ให้กองที่พื้นพอดี)
                            potion_rect = pygame.Rect(m.rect.centerx - 10, m.rect.bottom - 20, 20, 20)
                            health_potions.append(potion_rect)

                    # แก้ไข: มอนต้องตายถึงโชว์เนื้อเรื่อง
                    if current_scene == 3 and m.current_hp <= 0 and m_old_hp > 0 and "Wizard" in m.name:
                         from story import STORY_DATA
                         dialogue_manager.show_message(STORY_DATA["WIZARD_DEFEATED"])
                
                m._last_hp = m.current_hp


            # อัปเดตพัซเซิล (ถ้ามี) ก่อนเอาไปเช็ค HP
            if current_puzzle:
                current_puzzle.update(player, game_areas)

            # ตรวจสอบหลังจากอัปเดตทั้งหมด: ผู้เล่นโดนโจมตีหรือฮีล?
            if player.current_hp < player_old_hp:
                hit_diff = int(player_old_hp - player.current_hp)
                floating_texts.append(FloatingText(player.rect.centerx, player.rect.top - 20, f"-{hit_diff}", (255, 50, 50), size=28))
                if settings_menu.screen_shake_on: screen_shake.trigger(25, 0.5) 
                if PLAYER_HURT_SOUND: PLAYER_HURT_SOUND.play()
                for _ in range(6):
                    impact_particles.append(ImpactParticle(player.rect.centerx, player.rect.centery, color=(200, 0, 0)))
                hit_stop_timer = 6 
            elif player.current_hp > player_old_hp:
                heal_diff = int(player.current_hp - player_old_hp)
                floating_texts.append(FloatingText(player.rect.centerx, player.rect.top - 20, f"+{heal_diff}", (50, 255, 50), size=28))

            # ตรวจสอบการเก็บขวดเลือด
            for potion in health_potions[:]:
                if player.rect.colliderect(potion):
                    player.heal(50) # เพิ่มการฮีลเป็น 50 หน่วย
                    if HIT_SOUND: HIT_SOUND.play() # ใช้เสียง Hit เป็นเสียงเก็บชั่วคราว
                    health_potions.remove(potion)

            # --- ระบบ Juice ---
            old_player_hp = player.current_hp

            # 2. Particles ตอนโจมตี (Sword Trail)
            if player.is_attacking:
                for _ in range(2):
                    particles.append(Particle(player.rect.centerx + random.randint(-30, 30), player.rect.centery + random.randint(-30, 30)))

            # อัปเดตวิถีดาบ
            for sfx in slash_fx_list[:]:
                # ให้วิถีดาบขยับตามตัวผู้เล่นเล็กน้อย (หรือถ้าจะเอาแบบค้างที่พิกัดเดิมก็เอา player_pos ออก)
                sfx.update()
                if not sfx.alive: slash_fx_list.remove(sfx)

            # อัปเดตเอฟเฟกต์
            for ft in floating_texts[:]:
                ft.update()
                if not ft.alive: floating_texts.remove(ft)
            for p in particles[:]:
                p.update()
                if not p.alive: particles.remove(p)
            for ip in impact_particles[:]:
                ip.update()
                if not ip.alive: impact_particles.remove(ip)
            for sw in shockwaves[:]:
                sw.update()
                if not sw.alive: shockwaves.remove(sw)
            for dp in dust_particles[:]:
                dp.update()
                if not dp.alive: dust_particles.remove(dp)
            
        # การเปลี่ยนฉาก (ทะลุขวา) ไปฉากถัดไป
        if player.rect.right >= 820:
            if current_scene == 1:
                # ต้องฆ่ามอนสเตอร์ก่อนถึงจะไปต่อได้
                has_alive_monsters = any(m.is_alive for m in current_monsters)
                if not has_alive_monsters:
                    scene_monsters_cleared.add(1)
                    change_scene(2, player_new_x=10)
                else:
                    player._rect.right = 819
            elif current_scene == 2:
                if current_puzzle and current_puzzle.is_cleared:
                    change_scene(3, player_new_x=10)
                else:
                    player._rect.right = 819
            elif current_scene == 3:
                has_alive_monsters = any(m.is_alive for m in current_monsters)
                if not has_alive_monsters:
                    change_scene(4, player_new_x=10)
                else:
                    player._rect.right = 819

        # เดินย้อนกลับเปลี่ยนฉาก (ทะลุซ้าย)
        if player.rect.left <= -20:
            if current_scene == 2:
                change_scene(1, player_new_right=790)
            elif current_scene == 3:
                change_scene(2, player_new_right=790)
            elif current_scene == 4:
                change_scene(3, player_new_right=790)

    # จัดการฉากจบ (ENDING)
    if game_state == "ENDING":
        ending_timer += 1
        # พ่นอนุภาคแสงสีทอง
        if ending_timer % 10 == 0:
            particles.append(Particle(random.randint(0, 800), 500, color=(255, 215, 0)))
        
        if ending_step == 0: # เริ่มฉากจบ
            # ปรับตำแหน่งผู้เล่นให้เหยียบพื้นและอยู่กึ่งกลางเยื้องซ้าย
            player._rect.bottom = 440
            player._rect.x = 200
            player._is_moving = False
            player._is_running = False
            player._facing_right = True # หันหน้าไปหาพระอาทิตย์
            
            # โหลดพื้นหลังแบบเช้า
            morning_bg = background(game_surface, [("C:\\Users\\ASUS\\.gemini\\antigravity\\brain\\51ce651b-fc1c-4e36-9dd1-dde4c702ed04\\morning_forest_ending_1773329692151.png", 1.0)])
            bg = morning_bg # เปลี่ยนฉากหลังหลักเป็นตอนเช้าถาวร
            dialogue_manager.show_message(STORY_DATA["ENDING_DAWN"])
            ending_step = 1
            
            # เริ่ม Fade In (จากขาวหรือดำ)
            ending_fade_alpha = 255 
        
        # ปรับอัปเดตเอฟเฟกต์ (เพราะอยู่นอกบล็อค GAME)
        for ft in floating_texts[:]:
            ft.update()
            if not ft.alive: floating_texts.remove(ft)
        for p in particles[:]:
            p.update()
            if not p.alive: particles.remove(p)

        # อนุญาตให้ผู้เล่นเดินเองในฉากจบ หลังจากคุยจบแล้ว
        if not dialogue_manager.is_showing:
            keys = pygame.key.get_pressed()
            # เดินด้วยความเร็วที่สม่ำเสมอ
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player._rect.x += 3
                player._is_moving = True
            else:
                player._is_moving = False
            
            # อัปเดตฟิสิกส์ให้ตัวละครยืนบนพื้น
            player.update([WalkableArea(0, 440, 2000, 60)])
            
            # Fade In (ค่อยๆ ปรากฏฉาก)
            if ending_step == 1 and ending_fade_alpha > 0:
                ending_fade_alpha -= 5
            
            # print(f"ENDING XP: {player._rect.x}") # Debug
            
            # จุดจบเรื่อง (เดินผ่านหน้าพระอาทิตย์ไป)
            if player._rect.x > 500 and ending_step != 2: 
                ending_step = 2 # เริ่ม Fade Out
                ending_fade_alpha = 0
                
        if ending_step == 2:
            ending_fade_alpha += 5 
            if ending_fade_alpha >= 255:
                ending_fade_alpha = 255
                if not game_over_menu:
                    game_over_menu = GameOverMenu(800, 500, title="THE ADVENTURE CLEARED!", color=(255, 215, 0))
                    # เพิ่มข้อความขอบคุณ
                    floating_texts.append(FloatingText(400, 450, "Thank you for playing 'The Echo of the Abyss'", (255, 255, 255), size=20))
                    game_state = "GAME_OVER"

    # สร้าง Boss เมื่อเข้าสู่ฉาก 4 
    if current_scene != old_scene and current_scene == 4:
        if current_boss is None or not current_boss.is_alive:
            from boss import DemonSlimeBoss, BossUI
            # ฉากที่ 4: พื้นอยู่ที่ y=380, บอสสูง 100px -> เกิดที่ 280
            current_boss = create_monster(DemonSlimeBoss, 550, 280) 
            current_boss_ui = BossUI(current_boss)

    # เรียกคืนหรือ spawn มอนสเตอร์ตามฉากต่างๆ
    if current_scene != old_scene:
        # บังคับโชว์เนื้อเรื่องเมื่อเปลี่ยนฉาก (ถ้ายังไม่โชว์)
        story_key = f"SCENE_{current_scene}_START"
        if story_key in STORY_DATA:
            dialogue_manager.show_message(STORY_DATA[story_key])
        
        if current_scene == 1:
            if current_scene in scene_monster_data:
                # ผู้เล่นกลับมา เรียกคืนทดแทน
                current_monsters = scene_monster_data[current_scene]
            elif current_scene not in scene_monsters_cleared:
                from monster import NightBorne
                # ปรับตำแหน่ง y ให้ยืนบนพื้นพอดี (y = ground(410) - height(100) = 310)
                current_monsters = [create_monster(NightBorne, 700, 310)] # ขยับมอนเข้ามาเพื่อเช็คปาร์ตี้กับกับดัก
                
        elif current_scene == 2:
            current_puzzle = DeflectorPuzzleManager()
                
        elif current_scene == 3:
            if current_scene in scene_monster_data:
                current_monsters = scene_monster_data[current_scene]
            elif current_scene not in scene_monsters_cleared:
                from monster import EvilWizard
                # ปรับตำแหน่ง y ให้ยืนบนพื้นพอดี (y = ground(360) - height(150) = 210)
                current_monsters = [create_monster(EvilWizard, 450, 210)]

    # 4. วาดทุกอย่างลงบน game_surface (เรียงลำดับจากหลังมาหน้า)
    game_surface.fill((0, 0, 0)) # เคลียร์จอจำลอง

    # วาดฉากหลัง (รองรับ Parallax)
    bg.draw(player.rect.x)
    
    # วาดพื้นที่ทั้งหมด
    for area in game_areas:
        area.draw(game_surface)


    # วาดวิถีดาบ (Slash FX)
    for sfx in slash_fx_list:
        sfx.draw(game_surface)

    # วาดมอนสเตอร์ปกติ
    for m in current_monsters:
        m.draw(game_surface)

    # วาดพัซเซิล (ถ้ามี)
    if current_puzzle:
        current_puzzle.draw(game_surface)

    # วาดขวดเลือด (High Quality Visuals)
    for potion in health_potions:
        # วาดออร่าสีแดงจางๆ รอบขวด
        s = pygame.Surface((40, 40), pygame.SRCALPHA)
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5 + 15
        pygame.draw.circle(s, (255, 0, 0, 50), (20, 20), pulse)
        game_surface.blit(s, (potion.x - 10, potion.y - 10))
        # วาดตัวขวด
        pygame.draw.rect(game_surface, (200, 0, 0), potion, border_radius=5)
        pygame.draw.rect(game_surface, (255, 255, 255), (potion.x + 5, potion.y + 3, 10, 4), border_radius=2) # เงาสะท้อนน้ำยา
        pygame.draw.rect(game_surface, (255, 255, 255), potion, 1, border_radius=5)

    # วาดตัวละครผู้เล่น (ซ่อน UI ถ้าเป็นฉากจบ)
    player.draw(game_surface, show_ui=(game_state not in ["ENDING", "GAME_OVER"]))

    # วาดฉากเช้าถ้าอยู่ในโหมด ENDING
    if game_state == "ENDING" and morning_bg:
        morning_bg.draw(0)
        player.draw(game_surface, show_ui=False) # วาดผู้เล่นทับอีกรอบหลังเปลี่ยนพื้นหลัง

    # วาดเอฟเฟกต์
    for ap in ambient_particles: ap.draw(game_surface) # วาดบรรยากาศไว้หลังสุด (หรือหน้าสุดตามใจ)
    for ft in floating_texts: ft.draw(game_surface)
    for p in particles: p.draw(game_surface)
    for ip in impact_particles: ip.draw(game_surface)
    for sw in shockwaves: sw.draw(game_surface)
    for dp in dust_particles: dp.draw(game_surface)

    # วาดมอนสเตอร์และบอส (เฉพาะถ้ายังไม่ถึงฉากจบ)
    if not morning_bg:
        for m in current_monsters:
            m.draw(game_surface)
        if current_scene == 4 and current_boss:
            current_boss.draw(game_surface)
            if current_boss_ui:
                current_boss_ui.draw(game_surface)

    # อัพเดทดาเมจตัวเลขของมอนสเตอร์
    for m in current_monsters:
        if not hasattr(m, '_old_hp_track'): m._old_hp_track = m.current_hp
        if m.current_hp < m._old_hp_track:
            diff = m._old_hp_track - m.current_hp
            floating_texts.append(FloatingText(m.rect.centerx, m.rect.top, f"-{diff}", (255, 150, 0)))
        m._old_hp_track = m.current_hp

    # --- จังหวะรวมร่าง: Blit game_surface ลง screen พร้อม Screen Shake ---
    off_x, off_y = screen_shake.get_offset()
    
    # ถ้าหยุดเกม ให้วาดภาพเบลอแทนการวาดฉากปกติ
    if game_state == "PAUSED" and pause_bg_surf:
        screen.blit(pause_bg_surf, (0, 0))
    else:
        # Cinematic Hero Death: ถ้ากำลังสโลว์ตอนตาย ให้ฉากเป็นโทนดำ
        if death_cinematic_timer > 0:
            gray_surf = game_surface.copy()
            # ใช้สีเทาเข้มผสม 
            overlay = pygame.Surface((800, 500), pygame.SRCALPHA)
            overlay.fill((20, 20, 20, 150))
            gray_surf.blit(overlay, (0, 0))
            screen.blit(gray_surf, (off_x, off_y))
        else:
            screen.blit(game_surface, (off_x, off_y))

    # วาด Fade ตอนจบ (ทั้ง Fade In และ Fade Out)
    if game_state == "ENDING":
        if (ending_step == 1 and ending_fade_alpha > 0) or (ending_step == 2):
            fade_surface = pygame.Surface((800, 500))
            fade_surface.fill((255, 255, 255))
            fade_surface.set_alpha(ending_fade_alpha)
            screen.blit(fade_surface, (0, 0))

    # วาด Lighting Overlay (Vignette) - วาดทับโลกแต่ใต้ UI
    if game_state in ["GAME", "PAUSED"]:
        # เคลียร์ overlay ให้เป็นสีมืดขอบจอ
        vignette_overlay.fill((0, 0, 0, 150))
        # วาด Spotlight เจาะรูรอบตัวผู้เล่น (รวมค่าสั่นหน้าจอ)
        p_scr_x = player.rect.centerx + off_x
        p_scr_y = player.rect.centery + off_y
        vignette_overlay.blit(light_mask, (p_scr_x - 300, p_scr_y - 300), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(vignette_overlay, (0, 0))

    # วาด Low HP Pulse (ขอบจอแดงกระพริบ)
    if game_state == "GAME" and player.is_alive:
        hp_percent = player.current_hp / player._max_hp
        if hp_percent <= 0.3: # เลือดต่ำกว่า 30%
            low_hp_timer += 0.05 + (0.3 - hp_percent) * 0.2 # ยิ่งเลือดน้อยยิ่งกระพริบถี่
            pulse_val = math.sin(low_hp_timer) * 0.5 + 0.5
            alpha = int(pulse_val * 130) # เพิ่มความเข้มสูงสุดเป็น 130
            
            low_hp_overlay.fill((0, 0, 0, 0)) # เคลียร์
            # วาดขอบแดง (Vignette) ให้เล็กลงพอดีสายตา
            pygame.draw.rect(low_hp_overlay, (200, 0, 0, alpha), (0, 0, 800, 500), 25) 
            screen.blit(low_hp_overlay, (0, 0))

    # อัปเดตและวาดเนื้อเรื่อง (Dialogue) - วาดไว้บนสุดเสมอ (ไม่สั่นตามฉาก)
    dialogue_manager.update()
    dialogue_manager.draw(screen)

    # วาด Fade Transition ฉากหลัง (สีดำ)
    if is_scene_fading:
        fade_surf = pygame.Surface((800, 500))
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(scene_fade_alpha)
        screen.blit(fade_surf, (0, 0))
        
        if scene_fade_mode == "out":
            scene_fade_alpha += 15 # มืดลงเร็วขึ้น
            if scene_fade_alpha >= 255:
                scene_fade_alpha = 255
                _execute_scene_change() # เปลี่ยนฉากจริงที่จุดมืดที่สุด
                scene_fade_mode = "in"
        else:
            scene_fade_alpha -= 15 # สว่างขึ้น
            if scene_fade_alpha <= 0:
                scene_fade_alpha = 0
                is_scene_fading = False

    # วาดปุ่มเข้าป๊อบอับเมนู (Pause Button)
    if game_state == "GAME":
        pygame.draw.rect(screen, (80, 80, 80), in_game_menu_btn, border_radius=5)
        btn_surf = pygame.font.SysFont("Arial", 16, bold=True).render("MENU", True, (255, 255, 255))
        screen.blit(btn_surf, btn_surf.get_rect(center=in_game_menu_btn.center))
        

    # ตรวจสอบการพ่ายแพ้และชัยชนะ (เปลี่ยน State ไปที่ GAME_OVER)
    if not player.is_alive and game_state == "GAME":
        if death_cinematic_timer == 0:
            death_cinematic_timer = 120 # เริ่ม Cinematic ตาย 2 วินาที (60fps * 2)
            slow_mo_timer = 120 # สโลว์สุดขีด
            screen_shake.trigger(15, 0.8)

        if death_cinematic_timer > 0:
            death_cinematic_timer -= 1
            if death_cinematic_timer <= 1: # เมื่อจบ cinematic
                if not game_over_menu: # สร้างเมนูเมื่อตายครั้งแรก
                    game_over_menu = GameOverMenu(800, 500, title="You Loose!", color=(255, 0, 0))
                    game_state = "GAME_OVER"
    elif current_scene == 4 and current_boss and not current_boss.is_alive and game_state == "GAME":
        if not dialogue_manager.is_showing:
            # Cinematic Finish for Boss
            if death_cinematic_timer == 0:
                death_cinematic_timer = 180 # 3 วินาที
                slow_mo_timer = 180
                screen_shake.trigger(20, 1.0) # สั่นแรงมากตอนบอสตาย
                
            if death_cinematic_timer > 0:
                death_cinematic_timer -= 1
                if death_cinematic_timer <= 1:
                    dialogue_manager.show_message(STORY_DATA["BOSS_DEFEATED"])
                    game_state = "ENDING"

    # วาดเมนู Game Over ถ้าอยู่ใน State GAME_OVER
    if game_state == "GAME_OVER" and game_over_menu:
        game_over_menu.draw(screen)
        
    # วาดเมนูหยุดเกมทับถ้าอยู่ใน State PAUSED
    if game_state == "PAUSED":
        pause_menu.draw(screen)

    # อัปเดตพิกัดฉากเดิมก่อนจบรอบ
    old_scene = current_scene

    # ควบคุมความเร็วเกม (FPS)
    fps_to_use = settings_menu.fps
    if slow_mo_timer > 0:
        slow_mo_timer -= 1
        fps_to_use = 15 # สโลว์เหลือ 15 FPS
        
        # วาด Flash สีขาวเสี้ยววินาทีเมื่อเริ่มสโลว์
        if slow_mo_timer > 110: # เริ่มช่วงสโลว์ใหม่ๆ
            flash = pygame.Surface((800, 500))
            flash.fill((255, 255, 255))
            flash.set_alpha(100)
            screen.blit(flash, (0, 0))

    # อัปเดตหน้าจอหลักรวม
    pygame.display.update()
    clock.tick(fps_to_use)

pygame.quit()