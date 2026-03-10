import pygame
from boss import Enemy

# =====================================================================
# SOLID: 1. Single Responsibility Principle (SRP)
# =====================================================================
# ส่วนจัดการพิกเซลและภาพ (Sprite) แยกจากความรับผิดชอบหลักของตัวละคร 
# ทำให้สามารถนำไปใช้ซ้ำ (Reusable) กับตัวละครอื่นได้ และการทำงานนี้จะเฉพาะเจาะจงที่เรื่องภาพ
class SpriteManager:
    """Class ทำหน้าที่จัดการโหลดและตัดแบ่งภาพ Sprite Sheet"""
    def __init__(self, sheet_path, cols=1, rows=1):
        self._sheet = pygame.image.load(sheet_path).convert_alpha()
        self._cols = cols
        self._rows = rows
        self._frame_width = self._sheet.get_width() // cols
        self._frame_height = self._sheet.get_height() // rows
        
    def get_frame(self, row, col, scale=1.0, flip=False):
        """ดึงเฟรมแบบปลอดภัย ป้องกัน Index out of range"""
        x = (col * self._frame_width) % self._sheet.get_width()
        y = (row * self._frame_height) % self._sheet.get_height()
        
        rect = pygame.Rect(x, y, self._frame_width, self._frame_height)
        try:
            image = self._sheet.subsurface(rect).copy()
        except ValueError:
            image = pygame.Surface((self._frame_width, self._frame_height), pygame.SRCALPHA)
            
        if scale != 1.0:
            image = pygame.transform.scale(image, (int(self._frame_width * scale), int(self._frame_height * scale)))
            
        image.set_colorkey((0, 0, 0)) # สีดำ = โปร่งใส
        if flip:
            image = pygame.transform.flip(image, True, False)
        return image

# =====================================================================
# 6. Composition (การประกอบตัว) & Polymorphism
# =====================================================================
class SpellEffect:
    """Class แบบร่างสำหรับเอฟเฟคเวทมนตร์ (Polymorphism)"""
    def __init__(self, x, y, damage, target):
        self._x = x
        self._y = y
        self._damage = damage
        self._target = target
        self._is_active = True

    @property
    def is_active(self):
        return self._is_active

    def update(self):
        pass

    def draw(self, screen):
        pass

class NecroticOrb(SpellEffect):
    """ลูกไฟวิญญาณสีม่วง วิ่งเข้าหาเป้าหมาย"""
    def __init__(self, x, y, damage, target):
        super().__init__(x, y, damage, target)
        self._speed = 4
        self._radius = 12
        self._color = (138, 43, 226) # สีเพอร์เพิลสว่าง

    def update(self):
        if not self._is_active or not self._target:
            return

        # ถ้า target ตายหรือหายไปแล้ว ให้ดับลูกไฟทันที (ป้องกันโจมตีข้ามฉาก)
        if hasattr(self._target, 'is_alive') and not self._target.is_alive:
            self._is_active = False
            return

        # ถ้าลูกไฟออกนอกหน้าจอ ให้ดับตัวเองทันที (ป้องกันโจมตีข้ามฉาก)
        if self._x < -50 or self._x > 850 or self._y < -50 or self._y > 550:
            self._is_active = False
            return

        # คำนวณระยะห่างระหว่างลูกไฟและผู้เล่น
        dx = self._target.rect.centerx - self._x
        dy = self._target.rect.centery - self._y
        dist = (dx**2 + dy**2)**0.5

        if dist < self._speed + 10: # ระยะชน
            if hasattr(self._target, 'take_damage'):
                self._target.take_damage(self._damage)
            self._is_active = False # ปิดการทำงานเมื่อชนแล้ว
            return

        # คำนวณการเดินของลูกไฟ
        self._x += (dx / dist) * self._speed
        self._y += (dy / dist) * self._speed

    def draw(self, screen):
        if self._is_active:
            # ลูกแก้วแกนกลาง
            pygame.draw.circle(screen, self._color, (int(self._x), int(self._y)), self._radius)
            # ออร่าเรืองแสงรอบนอกหลอกๆ
            pygame.draw.circle(screen, (200, 150, 255), (int(self._x), int(self._y)), self._radius + 4, 3)

# =====================================================================
# SOLID: 2. Open/Closed Principle (OCP)
# =====================================================================
# สร้าง Interface รองรับรูปแบบการโจมตีใหม่ๆ สามารถเพิ่มระบบยิงธนู หรืออื่นๆได้ในภายหลัง
class IAttackStrategy:
    def execute_attack(self, attacker, target):
        pass

class SpatialMagicAttack(IAttackStrategy):
    """ร่ายเวทมนตร์กว้าง หรือโจมตีระยะไกล (Strategy Pattern)"""
    def execute_attack(self, attacker, target):
        # แทนที่จะใช้ดาเมจทันที เราสร้างโปรเจกไทล์แทน!
        orb = NecroticOrb(attacker.rect.centerx, attacker.rect.centery - 20, attacker._damage, target)
        # ฝากลูกแก้วให้ Necromancer เอาไปเรนเดอร์เอง (Encapsulation)
        if hasattr(attacker, 'add_effect'):
            attacker.add_effect(orb)

