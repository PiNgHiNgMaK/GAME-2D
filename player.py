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
    def handle_input(self, keys):
        """จัดการการกรอกข้อมูลจากผู้เล่น (ปุ่มกด)"""
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
        
        # Load and set up sprite sheet
        # สมมติเราใช้ Idle.png และ Walk.png เป็นหลัก ตัวอย่างนี้ใช้ Idle สำหรับตอนยืน และ Walk สำหรับเดิน
        # โหลดภาพและตัดพื้นหลังที่ติดมา (colorkey) ดำ หรือปรับปรุงให้เข้ากับภาพ
        self._sprite_idle = pygame.image.load("Knight_1/Idle.png").convert_alpha()
        self._sprite_walk = pygame.image.load("Knight_1/Walk.png").convert_alpha()
        self._sprite_run = pygame.image.load("Knight_1/Run.png").convert_alpha()
        
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

    @property
    def rect(self):
        """Getter สำหรับ Hitbox เอาไว้ใช้เช็คการชนกับ Area"""
        return self._rect
        
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
    def handle_input(self, keys):
        """Override ให้รับปุ่มซ้าย, ขวา, สเปซบาร์, และปุ่มวิ่ง (Shift)"""
        self._is_moving = False
        self._is_running = False
        
        # ถือปุ่ม Shift ซ้ายเพื่อวิ่ง (Speed ห่างจากเดินนิดหน่อย)
        current_speed = self._speed * 1.8 if keys[pygame.K_LSHIFT] else self._speed
        
        if keys[pygame.K_LSHIFT] and (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self._is_running = True
        
        if keys[pygame.K_LEFT]:
            self._rect.x -= current_speed
            self._facing_right = False
            self._is_moving = True
        if keys[pygame.K_RIGHT]:
            self._rect.x += current_speed
            self._facing_right = True
            self._is_moving = True
            
        # ป้องกันไม่ให้เดินหลุดออกไปนอกหน้าจอเกมซ้ายเกินไป (หน้าจอกว้าง 800)
        # แต่ปล่อยให้เดินทะลุขวาไปได้นิดหน่อย เพื่อใช้เป็นจุดเช็คเปลี่ยนฉาก
        if self._rect.left < 0:
            self._rect.left = 0
        if self._rect.right > 850: # ยอมให้เกิน 800 ไป 50 พิเซลเพื่อแตะขอบ
            self._rect.right = 850
            
        if keys[pygame.K_SPACE] and not self._is_jumping:
            self._velocity_y = self._jump_strength
            self._is_jumping = True
            
        self._x = self._rect.x

    def update(self, game_areas):
        """Override เพื่ออัปเดตฟิสิกส์และการขยับภาพ (Animation)"""
        self._apply_gravity(game_areas)
        
        # จัดการ Animation เบื้องต้น 
        # (Idle = 4 frame, Walk = 8 frame, Run = 7 frame รูป Run กว้าง 896)
        if self._is_running:
            max_frames = 7
            self._frame_width = int(self._sprite_run.get_width() / 7)
        elif self._is_moving:
            max_frames = 8
            self._frame_width = int(self._sprite_walk.get_width() / 8)
        else:
            max_frames = 4
            self._frame_width = int(self._sprite_idle.get_width() / 4)

        self._animation_timer += 1
        
        # ปรับความหน่วงของเฟรมเพิ่มขึ้น เพื่อให้แสดงผลแต่ละท่าทางชัดและสมูทขึ้น
        if self._is_running:
            animation_delay = 4 # สับขาไวขึ้นนิดนึงตอนวิ่ง
        elif self._is_moving:
            animation_delay = 2 
        else:
            animation_delay = 10
            
        if self._animation_timer > animation_delay: # ความเร็วการเปลี่ยนเฟรม
            self._animation_timer = 0
            self._current_frame += 1

        # ป้องกัน index ทะลุ
        if self._current_frame >= max_frames:
            self._current_frame = 0

    def draw(self, screen):
        """Override เพื่อวาดภาพตัวละครลงจอ โดยตัดส่วนนึงมาจาก Sprite Sheet"""
        # เลือก Sprite Sheet ตามสถานะการเดิน
        if self._is_running:
            current_sheet = self._sprite_run
        elif self._is_moving:
            current_sheet = self._sprite_walk
        else:
            current_sheet = self._sprite_idle
        
        # ดึงภาพเฟรมปัจจุบัน
        frame_rect = pygame.Rect(self._current_frame * self._frame_width, 0, self._frame_width, self._frame_height)
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