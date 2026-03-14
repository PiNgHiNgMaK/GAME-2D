import pygame
import random
from abc import ABC, abstractmethod
from effects import DustParticle, ShockwaveFX

# =====================================================================
# 1. Abstraction (นามธรรม)
# =====================================================================
class Character(ABC):
    """
    Abstract Base Class สำหรับตัวละครใดๆ ในเกม
    """
    def __init__(self, x, y, speed):
        self._x = x
        self._y = y
        self._speed = speed
        self._velocity_y = 0
        self._is_jumping = False
        self._facing_right = True

    @abstractmethod
    def update(self, game_areas):
        """อัปเดตสถานะของตัวละคร (การเคลื่อนที่, แรงโน้มถ่วง, การชน)"""
        pass

    @abstractmethod
    def draw(self, screen):
        """วาดตัวละครลงบนหน้าจอ"""
        pass

    @abstractmethod
    def handle_input(self, keys, mouse_btns=None):
        """จัดการการกรอกข้อมูลจากผู้เล่น (ปุ่มกด และเมาส์)"""
        pass


# =====================================================================
# 3. Inheritance (การสืบทอด)
# =====================================================================
class Player(Character):
    """
    คลาสผู้เล่น สืบทอดมาจาก Character
    """
    def __init__(self, x, y, speed=3): # ลดความเร็วเดินเพื่อความสมจริง
        super().__init__(x, y, speed)
        
        # เพิ่มระบบ HP ตามหลัก Encapsulation
        self._max_hp = 100
        self._current_hp = 100
        self._display_hp = 100.0 # หลอดเลือดเสมือนสำหรับอนิเมชั่นไหลนุ่มๆ
        self._is_alive = True
        self._damage = 100000
        self._name = ""
    
        # เพิ่มระบบ Stamina
        self._max_stamina = 150
        self._current_stamina = 150
        self._stamina_regen_rate = 50.0
        self._stamina_exhausted = False # สถานะเหนื่อยหอบ (วิ่งไม่ได้จนกว่าจะพัก)
        
        # Load and set up sprite sheet
        # สมมติเราใช้ Idle.png และ Walk.png เป็นหลัก ตัวอย่างนี้ใช้ Idle สำหรับตอนยืน และ Walk สำหรับเดิน
        # โหลดภาพและตัดพื้นหลังที่ติดมา (colorkey) ดำ หรือปรับปรุงให้เข้ากับภาพ
        self._sprite_idle = pygame.image.load("assets/player/Knight_1/Idle.png").convert_alpha()
        self._sprite_walk = pygame.image.load("assets/player/Knight_1/Walk.png").convert_alpha()
        self._sprite_run = pygame.image.load("assets/player/Knight_1/Run.png").convert_alpha()
        self._sprite_attack = pygame.image.load("assets/player/Knight_1/Attack 1.png").convert_alpha()
        self._sprite_attack2 = pygame.image.load("assets/player/Knight_1/Attack 3.png").convert_alpha()
        self._sprite_hurt = pygame.image.load("assets/player/Knight_1/Hurt.png").convert_alpha()
        
        # โหลด Sprite สำหรับการป้องกัน
        self._sprite_defend = pygame.image.load("assets/player/Knight_1/Protect.png").convert_alpha()
        
        # ระบบ Perfect Parry (ป้องกันจังหวะสุดท้าย)
        self._parry_timer = 0
        self._parry_flash_timer = 0
        
        # โหลดเสียงโจมตี
        try:
            import os
            if os.path.exists("assets/sound/alexis_gaming_cam-epee-342933.mp3"):
                self._attack_sound = pygame.mixer.Sound("assets/sound/alexis_gaming_cam-epee-342933.mp3")
                self._attack_sound.set_volume(0.8)
            else:
                self._attack_sound = None
        except:
            self._attack_sound = None

        # โหลดเสียงเดิน/วิ่ง แบบแยกส่วน
        try:
            if os.path.exists("assets/sound/player_walk.wav"):
                self._walk_sound = pygame.mixer.Sound("assets/sound/player_walk.wav")
                self._walk_sound.set_volume(0.5)
            else:
                self._walk_sound = None
                
            if os.path.exists("assets/sound/player_run.wav"):
                self._run_sound = pygame.mixer.Sound("assets/sound/player_run.wav")
                self._run_sound.set_volume(0.6)
            else:
                self._run_sound = None
        except:
            self._walk_sound = None
            self._run_sound = None
            
        self._current_footstep_sound = None # เก็บว่าตอนนี้เล่นเสียงไหนอยู่

        # โหลดเสียงตอนตาย
        try:
            import os
            if os.path.exists("assets/sound/3.mp3"):
                self._death_sound = pygame.mixer.Sound("assets/sound/3.mp3")
                self._death_sound.set_volume(0.8)
            else:
                self._death_sound = None
        except:
            self._death_sound = None

        # โหลดเสียงป้องกัน
        try:
            if os.path.exists("assets/sound/voicebosch-sword-block-the-ballad-of-blades-257226.mp3"):
                self._block_sound = pygame.mixer.Sound("assets/sound/voicebosch-sword-block-the-ballad-of-blades-257226.mp3")
                self._block_sound.set_volume(0.6)
            else:
                self._block_sound = None
        except:
            self._block_sound = None

        # โหลดเสียงโดนตี (Hit)
        try:
            if os.path.exists("assets/sound/2.mp3"):
                self._hit_sound = pygame.mixer.Sound("assets/sound/2.mp3")
                self._hit_sound.set_volume(0.7)
            else:
                self._hit_sound = None
        except:
            self._hit_sound = None

        # โหลดเสียงเพิ่มเติม (Jump, Land, Heal)
        try:
            if os.path.exists("assets/sound/player_jump.ogg"):
                self._jump_sound = pygame.mixer.Sound("assets/sound/player_jump.ogg")
                self._jump_sound.set_volume(0.6)
            else:
                self._jump_sound = None
                
            if os.path.exists("assets/sound/player_land.ogg"):
                self._land_sound = pygame.mixer.Sound("assets/sound/player_land.ogg")
                self._land_sound.set_volume(0.5)
            else:
                self._land_sound = None
                
            if os.path.exists("assets/sound/player_heal.ogg"):
                self._heal_sound = pygame.mixer.Sound("assets/sound/player_heal.ogg")
                self._heal_sound.set_volume(0.7)
            else:
                self._heal_sound = None
        except:
            self._jump_sound = None
            self._land_sound = None
            self._heal_sound = None

        self._frame_width = int(self._sprite_idle.get_width() / 4) # 128
        self._frame_height = self._sprite_idle.get_height() # 128
        
        # ขยายตัวละครให้ใหญ่ขึ้นตามต้องการ
        scale_factor = 2
        self._scaled_width = int(self._frame_width * scale_factor)
        self._scaled_height = int(self._frame_height * scale_factor)
        
        # =====================================================================
        # 2. Encapsulation (การห่อหุ้ม)
        # =====================================================================
        # ตัวแปรเหล่านี้ไม่ควรถูกเข้าถึงโดยตรงจากภายนอก _ (protected)
        # ตั้งตัวชน Hitbox ให้พอดีกับตัวอัศวินที่ขยายใหญ่ขึ้น (ปรับกะเอาช่วงลำตัว)
        self._rect = pygame.Rect(x, y, 60, 60) 
        self._gravity = 0.2 
        self._jump_strength = -6 
        self._current_frame = 0
        self._animation_timer = 0
        self._hit_flash_timer = 0
        self._parry_flash_timer = 0
        self._animation_timer = 0
        self._is_moving = False
        self._is_running = False # เพิ่มสถานะการวิ่ง
        self._is_attacking = False
        self._attack_type = 1 # เก็บประเภทการโจมตี (1 หรือ 2)
        self._is_defending = False # สถานะการป้องกัน
        self._is_hurt = False # สถานะบาดเจ็บ
        self._attack_cooldown = 0
        self._hit_flash_timer = 0

    @property
    def rect(self):
        """Getter สำหรับ Hitbox เอาไว้ใช้เช็คการชนกับ Area"""
        return self._rect

    @property
    def is_alive(self):
        """สถานะการมีชีวิต"""
        return self._is_alive

    @property
    def current_hp(self):
        """Getter สำหรับ HP ปัจจุบัน"""
        return self._current_hp

    @property
    def display_hp(self):
        """Getter สำหรับ HP ที่แสดงผล (สำหรับอนิเมชั่น)"""
        return self._display_hp

    @property
    def max_hp(self):
        """Getter สำหรับ HP สูงสุด"""
        return self._max_hp

    @property
    def name(self):
        return self._name
        
    @property
    def is_attacking(self):
        """Getter สำหรับสถานะกำลังโจมตี"""
        return self._is_attacking
        
    @property
    def current_frame(self):
        """Getter สำหรับเฟรมอนิเมชั่นปัจจุบัน"""
        return self._current_frame
        
    @name.setter
    def name(self, value):
        self._name = value

    def take_damage(self, amount, shockwave_list=None):
        """Method เปิดให้ภายนอกสร้างความเสียหาย"""
        if self._is_alive:
            # ระบบ Perfect Parry: ถ้ากดป้องกันได้เป๊ะๆ จะไม่เสียเลือดเลย
            if self._is_defending and self._parry_timer > 0:
                self._parry_flash_timer = 15 # กระพริบแสงทอง 15 เฟรม
                self._parry_timer = 0 # ใช้ออกไปแล้ว
                if hasattr(self, '_block_sound') and self._block_sound:
                    self._block_sound.play()
                
                # Boss-level effect: Shockwave
                if shockwave_list is not None:
                    shockwave_list.append(ShockwaveFX(self._rect.centerx, self._rect.centery, color=(255, 215, 0), max_radius=150))
                
                return True # แจ้งกลับไปยังผู้ตีว่าโดน Parry
                
            # ถ้ายกโล่ป้องกันปกติ (หลังจากหน้าต่าง Parry หมด)
            if self._is_defending:
                amount = int(amount * 0.1) 
                if hasattr(self, '_block_sound') and self._block_sound:
                    self._block_sound.play()
                
            self._current_hp -= amount
            self._hit_flash_timer = 15 # กระพริบ 15 เฟรม
            
            if self._current_hp <= 0:
                self._current_hp = 0
                self._is_alive = False
                if hasattr(self, '_death_sound') and self._death_sound:
                    self._death_sound.play()
            else:
                self._is_hurt = True
                self._current_frame = 0
        return False

    def heal(self, amount):
        """Method สำหรับเพิ่ม HP"""
        if self._is_alive:
            self._current_hp += amount
            if self._current_hp > self._max_hp:
                self._current_hp = self._max_hp
            if hasattr(self, '_heal_sound') and self._heal_sound:
                self._heal_sound.play()
        
    def _apply_gravity(self, game_areas):
        """Method ภายใน (Encapsulated) สำหรับคำนวณแรงโน้มถ่วงและการชนพื้น"""
        self._velocity_y += self._gravity
        self._rect.y += self._velocity_y

        # เช็คการชนกับพื้นที่ที่เดินได้ (WalkableArea)
        on_ground = False
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                # ถ้ากำลังตก (velocity_y > 0) และชนกับพื้น
                    if self._velocity_y > 1: # สั่นจอเบาๆ และเกิดฝุ่นเวลาลงพื้นแรง
                        # เล่นเสียงลงพื้น
                        if self._is_jumping and hasattr(self, '_land_sound') and self._land_sound:
                            self._land_sound.play()
                        pass
                    
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
                    if self._is_jumping: # จังหวะแตะพื้น
                        if hasattr(self, '_dust_list') and self._dust_list is not None:
                            for _ in range(5):
                                self._dust_list.append(DustParticle(self._rect.centerx + random.randint(-20, 20), self._rect.bottom))
                    self._is_jumping = False
                    on_ground = True
        
        # อัพเดตตำแหน่ง Y จริงให้ตรงกับกล่องชน
        self._y = self._rect.y

    # =====================================================================
    # 4. Polymorphism (พหุสัณฐาน)
    # =====================================================================
    def handle_input(self, keys, mouse_btns=None):
        """Override ให้รับปุ่มบังคับและเมาส์"""
        if mouse_btns is None:
            mouse_btns = (False, False, False)
            
        if self._is_attacking or self._is_hurt:
            return  # ไม่ให้เดินหรือป้องกันตอนกำลังโจมตี หรือ กำลังบาดเจ็บ

        self._is_moving = False
        self._is_running = False
        
        # ระบบเหนื่อยหอบ: ถ้า Stamina หมด จะติดสถานะ exhausted
        if self._current_stamina <= 0:
            self._stamina_exhausted = True
        
        # จะหายเหนื่อยก็ต่อเมื่อ Stamina กลับมาถึงระดับหนึ่ง (เช่น 30%)
        if self._stamina_exhausted and self._current_stamina >= 30:
            self._stamina_exhausted = False

        # ลดคูลดาวน์ Parry
        if self._parry_timer > 0:
            self._parry_timer -= 1
        if self._parry_flash_timer > 0:
            self._parry_flash_timer -= 1

        # จัดการปุ่ม X หรือคลิกขวา (mouse_btns[2]) สำหรับยกโล่ป้องกัน
        if not self._stamina_exhausted and (keys[pygame.K_x] or mouse_btns[2]):
            if not self._is_defending:
                self._current_frame = 0 # เริ่มต้นเฟรมป้องกัน
                self._parry_timer = 12 # มีเวลา 12 เฟรม (ประมาณ 0.2 วิ) สำหรับ Perfect Parry
            self._is_defending = True
        else:
            self._is_defending = False
            self._parry_timer = 0

        if self._is_defending:
            return # ไม่ให้เดินตอนกำลังยกโล่
        
        # ถือปุ่ม Shift ซ้ายเพื่อวิ่ง 
        # ถ้าอยู่ในสถานะเหนื่อยหอบ (exhausted) จะวิ่งไม่ได้
        if keys[pygame.K_LSHIFT] and not self._stamina_exhausted:
            current_speed = self._speed * 1.8
        else:
            current_speed = self._speed
        
        # เช็คปุ่มวิ่ง + ปุ่มเดิน
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]) and not self._stamina_exhausted:
            self._is_running = True
            # ลด stamina เมื่อวิ่ง
            self._current_stamina -= 0.5
            if self._current_stamina < 0:
                self._current_stamina = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self._rect.x -= current_speed
            self._facing_right = False
            self._is_moving = True
            
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self._rect.x += current_speed
            self._facing_right = True
            self._is_moving = True
            
        # ป้องกันไม่ให้เดินหลุดออกไปนอกหน้าจอเกมซ้ายเกินไป (หน้าจอกว้าง 800)
        # แต่ปล่อยให้เดินทะลุขวาไปได้นิดหน่อย เพื่อใช้เป็นจุดเช็คเปลี่ยนฉาก
        if self._rect.left < 0:
            self._rect.left = 0
        if self._rect.right > 850: # ยอมให้เกิน 800 ไป 50 พิเซลเพื่อแตะขอบ
            self._rect.right = 850
            
        # รองรับกระโดดด้วย Spacebar, W, หรือลูกศรขึ้น
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and not self._is_jumping:
            self._velocity_y = -6 # ปรับลดความสูงลงตามความต้องการ (เดิม -10)
            self._is_jumping = True
            if hasattr(self, '_jump_sound') and self._jump_sound:
                self._jump_sound.play()
            if hasattr(self, '_dust_list') and self._dust_list is not None:
                for _ in range(5):
                    self._dust_list.append(DustParticle(self._rect.centerx + random.randint(-15, 15), self._rect.bottom))
            
        self._x = self._rect.x

    def attack(self, target=None, attack_type=1):
        if self._is_defending or self._is_hurt:
            return # ห้ามโจมตีถ้ายกโล่อยู่ หรือบาดเจ็บอยู่
            
        # เช็ค stamina ที่ต้องใช้
        stamina_cost = 0
        if attack_type == 1: # โจมตีหนัก (Z) - 1/2 ของหลอด
            stamina_cost = self._max_stamina / 2
        elif attack_type == 2: # โจมตีปกติ (C) - 1/4 ของหลอด
            stamina_cost = self._max_stamina / 4
            
        if self._current_stamina < stamina_cost:
            return # stamina ไม่พอ โจมตีไม่ได้
            
        if self._attack_cooldown == 0 and self._is_alive:
            self._current_stamina -= stamina_cost # หัก stamina
            self._is_attacking = True
            self._attack_type = attack_type
            self._current_frame = 0
            self._attack_cooldown = 40 
            
            if hasattr(self, '_attack_sound') and self._attack_sound:
                self._attack_sound.play()
            
            # โจมตีโดนเป้าหมาย (ทำก่อน Return เพื่อให้ดาเมจเกิดจริง)
            if target and getattr(target, 'is_alive', False):
                distance = target.rect.centerx - self._rect.centerx
                if (self._facing_right and distance > 0) or (not self._facing_right and distance < 0):
                    if abs(distance) < 95:
                        # คำนวณความแรงตามประเภทการโจมตี
                        final_damage = self._damage
                        if attack_type == 1: # โจมตีหนัก
                             final_damage *= 2.0
                        
                        target.take_damage(int(final_damage))
            
            return True # เริ่มโจมตีสำเร็จ
        return False

    def update(self, game_areas, dust_list=None, mute_footsteps=False):
        """Override เพื่ออัปเดตฟิสิกส์และการขยับภาพ (Animation)"""
        self._dust_list = dust_list
        if not self._is_alive:
            if hasattr(self, '_footstep_sound') and self._footstep_sound and getattr(self, '_is_footstep_playing', False):
                self._footstep_sound.stop()
                self._is_footstep_playing = False
            return
            
        # Smooth HP: ค่อยๆ ปรับหลอดเลือดให้ไหลตามเลือดจริง
        if self._display_hp > self._current_hp:
            self._display_hp -= (self._display_hp - self._current_hp) * 0.1
            if self._display_hp < self._current_hp: self._display_hp = self._current_hp
        elif self._display_hp < self._current_hp:
            self._display_hp += (self._current_hp - self._display_hp) * 0.1
            if self._display_hp > self._current_hp: self._display_hp = self._current_hp
            
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1
            
        if self._parry_flash_timer > 0:
            self._parry_flash_timer -= 1
            
        self._apply_gravity(game_areas)
        
        # จัดการเสียงเดิน/วิ่ง (แยกเสียงตามสถานะ)
        target_sound = self._run_sound if self._is_running else self._walk_sound
        
        if not mute_footsteps and target_sound and (self._is_moving or self._is_running) and not self._is_jumping and not self._is_hurt and not self._is_attacking and not self._is_defending:
            # ถ้าเสียงที่ควรเล่น ไม่ใช่เสียงที่กำลังเล่นอยู่
            if self._current_footstep_sound != target_sound:
                if self._current_footstep_sound:
                    self._current_footstep_sound.stop()
                target_sound.play(loops=-1)
                self._current_footstep_sound = target_sound
        else:
            # หยุดเสียงถ้าไม่ได้เดิน/วิ่ง หรือติดสถานะอื่น หรือสั่ง Mute
            if self._current_footstep_sound:
                self._current_footstep_sound.stop()
                self._current_footstep_sound = None

        # ลด Cooldown
        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1
            
        # ฟื้นฟู Stamina
        if not self._is_running and not self._is_attacking:
            self._current_stamina += self._stamina_regen_rate
            if self._current_stamina > self._max_stamina:
                self._current_stamina = self._max_stamina

        # จัดการ Animation เบื้องต้น 
        if self._is_hurt:
            max_frames = 2 if self._sprite_hurt.get_width() // self._sprite_hurt.get_height() == 2 else 4
        elif self._is_attacking:
            if self._attack_type == 1:
                max_frames = 5 if self._sprite_attack.get_width() // self._sprite_attack.get_height() == 5 else 4
            else:
                max_frames = 5 if self._sprite_attack2.get_width() // self._sprite_attack2.get_height() == 5 else 4
        elif self._is_defending:
            max_frames = max(1, self._sprite_defend.get_width() // self._sprite_defend.get_height())
        elif self._is_running:
            max_frames = 7
        elif self._is_moving:
            max_frames = 8
        else:
            max_frames = 4

        self._animation_timer += 1
        
        # ปรับความหน่วงของเฟรมเพิ่มขึ้น เพื่อให้แสดงผลแต่ละท่าทางชัดและสมูทขึ้น
        if self._is_hurt:
            animation_delay = 6
        elif self._is_attacking:
            animation_delay = 5 
        elif self._is_running:
            animation_delay = 3 # สับขาไวขึ้นตอนวิ่ง
        elif self._is_moving:
            animation_delay = 6 # เดินปกติ slow life
        else:
            animation_delay = 10
            
        if self._animation_timer > animation_delay: # ความเร็วการเปลี่ยนเฟรม
            self._animation_timer = 0
            
            if self._is_hurt:
                if self._current_frame < max_frames - 1:
                    self._current_frame += 1
                else:
                    self._is_hurt = False # จบอนิเมชันบาดเจ็บ กลับไปยืน
                    self._current_frame = 0
            elif self._is_attacking:
                if self._current_frame < max_frames - 1:
                    self._current_frame += 1
                else:
                    self._is_attacking = False # จบอนิเมชันโจมตี
                    self._current_frame = 0
            elif self._is_defending:
                # ตั้งแต่จุดยกโล่ไปจนถึงเฟรมสุดท้ายและค้างไว้ที่เฟรมนั้น
                if self._current_frame < max_frames - 1:
                    self._current_frame += 1
            else:
                self._current_frame += 1
                # ป้องกัน index ทะลุ
                if self._current_frame >= max_frames:
                    self._current_frame = 0


    def draw(self, screen, show_ui=True):
        """งานระดับ AAA: วาดเงา และตัวละครพร้อมเอฟเฟกต์"""
        if not self._is_alive:
            return


        # จัดการเฟรมและภาพ
        # วาดส่วนติดต่อผู้ใช้ (UI) - HP/Stamina Bar
        if show_ui:
            # วาดชื่อผู้เล่นเหนือหลอดเลือดแบบบอส
            if self._name != "":
                if not hasattr(self, '_font'):
                    self._font = pygame.font.SysFont("Arial", 28, bold=True)
                name_surf = self._font.render(self._name, True, (255, 255, 255))
                screen.blit(name_surf, (20, 10))

            # วาดหลอดเลือด Player (มุมซ้ายบน เลื่อนลงเพื่อให้มีที่วางชื่อ)
            hp_ratio = self._current_hp / self._max_hp
            display_hp_ratio = self._display_hp / self._max_hp # อัตราที่จะใช้วาดจริง
            bar_width, bar_height = 200, 15
            x_off, y_off = 20, 40

            pygame.draw.rect(screen, (50, 50, 50), (x_off, y_off, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (x_off, y_off, int(bar_width * display_hp_ratio), bar_height)) 
            # วาดสีแดงสดทับเมื่อเลือดจริงลดฮวบเพื่อให้เห็นช่องว่าง
            if hp_ratio < display_hp_ratio:
                 pygame.draw.rect(screen, (255, 0, 0), (x_off, y_off, int(bar_width * hp_ratio), bar_height))
            
            pygame.draw.rect(screen, (255, 255, 255), (x_off, y_off, bar_width, bar_height), 2)
            
            # วาดหลอด Stamina (ใต้หลอดเลือด)
            pygame.draw.rect(screen, (50, 50, 50), (20, 60, 200, 10))
            pygame.draw.rect(screen, (200, 200, 0), (20, 60, int(200 * (self._current_stamina / self._max_stamina)), 10))
            pygame.draw.rect(screen, (255, 255, 255), (20, 60, 200, 10), 2)

        # เลือก Sprite Sheet ตามสถานะการเดิน
        if self._is_hurt:
            current_sheet = self._sprite_hurt
            max_frames = 2 if self._sprite_hurt.get_width() // self._sprite_hurt.get_height() == 2 else 4
        elif self._is_attacking:
            if self._attack_type == 1:
                current_sheet = self._sprite_attack
                max_frames = 5 if self._sprite_attack.get_width() // self._sprite_attack.get_height() == 5 else 4
            else:
                current_sheet = self._sprite_attack2
                max_frames = 5 if self._sprite_attack2.get_width() // self._sprite_attack2.get_height() == 5 else 4
        elif self._is_defending:
            current_sheet = self._sprite_defend
            max_frames = max(1, self._sprite_defend.get_width() // self._sprite_defend.get_height())
        elif self._is_running:
            current_sheet = self._sprite_run
            max_frames = 7
        elif self._is_moving:
            current_sheet = self._sprite_walk
            max_frames = 8
        else:
            current_sheet = self._sprite_idle
            max_frames = 4
        
        # คำนวณขนาดใหม่ทุกครั้งที่วาด เพื่อป้องกันปัญหาความสูง-กว้างต่างกันในแต่ละ Sprite Sheet
        frame_width = current_sheet.get_width() // max_frames
        frame_height = current_sheet.get_height()
        
        # ป้องกัน index เฟรมทะลุระหว่างเปลี่ยนสถานะ
        if self._current_frame >= max_frames:
            self._current_frame = 0

        # ดึงภาพเฟรมปัจจุบัน
        frame_rect = pygame.Rect(self._current_frame * frame_width, 0, frame_width, frame_height)
        frame_image = current_sheet.subsurface(frame_rect)
        
        # ย่อส่วนภาพ (Scale down)
        frame_image = pygame.transform.scale(frame_image, (self._scaled_width, self._scaled_height))
        
        # ลบพื้นหลัง (ถ้า spritesheet ข้างหลังไม่ได้โปร่งใส ให้ตัดสีพื้นออก)
        frame_image.set_colorkey((0, 0, 0)) 
        
        # พลิกภาพถ้าหันซ้าย
        if not self._facing_right:
            frame_image = pygame.transform.flip(frame_image, True, False)
            
        # Hit Flash: ระบายสีแดงเมื่อโดนดาเมจ
        if self._hit_flash_timer > 0:
            red_overlay = pygame.Surface(frame_image.get_size()).convert_alpha()
            red_overlay.fill((255, 0, 0, 150)) # สีแดงโปร่งแสง
            frame_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Perfect Parry Flash: แสงสีทองสว่างเมื่อบล็อกได้เป๊ะ
        if self._parry_flash_timer > 0:
            # สร้างวงกลมแสงขาว/ทอง
            size = self._parry_flash_timer * 8
            glow = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 200, 150), (size, size), size)
            pygame.draw.circle(glow, (255, 255, 255, 200), (size, size), size // 2)
            glow_rect = glow.get_rect(center=self._rect.center)
            screen.blit(glow, glow_rect, special_flags=pygame.BLEND_RGB_ADD)

        # สร้าง Rect สำหรับภาพที่วาด เพื่อให้มันมีศูนย์กลางตรงกันทั้งหันซ้ายและหันขวา
        image_rect = frame_image.get_rect()
        
        # ขยับภาพลงนิดนึงเพราะ sprite มีที่ว่างด้านล่างเพื่อให้เท้าเหยียบถึงพื้นพอดี
        image_rect.midbottom = (self._rect.midbottom[0], self._rect.midbottom[1] + 20)
            
        # วาดลงจอโดยใช้ตำแหน่ง image_rect ที่จัดกึ่งกลางไว้แล้ว
        
        screen.blit(frame_image, image_rect)