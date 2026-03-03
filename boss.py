import pygame
from player import Character

# =====================================================================
# 1. Abstraction (นามธรรม) / Inheritance (การสืบทอด)
# =====================================================================
# คลาสศัตรูพื้นฐาน (Enemy) ทำหน้าที่เป็นแม่แบบให้ศัตรูประเภทต่างๆ
class Enemy(Character):
    def __init__(self, x, y, speed, hp, name):
        super().__init__(x, y, speed)
        # =====================================================================
        # 2. Encapsulation (การห่อหุ้ม)
        # =====================================================================
        # แอตทริบิวต์เหล่านี้ควรเป็น private/protected เปลี่ยนแปลงเฉพาะผ่านเมธอด
        self._max_hp = hp
        self._current_hp = hp
        self._name = name
        self._damage = 25
        self._is_alive = True
    
    @property
    def is_alive(self):
        return self._is_alive

    @property
    def rect(self):
        """Getter สำหรับ Hitbox"""
        return self._rect

    @property
    def current_hp(self):
        return self._current_hp

    @property
    def max_hp(self):
        return self._max_hp
        
    @property
    def name(self):
        return self._name

    # ฟังก์ชันเปิดให้ภายนอกทำดาเมจ โดยไม่ให้เข้าถึง _current_hp ตรงๆ
    def take_damage(self, amount):
        if self._is_alive:
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._is_alive = False

    def handle_input(self, keys):
        """ศัตรูทำงานด้วย AI ไม่จำเป็นต้องใช้การควบคุมด้วยปุ่มแบบ Player"""
        pass

    # บังคับให้ subclass ต้องมีการโจมตี
    def attack(self, target):
        pass


