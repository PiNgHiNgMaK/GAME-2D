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
        self._hit_flash_timer = 0 # สำหรับเอฟเฟกต์กระพริบตอนโดนตี
    
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
            self._hit_flash_timer = 10 # กระพริบ 10 เฟรม

    def handle_input(self, keys):
        """ศัตรูทำงานด้วย AI ไม่จำเป็นต้องใช้การควบคุมด้วยปุ่มแบบ Player"""
        pass

    # บังคับให้ subclass ต้องมีการโจมตี
    def attack(self, target):
        pass


class MinotaurBoss(Enemy):
    """
    บอส Demon Slime จอมเขมือบจากอเวจี
    (Inheritance: รับคุณสมบัติจาก Enemy และ Character)
    """
    def __init__(self, x, y):
        # 3. Inheritance สืบทอดแอตทริบิวต์และเมธอดเริ่มต้น
        super().__init__(x, y, speed=2, hp=1000, name="Demon Slime")
        
        # โหลด Sprite แบบแยกโฟลเดอร์ตามโครงสร้างไฟล์ใหม่
        self._animations = {
            "idle": self._load_frames("01_demon_idle", "demon_idle", 6),
            "walk": self._load_frames("02_demon_walk", "demon_walk", 12),
            "attack": self._load_frames("03_demon_cleave", "demon_cleave", 15),
            "hurt": self._load_frames("04_demon_take_hit", "demon_take_hit", 5),
            "dead": self._load_frames("05_demon_death", "demon_death", 22)
        }
        
        self._action = "idle" 
        self._current_frame = 0
        self._animation_timer = 0
        self._attack_cooldown = 0
        
        # ปรับ Hitbox ให้เหมาะกับสไลม์ (ตัวกว้าง)
        self._rect = pygame.Rect(x, y, 140, 100)
        self._detect_range = 500
        self._attack_range = 180 # ท่า Cleave มีระยะกว้าง
        self._facing_right = False
        self._damage = 30
        self._is_berserk = False # สถานะคลั่ง (Phase 2)

        # เล่นเสียงตอนโผล่ออกมา
        try:
            import os
            if os.path.exists("assets/sound/1.mp3"):
                self._spawn_sound = pygame.mixer.Sound("assets/sound/1.mp3")
                self._spawn_sound.set_volume(0.8)
                self._spawn_sound.play()
        except:
            pass

        # โหลดเสียงตอนตาย
        try:
            import os
            if os.path.exists("assets/sound/2.mp3"):
                self._death_sound = pygame.mixer.Sound("assets/sound/2.mp3")
                self._death_sound.set_volume(0.8)
            else:
                self._death_sound = None
        except:
            self._death_sound = None

    def _load_frames(self, folder, prefix, count):
        frames = []
        base_path = f"assets/boss/boss_demon_slime_FREE_v1.0/individual sprites/{folder}/{prefix}_"
        for i in range(1, count + 1):
            try:
                img = pygame.image.load(f"{base_path}{i}.png").convert_alpha()
                frames.append(img)
            except:
                print(f"Error loading: {base_path}{i}.png")
        return frames

    # =====================================================================
    # 4. Polymorphism (พหุสัณฐาน)
    # =====================================================================
    def take_damage(self, amount):
        if self._current_hp > 0:
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._action = "dead"
                self._current_frame = 0
                self._animation_timer = 0
                if hasattr(self, '_death_sound') and self._death_sound:
                    self._death_sound.play()
            else:
                if self._action != "attack":
                    self._action = "hurt"
                    self._current_frame = 0
                    self._animation_timer = 0
                self._hit_flash_timer = 12
                
    def update(self, game_areas, player=None):
        if not self._is_alive:
            return
            
        # เช็ค Phase 2 (Berserk) เมื่อเลือดต่ำกว่า 50%
        if not self._is_berserk and self._current_hp < self._max_hp / 2:
            self._is_berserk = True
            self._speed *= 1.5 # วิ่งไวขึ้น
            self._damage += 15 # ตีแรงขึ้น
            
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1

        if self._action != "dead":
            if player and getattr(player, 'is_alive', True):
                distance = player.rect.centerx - self._rect.centerx
                self._facing_right = distance > 0
                abs_distance = abs(distance)
                
                if self._attack_cooldown > 0:
                    self._attack_cooldown -= 1
                    
                if self._action != "hurt":
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
                if self._action not in ("attack", "hurt"):
                    self._action = "idle"

        # ระบบแรงโน้มถ่วง
        self._velocity_y += 0.5
        self._rect.y += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0 and self._rect.bottom <= area.rect.bottom:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
                
        # อัพเดต Animation
        frames = self._animations.get(self._action, self._animations["idle"])
        if not frames: return
        
        self._animation_timer += 1
        
        # ความเร็วอนิเมชันตามท่า
        anim_speed = 6
        if self._action == "attack": anim_speed = 4
        if self._action == "hurt": anim_speed = 8
        if self._action == "dead": anim_speed = 5

        if self._animation_timer >= anim_speed:
            self._animation_timer = 0
            if self._action == "dead":
                if self._current_frame < len(frames) - 1:
                    self._current_frame += 1
                else:
                    self._is_alive = False
            elif self._action == "hurt":
                self._current_frame += 1
                if self._current_frame >= len(frames):
                    self._current_frame = 0
                    self._action = "idle"
            elif self._action == "attack":
                self._current_frame += 1
                if self._current_frame >= len(frames):
                    self._current_frame = 0
                    self._action = "idle"
                    self._attack_cooldown = 100
            else:
                self._current_frame += 1
                if self._current_frame >= len(frames):
                    self._current_frame = 0
        
    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0 
        if hasattr(target, 'take_damage'):
            target.take_damage(self._damage)

    def draw(self, screen):
        if not self._is_alive or self._action not in self._animations:
            return
            
        frames = self._animations[self._action]
        if not frames: return
        
        current_idx = min(self._current_frame, len(frames)-1)
        frame_image = frames[current_idx]
            
        # ปรับสเกล
        scale = 1.8
        if self._is_berserk: scale = 2.0 # ตัวใหญ่ขึ้นนิดนึงตอนคลั่ง
        w, h = frame_image.get_size()
        frame_image = pygame.transform.scale(frame_image, (int(w * scale), int(h * scale)))
        
        # เอฟเฟกต์กระพริบสีขาวตอนโดนตี
        if self._hit_flash_timer > 0:
            flash_surf = pygame.Surface(frame_image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, 150)) # สีขาวกึ่งโปร่งใส
            frame_image.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # เอฟเฟกต์สีแดงถ้าคลั่ง (Phase 2)
        if self._is_berserk:
            red_tint = pygame.Surface(frame_image.get_size(), pygame.SRCALPHA)
            red_tint.fill((100, 0, 0, 0)) # เน้นสีแดง
            frame_image.blit(red_tint, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        if self._facing_right:
            frame_image = pygame.transform.flip(frame_image, True, False)
            
        image_rect = frame_image.get_rect()
        image_rect.midbottom = (self._rect.midbottom[0], self._rect.midbottom[1] + 10)
        
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
