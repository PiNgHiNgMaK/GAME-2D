import pygame
import os
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
        self._display_hp = float(hp)
        self._name = name
        self._is_stunned = False
        self._damage = 25
        self._is_alive = True
        self._hit_flash_timer = 0
        self._stun_timer = 0
        
        # โหลดเสียงเจ็บพื้นฐาน
        try:
            if os.path.exists("assets/sound/monster_hurt.ogg"):
                self._hurt_sound = pygame.mixer.Sound("assets/sound/monster_hurt.ogg")
                self._hurt_sound.set_volume(0.5)
            else: self._hurt_sound = None
        except: self._hurt_sound = None
    
    @property
    def action(self):
        return getattr(self, '_action', "idle")
        
    @property
    def frame_index(self):
        return getattr(self, '_current_frame', 0)

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
            
            # เมื่อโดนโจมตี ให้เข้าสู่ท่า Hurt เสมอเพื่อให้ State Machine ทำงานต่อยอดไปยังท่าตายได้
            if hasattr(self, '_action') and self._action != "dead":
                self._action = "hurt"
                self._current_frame = 0
                
            self._hit_flash_timer = 10 # กระพริบ 10 เฟรม
            if hasattr(self, '_hurt_sound') and self._hurt_sound:
                self._hurt_sound.play()

    def handle_input(self, keys):
        """ศัตรูทำงานด้วย AI ไม่จำเป็นต้องใช้การควบคุมด้วยปุ่มแบบ Player"""
        pass

    # บังคับให้ subclass ต้องมีการโจมตี
    def attack(self, target):
        pass

    def stun(self, duration):
        """ทำให้ศัตรูติดสตั้น (หยุดนิ่ง)"""
        if self._is_alive:
            self._is_stunned = True
            self._stun_timer = duration
            # เปลี่ยนท่าทางอัตโนมัติ (ถ้ามีท่า hurt ให้ใช้ท่า hurt)
            if hasattr(self, '_action'):
                self._action = "hurt"
                self._current_frame = 0


