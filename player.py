import pygame
from abc import ABC, abstractmethod

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
        self._max_hp = 150
        self._current_hp = 150
        self._is_alive = True
        self._damage = 25
        self._name = ""
        
        # Load and set up sprite sheet
        # สมมติเราใช้ Idle.png และ Walk.png เป็นหลัก ตัวอย่างนี้ใช้ Idle สำหรับตอนยืน และ Walk สำหรับเดิน
        # โหลดภาพและตัดพื้นหลังที่ติดมา (colorkey) ดำ หรือปรับปรุงให้เข้ากับภาพ
        self._sprite_idle = pygame.image.load("Knight_1/Idle.png").convert_alpha()
        self._sprite_walk = pygame.image.load("Knight_1/Walk.png").convert_alpha()
        self._sprite_run = pygame.image.load("Knight_1/Run.png").convert_alpha()
        self._sprite_attack = pygame.image.load("Knight_1/Attack 1.png").convert_alpha()
        self._sprite_attack2 = pygame.image.load("Knight_1/Attack 3.png").convert_alpha()
        self._sprite_hurt = pygame.image.load("Knight_1/Hurt.png").convert_alpha()
        
        # โหลด Sprite สำหรับการป้องกัน
        self._sprite_defend = pygame.image.load("Knight_1/Protect.png").convert_alpha()
        
        # กำหนดขนาดเฟรม (Idle กว้าง 512 มี 4 เฟรม = 128x128)
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
        self._gravity = 0.2 # แรงโน้มถ่วงลดลง เพื่อให้เวลากระโดดดูสมูท ลอยๆ (สไตล์ Limbo)
        self._jump_strength = -6 # แรงกระโดดลดลงให้สอดคล้องกับแรงโน้มถ่วงใหม่
        self._current_frame = 0
        self._animation_timer = 0
        self._is_moving = False
        self._is_running = False # เพิ่มสถานะการวิ่ง
        self._is_attacking = False
        self._attack_type = 1 # เก็บประเภทการโจมตี (1 หรือ 2)
        self._is_defending = False # สถานะการป้องกัน
        self._is_hurt = False # สถานะบาดเจ็บ
        self._attack_cooldown = 0

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
    def max_hp(self):
        """Getter สำหรับ HP สูงสุด"""
        return self._max_hp

    @property
    def name(self):
        return self._name
        
    @name.setter
    def name(self, value):
        self._name = value

    def take_damage(self, amount):
        """Method เปิดให้ภายนอกสร้างความเสียหาย (Polymorphism: ตัวละครทุกตัวมีฟังก์ชันรับความเสียหายที่อาจต่างกัน)"""
        if self._is_alive:
            # ถ้ายกโล่ป้องกันอยู่ จะลดดาเมจที่ได้รับ
            if self._is_defending:
                amount = int(amount * 0.1) # เหลือดาเมจแค่ 20%
                
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._is_alive = False
            else:
                self._is_hurt = True
                self._current_frame = 0
        
    def _apply_gravity(self, game_areas):
        """Method ภายใน (Encapsulated) สำหรับคำนวณแรงโน้มถ่วงและการชนพื้น"""
        self._velocity_y += self._gravity
        self._rect.y += self._velocity_y

        # เช็คการชนกับพื้นที่ที่เดินได้ (WalkableArea)
        on_ground = False
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                # ถ้ากำลังตก (velocity_y > 0) และชนกับพื้น
                if self._velocity_y > 0 and self._rect.bottom <= area.rect.bottom:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
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
        
        # จัดการปุ่ม X หรือคลิกขวา (mouse_btns[2]) สำหรับยกโล่ป้องกัน
        if keys[pygame.K_x] or mouse_btns[2]:
            if not self._is_defending:
                self._current_frame = 0 # เริ่มต้นเฟรมป้องกัน
            self._is_defending = True
        else:
            self._is_defending = False

        if self._is_defending:
            return # ไม่ให้เดินตอนกำลังยกโล่
        
        # ถือปุ่ม Shift ซ้ายเพื่อวิ่ง (Speed ห่างจากเดินนิดหน่อย)
        current_speed = self._speed * 1.8 if keys[pygame.K_LSHIFT] else self._speed
        
        # เช็คปุ่มวิ่ง + ปุ่มเดิน (ซ้ายหรือขวา หรือ A หรือ D)
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_a] or keys[pygame.K_d]):
            self._is_running = True
        
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
            self._velocity_y = self._jump_strength
            self._is_jumping = True
            
        self._x = self._rect.x

    def attack(self, target=None, attack_type=1):
        if self._is_defending or self._is_hurt:
            return # ห้ามโจมตีถ้ายกโล่อยู่ หรือบาดเจ็บอยู่
            
        if self._attack_cooldown == 0 and self._is_alive:
            self._is_attacking = True
            self._attack_type = attack_type
            self._current_frame = 0
            self._attack_cooldown = 40 # ระยะเวลาหน่วงระหว่างการโจมตีแต่ละครั้ง
            
            # โจมตีโดนเป้าหมาย
            if target and getattr(target, 'is_alive', False):
                distance = target.rect.centerx - self._rect.centerx
                # เช็คว่าหันหน้าถูกทางและอยู่ในระยะโจมตี
                if (self._facing_right and distance > 0) or (not self._facing_right and distance < 0):
                    if abs(distance) < 90: # ระยะโจมตีของ Player
                        target.take_damage(self._damage)

    def update(self, game_areas):
        """Override เพื่ออัปเดตฟิสิกส์และการขยับภาพ (Animation)"""
        if not self._is_alive:
            return
        self._apply_gravity(game_areas)
        
        # ลด Cooldown
        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1

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
            animation_delay = 4 # สับขาไวขึ้นนิดนึงตอนวิ่ง
        elif self._is_moving:
            animation_delay = 2 
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

    def draw(self, screen):
        """Override เพื่อวาดภาพตัวละครลงจอ โดยตัดส่วนนึงมาจาก Sprite Sheet"""
        if not self._is_alive:
            return
            
        # วาดชื่อผู้เล่นเหนือหลอดเลือดแบบบอส
        if self._name != "":
            if not hasattr(self, '_font'):
                self._font = pygame.font.SysFont("Arial", 28, bold=True)
            name_surf = self._font.render(self._name, True, (255, 255, 255))
            screen.blit(name_surf, (20, 10))

        # วาดหลอดเลือด Player (มุมซ้ายบน เลื่อนลงเพื่อให้มีที่วางชื่อ)
        pygame.draw.rect(screen, (50, 50, 50), (20, 40, 200, 15))
        pygame.draw.rect(screen, (0, 200, 0), (20, 40, int(200 * (self._current_hp / self._max_hp)), 15))
        pygame.draw.rect(screen, (255, 255, 255), (20, 40, 200, 15), 2)

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
            
        # สร้าง Rect สำหรับภาพที่วาด เพื่อให้มันมีศูนย์กลางตรงกันทั้งหันซ้ายและหันขวา
        image_rect = frame_image.get_rect()
        
        # วางศูนย์กลางด้านล่างของภาพ (Midbottom) ให้อยู่จุดกึ่งกลางด้านล่างของตัวชน (Hitbox)
        image_rect.midbottom = self._rect.midbottom
            
        # วาดลงจอโดยใช้ตำแหน่ง image_rect ที่จัดกึ่งกลางไว้แล้ว
        screen.blit(frame_image, image_rect)