# =====================================================================
# 3. Inheritance (สืบทอดจาก Enemy/Character)
# 4. Encapsulation (ปกปิดตัวแปรและสถานะ)
# SOLID: 3. Liskov Substitution Principle (LSP) - มันใช้ทดแทน Enemy ใน main.py ได้
# SOLID: 5. Dependency Inversion Principle (DIP) - พึ่งพากลยุทธ์นามธรรม (IAttackStrategy)
# =====================================================================
class Necromancer(Enemy):
    def __init__(self, x, y):
        # สืบทอดลักษณะแบบ Enemy
        super().__init__(x, y, speed=1.5, hp=150, name="Necromancer")
        
        # OCP & DIP: พึ่งพากลยุทธ์ที่จะโจมตี (ไม่ใช่ hard code ว่าตายตัวแบบใด)
        self._attack_strategy = SpatialMagicAttack()
        self._damage = 5
        
        # SRP: โยนเรื่องจัดการ sprite แผ่นยักษ์ไว้ในตู้อื่น
        # สมมติ sprite sheet ประกอบด้วย 17 คอลัมน์ แถวละ 1 แอ็คชั่น (7 แถว)
        self._sprite_manager = SpriteManager("assets/mons/Necromancer_creativekind-Sheet.png", cols=17, rows=7)
        
        # Encapsulation (Hitbox)
        # ขยาย Hitbox เพิ่มขึ้นตาม Scale ที่ใหญ่ขึ้น
        self._rect = pygame.Rect(x, y, 100, 130)
        self._detect_range = 450
        self._attack_range = 150 # ระยะห่างพอสมควร
        self._attack_cooldown = 0
        self._facing_right = False
        
        self._action = "idle" 
        self._current_frame = 0
        self._animation_timer = 0
        self._current_row = 0
        
        # คิวของเวทมนตร์ทั้งหมดที่กำลังยิงอยู่
        self._active_effects = []

    def add_effect(self, effect):
        """เพิ่มเอฟเฟคเข้าระบบการแสดงผลของตัวมันเอง"""
        self._active_effects.append(effect)

    # =====================================================================
    # 5. Polymorphism - Overriding รูปแบบปฏิสัมพันธ์
    # =====================================================================
    def take_damage(self, amount):
        if self._current_hp > 0 and self._action != "dead":
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._action = "dead"
                self._current_frame = 0
                self._animation_timer = 0
            else:
                self._action = "hurt"
                self._current_frame = 0
                self._animation_timer = 0
                
    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0
        self._attack_cooldown = 100 # เวทใหญ่นานหน่อย
        self._attack_strategy.execute_attack(self, target)

    def update(self, game_areas, player=None):
        # อัปเดตเอฟเฟคต่างๆ แม้มอนสเตอร์จะตายไปแล้วหรือยังอยู่ (เพื่อให้ลูกไฟพุ่งจนสุดทาง)
        for effect in self._active_effects:
            effect.update()
            
        # ล้างเอฟเฟคที่ชนไปแล้ว (หมดอายุ) ออกจากคิว
        self._active_effects = [e for e in self._active_effects if e.is_active]
            
        if not self._is_alive:
            return
            
        # ควบคุมพฤติกรรม
        if self._action != "dead":
            self._handle_ai(player)
            
        # ฟิสิกส์มอนสเตอร์ทั่วไป (Polymorphism: อาจเบากว่า/ลอยกว่าบอสได้ถ้าแก้ Gravity)
        self._velocity_y += 0.5
        self._rect.y += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0 and self._rect.bottom <= area.rect.bottom:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
                    
        self._update_animation()

    def _handle_ai(self, player):
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
                    self._rect.x += self._speed if self._facing_right else -self._speed
                elif self._action != "attack":
                    self._action = "idle"
        else:
            if self._action not in ("attack", "hurt"):
                self._action = "idle"

    def _update_animation(self):
        self._animation_timer += 1
        
        # Map แอคชันกับความเร็วและจำนวนเฟรมคร่าวๆ
        if self._action == "dead":
            max_frames, speed_anim, row = 9, 8, 4  
        elif self._action == "hurt":
            max_frames, speed_anim, row = 5, 5, 3
        elif self._action == "attack":
            max_frames, speed_anim, row = 13, 5, 2
        elif self._action == "walk":
            max_frames, speed_anim, row = 8, 5, 1
        else: # idle
            max_frames, speed_anim, row = 8, 7, 0
            
        if self._animation_timer >= speed_anim:
            self._animation_timer = 0
            if self._action == "dead":
                if self._current_frame < max_frames - 1:
                    self._current_frame += 1
                else:
                    self._is_alive = False
            elif self._action == "hurt":
                self._current_frame += 1
                if self._current_frame >= max_frames:
                    self._current_frame = 0
                    self._action = "idle"
            else:
                self._current_frame += 1
                if self._current_frame >= max_frames:
                    self._current_frame = 0
                    if self._action == "attack":
                        self._action = "idle"
                        
        self._current_row = row

    def draw(self, screen):
        # วาดเอฟเฟคก่อน/หลังวาดตัวมอนสเตอร์ได้ตามที่ต้องการ
        for effect in self._active_effects:
            effect.draw(screen)
            
        if not self._is_alive:
            return
            
        frame_image = self._sprite_manager.get_frame(
            row=self._current_row, 
            col=self._current_frame, 
            scale=2.5, 
            flip=not self._facing_right
        )
        
        image_rect = frame_image.get_rect()
        image_rect.midbottom = (self._rect.centerx, self._rect.bottom + 10) # ชดเชยที่ว่างล่างสุด
        
        screen.blit(frame_image, image_rect)

        # หลอดเลือด HP ประจำตัวมอนสเตอร์ (ขนาดเล็ก) บนศีรษะ
        if self._current_hp < self._max_hp:
            hp_ratio = self._current_hp / self._max_hp
            pygame.draw.rect(screen, (50, 50, 50), (self._rect.centerx - 20, self._rect.top - 15, 40, 5))
            pygame.draw.rect(screen, (200, 0, 0), (self._rect.centerx - 20, self._rect.top - 15, int(40 * hp_ratio), 5))