class DemonSlimeBoss(Enemy):
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
        
        # เสียงเตรียมการ
        try:
            if os.path.exists("assets/sound/mino1.wav"):
                self._roar_sound = pygame.mixer.Sound("assets/sound/mino1.wav")
                self._roar_sound.set_volume(0.7)
            else: self._roar_sound = None
        except: self._roar_sound = None

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
            if os.path.exists("assets/sound/2.mp3"):
                self._death_sound = pygame.mixer.Sound("assets/sound/2.mp3")
                self._death_sound.set_volume(0.8)
            else:
                self._death_sound = None
        except:
            self._death_sound = None

    @property
    def action(self):
        return self._action
        
    @property
    def frame_index(self):
        return self._current_frame

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
                if hasattr(self, '_death_sound') and self._death_sound:
                    self._death_sound.play()
            else:
                if self._action != "attack":
                    self._action = "hurt"
                    self._current_frame = 0
            self._animation_timer = 0
            self._hit_flash_timer = 12

    def attack(self, target):
        if self._attack_cooldown == 0 and self._is_alive and self._action not in ("dead", "hurt"):
            self._action = "attack"
            self._current_frame = 0
            self._animation_timer = 0
            if hasattr(self, '_roar_sound') and self._roar_sound:
                self._roar_sound.play()
                
    def update(self, game_areas, player=None, shockwave_list=None):
        if not self._is_alive:
            return
            
        # เก็บ shockwave_list ไว้ใช้ใน update_animation หรือช่วงเช็คดาเมจ
        self._shockwave_list = shockwave_list
        # เช็ค Phase 2 (Berserk) เมื่อเลือดต่ำกว่า 50%
        if not self._is_berserk and self._current_hp < self._max_hp / 2:
            self._is_berserk = True
            self._speed *= 1.5 # วิ่งไวขึ้น
            self._damage += 15 # ตีแรงขึ้น
            
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1
            
        # Smooth HP interpolation
        if self._display_hp > self._current_hp:
            self._display_hp -= (self._display_hp - self._current_hp) * 0.05
            if self._display_hp < self._current_hp: self._display_hp = self._current_hp
        elif self._display_hp < self._current_hp:
            self._display_hp += (self._current_hp - self._display_hp) * 0.05
            if self._display_hp > self._current_hp: self._display_hp = self._current_hp
            
        # จัดการระบบ Stun
        if self._stun_timer > 0:
            self._stun_timer -= 1
            self._is_stunned = True
            if self._stun_timer <= 0:
                self._is_stunned = False
                if self._current_hp > 0:
                    self._action = "idle"
                else:
                    self._action = "dead"
        
        if self._is_stunned:
            # ข้าม AI ไปยังส่วน Animation ด้านล่าง
            pass
        else:
            if self._action != "dead":
                self._handle_ai(player, game_areas)

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
                    self._action = "idle" if self._current_hp > 0 else "dead"
            elif self._action == "attack":
                self._current_frame += 1
                
                # ทำดาเมจจริงที่เฟรมที่ 12 (จังหวะที่ดาบขนาดยักษ์กระแทกพื้นพอดี)
                if self._current_frame == 12 and player:
                    # เช็คระยะอีกครั้งในจังหวะฟัน (ป้องกันผู้เล่นพุ่งหลบออกไปทัน)
                    dist = abs(player.rect.centerx - self._rect.centerx)
                    if dist <= self._attack_range + 20: 
                        if player.take_damage(self._damage, shockwave_list=getattr(self, '_shockwave_list', None)):
                             self.stun(120) # สตั้น 2 วินาทีเมื่อโดน Parry

                if self._current_frame >= len(frames):
                    self._current_frame = 0
                    self._action = "idle" if self._current_hp > 0 else "dead"
                    # คูลดาวน์สั้นลงถ้าอยู่ในโหมดคลั่ง
                    self._attack_cooldown = 60 if self._is_berserk else 100
            else:
                self._current_frame += 1
                if self._current_frame >= len(frames):
                    self._current_frame = 0

    def _handle_ai(self, player, game_areas):
        """ตรรกะ AI ของบอสสไลม์"""
        if player and getattr(player, 'is_alive', True):
            distance = player.rect.centerx - self._rect.centerx
            self._facing_right = distance > 0
            abs_dist = abs(distance)
            
            if self._attack_cooldown > 0:
                self._attack_cooldown -= 1
                
            if self._action not in ("hurt", "attack", "dead"):
                move_dir = 0
                
                if self._is_berserk:
                    # Phase 2: เกี้ยวกราด - เดินหน้าฆ่ามันอย่างเดียว
                    if abs_dist <= self._attack_range:
                        if self._attack_cooldown == 0:
                            self.attack(player)
                    else:
                        move_dir = 1 if self._facing_right else -1
                else:
                    # Phase 1: สุขุม - เดินเข้าหาและรักษาระยะ
                    if abs_dist <= self._attack_range:
                        if self._attack_cooldown == 0:
                            self.attack(player)
                        elif abs_dist < 100:
                            # ถ้าผู้เล่นมาชิดเกินไปช่วงคูลดาวน์ ให้ถอยเล็กน้อย
                            move_dir = -1 if self._facing_right else 1
                    elif abs_dist <= self._detect_range:
                        move_dir = 1 if self._facing_right else -1

                if move_dir != 0:
                    # ตรวจสอบขอบเหว (Edge Detection)
                    new_x = self._rect.x + (move_dir * self._speed)
                    check_x = new_x + (self._rect.width if move_dir > 0 else 0)
                    check_rect = pygame.Rect(check_x, self._rect.bottom + 5, 2, 2)
                    
                    has_ground = any(a.is_walkable() and a.rect.colliderect(check_rect) for a in game_areas)
                    # บอสจะไม่ตกหลุม (แต่ฉาก 4 มักจะกว้างสุดจออยู่แล้ว)
                    if has_ground:
                        self._rect.x = new_x
                        self._action = "walk"
                    elif self._action not in ("attack", "dead"):
                        self._action = "idle"
                elif self._action not in ("attack", "dead"):
                    self._action = "idle"
        else:
            if self._action not in ("attack", "hurt", "dead"):
                self._action = "idle"
        
    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0 
        # ย้ายการทำดาเมจไปไว้ที่ update() ตามเฟรมอนิเมชั่น

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
        
        # เอฟเฟกต์กระพริบสีขาวตอนโดนตี (High Quality Fix)
        if self._hit_flash_timer > 0:
            flash_surf = frame_image.copy()
            flash_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            flash_surf.set_alpha(150) # ทำให้ขาวนวลๆ
            frame_image.blit(flash_surf, (0, 0))

        # เอฟเฟกต์สีแดงถ้าคลั่ง (Phase 2 - แก้ไขให้ไม่เป็นปื้น)
        if self._is_berserk:
            red_tint = frame_image.copy()
            red_tint.fill((100, 0, 0), special_flags=pygame.BLEND_RGB_ADD) # ย้อมแดง
            red_tint.set_alpha(100) # เจือจางลง
            frame_image.blit(red_tint, (0, 0))

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
        if not self._boss or not hasattr(self._boss, 'is_alive') or not self._boss.is_alive:
            return
            
        bar_width = 500
        bar_height = 25
        # วางไว้ตรงกลางด้านบน
        x = (800 - bar_width) // 2
        y = 50
        
        hp_ratio = self._boss.current_hp / self._boss.max_hp
        display_hp_ratio = getattr(self._boss, '_display_hp', self._boss.current_hp) / self._boss.max_hp
        
        # พื้นหลัง
        pygame.draw.rect(screen, (30, 30, 30), (x, y, bar_width, bar_height))
        # หลอด "เลือกลด" (สีแดงเข้ม/ขาวจางๆ) - ใช้ display_hp_ratio
        pygame.draw.rect(screen, (200, 50, 50), (x, y, int(bar_width * display_hp_ratio), bar_height))
        # หลอดเลือดจริง (สีม่วงบอส) - ใช้ hp_ratio
        pygame.draw.rect(screen, (150, 0, 200), (x, y, int(bar_width * hp_ratio), bar_height))
        # กรอบสีทอง
        pygame.draw.rect(screen, (255, 215, 0), (x, y, bar_width, bar_height), 2)
        
        # วาดชื่อ Boss เหนือหลอดเลือด
        name_surface = self._font.render(self._boss.name, True, (255, 255, 255))
        screen.blit(name_surface, (x + (bar_width - name_surface.get_width())//2, y - 35))
