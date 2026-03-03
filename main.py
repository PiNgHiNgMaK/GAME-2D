import pygame
from abc import ABC, abstractmethod
from background.back_g import background
from player import Player

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

current_scene = 1
bg, game_areas = load_scene(current_scene)

# สร้างตัวละครผู้เล่น (Abstaction & Encapsulation จาก Player class)
player = Player(50, 100) # เริ่มต้นที่ขอบซ้ายของจอ

clock = pygame.time.Clock() # สร้างตัวควบคุมเวลา (FPS)
running = True
while running:
    # 1. การจัดการ Event ปิดเกม
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. การจัดการ Input การกดค้างของผู้เล่น (เดินซ้าย, ขวา, สเปซบาร์)
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # 3. อัปเดตตรรกะและฟิสิกส์ต่างๆ ในเกม
    player.update(game_areas)
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

    # 4. วาดทุกอย่างลงบนหน้าจอ (เรียงลำดับจากหลังมาหน้า)
    # วาดฉากหลัง
    bg.draw()
    
    # วาดพื้นที่ทั้งหมด โดยใช้หลักการ Polymorphism เรียก method draw ทีเดียว
    for area in game_areas:
        area.draw(screen)

    # วาดตัวละครผู้เล่น
    player.draw(screen)

    # อัปเดตหน้าจอหลักรวม
    pygame.display.update()
    
    # ควบคุมความเร็วของเกมให้อยู่ที่ 60 เฟรมต่อวินาที (FPS คงที่เพื่อให้การแสดงผลและเดินคงที่)
    clock.tick(60)

pygame.quit()