class MinotaurBoss(Enemy):
    """
    บอส Minotaur เฝ้าสมบัติ 
    (Inheritance: รับคุณสมบัติจาก Enemy และ Character)
    """
    def __init__(self, x, y):
        # 3. Inheritance สืบทอดแอตทริบิวต์และเมธอดเริ่มต้น
        super().__init__(x, y, speed=1, hp=300, name="Minotaur")
        
        # นำเข้า Sprite
        self._sprite_idle = pygame.image.load("Minotaur_1/Idle.png").convert_alpha()
        self._sprite_walk = pygame.image.load("Minotaur_1/Walk.png").convert_alpha()
        self._sprite_attack = pygame.image.load("Minotaur_1/Attack.png").convert_alpha()
        self._sprite_dead = pygame.image.load("Minotaur_1/Dead.png").convert_alpha()
        
        self._action = "idle" # "idle", "walk", "attack", "dead"
        self._current_frame = 0
        self._animation_timer = 0
        self._attack_cooldown = 0
        
        # ปรับขนาดกล่องชน Hitbox ให้เข้ากับตัวบอส
        self._rect = pygame.Rect(x, y, 90, 110)
        self._detect_range = 350 # ระยะมองเห็นตัวเล่น
        self._attack_range = 100  # ระยะที่เริ่มโจมตี
        self._facing_right = False

    # =====================================================================
    # 4. Polymorphism (พหุสัณฐาน)
    # =====================================================================
    # รูปแบบการทำงานอัปเดตสถานะของ Boss ต่างจาก Player 
    def take_damage(self, amount):
        if self._current_hp > 0:
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._action = "dead"
                self._current_frame = 0
                self._animation_timer = 0
                
    def update(self, game_areas, player=None):
        if not self._is_alive:
            return
            
        # การทำงานของ AI บอส (เดินหา Player และโจมตี)
        if self._action != "dead":
            if player and getattr(player, 'is_alive', True):
                distance = player.rect.centerx - self._rect.centerx
                
                # หันหน้าหาผู้เล่น
                self._facing_right = distance > 0
                
                abs_distance = abs(distance)
                
                # ลด Cooldown การโจมตี
                if self._attack_cooldown > 0:
                    self._attack_cooldown -= 1
                    
                # ตัดสินใจพฤติกรรม
                if abs_distance <= self._attack_range and self._attack_cooldown == 0 and self._action != "attack":
                    self.attack(player)
                elif abs_distance <= self._detect_range and self._action != "attack" and not player.rect.colliderect(self._rect):
                    self._action = "walk"
                    if self._facing_right:
                        self._rect.x += self._speed
                    else:
                        self._rect.x -= self._speed
                elif self._action != "attack":
                    self._action = "idle"
            else:
                if self._action != "attack":
                    self._action = "idle"

        # ระบบแรงโน้มถ่วงง่ายๆ
        self._velocity_y += 0.5
        self._rect.y += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0 and self._rect.bottom <= area.rect.bottom:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
                
        # อัพเดต Animation ของ Boss
        if self._action == "dead":
            sheet = self._sprite_dead
        elif self._action == "attack":
            sheet = self._sprite_attack
        elif self._action == "walk":
            sheet = self._sprite_walk
        else:
            sheet = self._sprite_idle
            
        # คำนวณจำนวนเฟรมโดยประมาณจากสัดส่วนภาพ
        frames_count = sheet.get_width() // sheet.get_height()
        max_frames = frames_count if frames_count > 0 else 4
        
        self._animation_timer += 1
        speed_anim = 8 if self._action == "attack" else 6
        
        if self._animation_timer >= speed_anim:
            self._animation_timer = 0
            
            if self._action == "dead":
                if self._current_frame < max_frames - 1:
                    self._current_frame += 1
                else:
                    self._is_alive = False # ตายสนิทเมื่อรันอนิเมชันจบ
            else:
                self._current_frame += 1
                if self._current_frame >= max_frames:
                    self._current_frame = 0
                    if self._action == "attack":
                        self._action = "idle" # โจมตีจบกลับมายืน
                        self._attack_cooldown = 90 # Cooldown ก่อนโจมตีครั้งต่อไป
        
    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0 
        # ทำดาเมจ (ให้ผู้เล่นมีฟังก์ชันรับดาเมจ)
        if hasattr(target, 'take_damage'):
            target.take_damage(self._damage)

    # Polymorphism: การแสดงผลต่างจาก Player ตรงการดึง sprite และขนาดภาพ
    def draw(self, screen):
        if not self._is_alive:
            return
            
        if self._action == "dead":
            current_sheet = self._sprite_dead
        elif self._action == "attack":
            current_sheet = self._sprite_attack
        elif self._action == "walk":
            current_sheet = self._sprite_walk
        else:
            current_sheet = self._sprite_idle
            
        frame_width = current_sheet.get_width() // (current_sheet.get_width() // current_sheet.get_height() or 1)
        frame_height = current_sheet.get_height()
        
        max_f = current_sheet.get_width() // frame_width
        current_frame_clamped = self._current_frame if self._current_frame < max_f else 0
            
        frame_rect = pygame.Rect(current_frame_clamped * frame_width, 0, frame_width, frame_height)
        frame_image = current_sheet.subsurface(frame_rect)
            
        # ขยายร่างบอสให้ตัวใหญ่สมจริงตามฉาก
        scale_size = 2.5
        frame_image = pygame.transform.scale(frame_image, (int(frame_width * scale_size), int(frame_height * scale_size)))
        frame_image.set_colorkey((0, 0, 0)) # โปร่งใส
        
        if not self._facing_right:
            frame_image = pygame.transform.flip(frame_image, True, False)
            
        image_rect = frame_image.get_rect()
        image_rect.midbottom = self._rect.midbottom
        
        screen.blit(frame_image, image_rect)

# =====================================================================
# คลาสสำหรับจัดการ UI (Single Responsibility Principle)
# =====================================================================
class BossUI:
    """ทำหน้าที่เฉพาะวาดหลอดเลือดและชื่อของบอสที่มุมขวาบน"""
    def __init__(self, boss):
        self._boss = boss
        pygame.font.init()
        self._font = pygame.font.SysFont("Arial", 28, bold=True)
        
    def draw(self, screen):
        if not self._boss.is_alive:
            return
            
        bar_width = 300
        bar_height = 25
        x = 800 - bar_width - 20 # ชิดขวาบนของจอ (จอสมมติกว้าง 800)
        y = 40
        
        hp_ratio = self._boss.current_hp / self._boss.max_hp
        current_bar_width = int(bar_width * hp_ratio)
        current_bar_width = max(0, current_bar_width)
        
        # พื้นหลัง (สีเทาเข้ม)
        pygame.draw.rect(screen, (40, 40, 40), (x, y, bar_width, bar_height))
        # หลอดเลือด (สีแดงเลือดหมู)
        pygame.draw.rect(screen, (180, 20, 20), (x, y, current_bar_width, bar_height))
        # กรอบหลอดเลือด (สีทอง)แสดงความเป็นบอส
        pygame.draw.rect(screen, (255, 215, 0), (x, y, bar_width, bar_height), 3) 
        
        # วาดชื่อ Boss เหนือหลอดเลือด
        name_surface = self._font.render(self._boss.name, True, (255, 255, 255))
        screen.blit(name_surface, (x, y - 30))
