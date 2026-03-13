import pygame
import os
import random
import math
from boss import Enemy

# =====================================================================
# 1. Sprite & FX Management
# =====================================================================
class SpriteManager:
    """Class ทำหน้าที่จัดการโหลดและตัดแบ่งภาพ Sprite Sheet"""
    def __init__(self, sheet_path, cols=1, rows=1):
        self._sheet = pygame.image.load(sheet_path).convert_alpha()
        self._cols = cols
        self._frame_width = self._sheet.get_width() // cols
        self._frame_height = self._sheet.get_height() // rows 
        
    def get_frame(self, row, col, scale=1.0, flip=False):
        x = (col * self._frame_width) % self._sheet.get_width()
        y = (row * self._frame_height) % self._sheet.get_height()
        rect = pygame.Rect(x, y, self._frame_width, self._frame_height)
        try:
            image = self._sheet.subsurface(rect).copy()
        except ValueError:
            image = pygame.Surface((self._frame_width, self._frame_height), pygame.SRCALPHA)
            
        if scale != 1.0:
            image = pygame.transform.scale(image, (int(self._frame_width * scale), int(self._frame_height * scale)))
        if flip:
            image = pygame.transform.flip(image, True, False)
        return image

class IAttackStrategy:
    def execute_attack(self, attacker, target): pass

class MeleeComboAttack(IAttackStrategy):
    def execute_attack(self, attacker, target): pass

# =====================================================================
# 2. Projectile Systems
# =====================================================================
class SpellEffect:
    def __init__(self, x, y, damage, target):
        self._x = x
        self._y = y
        self._damage = damage
        self._target = target
        self._is_active = True
    @property
    def is_active(self): return self._is_active
    def update(self, **kwargs): pass
    def draw(self, screen): pass

class DarkFireball(SpellEffect):
    """ลูกไฟสีแดงสว่าง (โหมดใหม่) เพื่อความชัดเจน ในฉากที่ 3"""
    def __init__(self, x, y, damage, target, source_enemy=None):
        super().__init__(x, y, damage, target)
        self._speed = 7
        self._radius = 18
        self._source_enemy = source_enemy
        # สีใหม่: ส้มสว่างขอบแดง เพื่อให้มองเห็นชัดในฉากมืด
        self._inner_color = (255, 200, 0)
        self._outer_color = (255, 50, 0)

    def update(self, shockwave_list=None, **kwargs):
        if not self._is_active or not self._target: return
        if not self._target.is_alive:
            self._is_active = False
            return
            
        # เคลื่อนที่เข้าหาเป้าหมาย (Player)
        dx = self._target.rect.centerx - self._x
        dy = (self._target.rect.centery) - self._y
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 40: # Collision Check (เพิ่มระยะเช็คให้โดนง่ายขึ้น)
            if hasattr(self._target, 'take_damage'):
                # สร้างความเสียหาย
                self._target.take_damage(self._damage, shockwave_list=shockwave_list)
            self._is_active = False
            return

        if dist != 0:
            self._x += (dx / dist) * self._speed
            self._y += (dy / dist) * self._speed
            
        # ออกนอกหน้าจอ
        if self._x < -100 or self._x > 900 or self._y < -100 or self._y > 600:
            self._is_active = False

    def draw(self, screen):
        if self._is_active:
            # วาดออร่า
            for i in range(3):
                alpha = 100 - (i * 30)
                s = pygame.Surface((self._radius*4, self._radius*4), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self._outer_color, alpha), (self._radius*2, self._radius*2), self._radius + (i*4))
                screen.blit(s, (int(self._x - self._radius*2), int(self._y - self._radius*2)))
            
            # วาดตัวลูกไฟ
            pygame.draw.circle(screen, self._outer_color, (int(self._x), int(self._y)), self._radius)
            pygame.draw.circle(screen, self._inner_color, (int(self._x), int(self._y)), self._radius - 4)

class EvilWizardAttack(IAttackStrategy):
    def execute_attack(self, attacker, target):
        # เสกออกมาจากตรงยอดไม้เท้า (ปรับให้ตรงกับแอนิเมชั่นที่ถือไม้เท้าสูง)
        ball = DarkFireball(attacker.rect.centerx, attacker.rect.top - 80, attacker._damage, target, source_enemy=attacker)
        attacker.add_effect(ball)

# =====================================================================
# 3. Monster Classes
# =====================================================================
class EvilWizard(Enemy):
    """Monster บอสฉากที่ 3 (Wizard มืด)"""
    def __init__(self, x, y):
        super().__init__(x, y, speed=1.8, hp=350, name="Evil Wizard")
        self._damage = 25
        self._attack_strategy = EvilWizardAttack()
        
        path = "assets/mons/EVil Wizard 2/Sprites/"
        self._sprites = {
            "idle": SpriteManager(path + "Idle.png", cols=8, rows=1),
            "walk": SpriteManager(path + "Run.png", cols=8, rows=1),
            "attack": SpriteManager(path + "Attack1.png", cols=8, rows=1),
            "hurt": SpriteManager(path + "Take hit.png", cols=3, rows=1),
            "dead": SpriteManager(path + "Death.png", cols=7, rows=1)
        }
        
        self._rect = pygame.Rect(x, y, 70, 110)
        self._detect_range = 500
        self._attack_range = 350
        self._attack_cooldown = 0
        self._facing_right = False
        
        self._action = "idle"
        self._current_frame = 0
        self._animation_timer = 0
        self._active_effects = []
        self._hit_flash_timer = 0

        try:
            if os.path.exists("assets/sound/spell.wav"):
                self._spell_sound = pygame.mixer.Sound("assets/sound/spell.wav")
                self._spell_sound.set_volume(0.3)
            else: self._spell_sound = None
        except: self._spell_sound = None

    def take_damage(self, amount):
        if self._current_hp > 0 and self._action != "dead":
            super().take_damage(amount)
            if self._current_hp <= 0:
                self._action = "dead"
                self._current_frame = 0
            else:
                self._action = "hurt"
                self._current_frame = 0
            self._animation_timer = 0

    def add_effect(self, effect):
        self._active_effects.append(effect)

    def update(self, game_areas, player=None, *args, **kwargs):
        shockwave_list = kwargs.get('shockwave_list')
        
        # อัปเดตลูกไฟ
        for effect in self._active_effects:
            effect.update(shockwave_list=shockwave_list)
        self._active_effects = [e for e in self._active_effects if e.is_active]
            
        if not self._is_alive: return
            
        if self._action != "dead":
            if getattr(self, '_stun_timer', 0) > 0:
                self._stun_timer -= 1
                self._is_stunned = True
                if self._stun_timer <= 0: self._is_stunned = False
            else: self._is_stunned = False

            if not self._is_stunned:
                self._handle_ai(player, game_areas)
            
        # Smooth HP & Hit Flash
        if self._display_hp > self._current_hp:
            self._display_hp -= (self._display_hp - self._current_hp) * 0.1
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1
            
        # Physics
        self._velocity_y += 0.5
        self._rect.y += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
                    
        self._update_animation(player)

    def _handle_ai(self, player, game_areas):
        if player and player.is_alive:
            distance = player.rect.centerx - self._rect.centerx
            self._facing_right = distance > 0
            abs_dist = abs(distance)
            
            if self._attack_cooldown > 0:
                self._attack_cooldown -= 1
                
            if self._action != "hurt" and self._action != "attack":
                move_dir = 0
                # รักษาระยะห่างที่เหมาะสม (200 - 350 พิกเซล)
                if abs_dist < 200: 
                    # ถอยหลังหนี (ถ้าผู้เล่นอยู่ขวา ให้ไปซ้าย)
                    move_dir = -1 if self._facing_right else 1
                    self._speed = 2.5 # เร่งฝีเท้าตอนหนี
                elif abs_dist > 350:
                    # เดินเข้าหาเพื่อให้ได้ระยะยิง (ถ้าผู้เล่นอยู่ขวา ให้ไปขวา)
                    move_dir = 1 if self._facing_right else -1
                    self._speed = 1.8 # ความเร็วปกติ
                else:
                    # อยู่ในระยะยิงที่เหมาะสมแล้ว: โจมตี หรือ ยืนรอจังหวะ
                    if self._attack_cooldown == 0:
                        self.attack(player)
                    else:
                        # ขยับตัวหยั่งเชิงเล็กน้อย (สุ่ม) ให้ดูฉลาด
                        if random.random() < 0.02: move_dir = random.choice([-1, 1])
                
                if move_dir != 0:
                    new_x = self._rect.x + (move_dir * self._speed)
                    # Check edge (ขอบพื้น)
                    check_x = new_x + (self._rect.width if move_dir > 0 else 0)
                    check_rect = pygame.Rect(check_x, self._rect.bottom + 5, 2, 2)
                    has_ground = any(a.is_walkable() and a.rect.colliderect(check_rect) for a in game_areas)
                    
                    if has_ground:
                        self._rect.x = new_x
                        self._action = "walk"
                    elif self._action != "attack":
                         self._action = "idle"
                elif self._action != "attack":
                    self._action = "idle"
            self._player_ref = player
        else:
            if self._action not in ("attack", "hurt", "dead"): self._action = "idle"
            self._player_ref = None

    def _update_animation(self, player=None):
        self._animation_timer += 1
        frame_counts = {"idle": 8, "walk": 8, "attack": 8, "hurt": 3, "dead": 7}
        anim_speeds = {"idle": 10, "walk": 7, "attack": 12, "hurt": 6, "dead": 10}
        
        max_frames = frame_counts.get(self._action, 8)
        speed_anim = anim_speeds.get(self._action, 8)
        
        if self._animation_timer >= speed_anim:
            self._animation_timer = 0
            self._current_frame += 1
            
            # เสกบอลตอนเฟรมที่ 6 (จังหวะชูไม้เท้าขึ้นสูงสุด)
            if self._action == "attack" and self._current_frame == 6:
                if self._player_ref:
                    self._attack_strategy.execute_attack(self, self._player_ref)
                    if self._spell_sound: self._spell_sound.play()

            if self._current_frame >= max_frames:
                if self._action == "dead":
                    self._current_frame = max_frames - 1
                    self._is_alive = False
                elif self._action in ("hurt", "attack"):
                    self._current_frame = 0
                    self._action = "idle" if self._current_hp > 0 else "dead"
                else: self._current_frame = 0

    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0
        self._animation_timer = 0
        self._attack_cooldown = 150

    def draw(self, screen):
        # วาดลูกไฟก่อน
        for effect in self._active_effects:
            effect.draw(screen)
            
        if not self._is_alive: return
            
        manager = self._sprites.get(self._action, self._sprites["idle"])
        frame_image = manager.get_frame(0, self._current_frame, scale=2.2, flip=not self._facing_right)
        
        if self._hit_flash_timer > 0:
            flash_surf = frame_image.copy()
            flash_surf.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            flash_surf.set_alpha(160)
            frame_image.blit(flash_surf, (0, 0))

        image_rect = frame_image.get_rect()
        # ปรับค่า Offset เพิ่มขึ้นอีกเพื่อให้เท้าแตะพื้นพอดี (ไฟล์ Sprite นี้มี padding ด้านล่างเยอะมาก)
        image_rect.midbottom = (self._rect.centerx, self._rect.bottom + 185)
        screen.blit(frame_image, image_rect)

        # HP Bar
        if self._current_hp < self._max_hp:
            hp_ratio = self._current_hp / self._max_hp
            pygame.draw.rect(screen, (40, 40, 40), (self._rect.centerx - 25, self._rect.top - 15, 50, 5))
            pygame.draw.rect(screen, (220, 0, 50), (self._rect.centerx - 25, self._rect.top - 15, int(50 * hp_ratio), 5))

class NightBorne(Enemy):
    """Monster จากฉากที่ 1"""
    def __init__(self, x, y):
        super().__init__(x, y, speed=2.2, hp=250, name="NightBorne")
        self._damage = 20
        self._sprite_manager = SpriteManager("assets/mons/NightBorne/NightBorne.png", cols=23, rows=5)
        self._rect = pygame.Rect(x, y, 90, 100)
        self._detect_range = 800
        self._attack_range = 80
        self._attack_cooldown = 0
        self._facing_right = False
        self._action = "idle" 
        self._current_frame = 0
        self._animation_timer = 0
        self._current_row = 0
        self._hit_flash_timer = 0

        try:
            if os.path.exists("assets/sound/alexis_gaming_cam-epee-342933.mp3"):
                self._attack_sound = pygame.mixer.Sound("assets/sound/alexis_gaming_cam-epee-342933.mp3")
                self._attack_sound.set_volume(0.4)
            else: self._attack_sound = None
        except: self._attack_sound = None

    def take_damage(self, amount):
        if self._current_hp > 0 and self._action != "dead":
            super().take_damage(amount)
            if self._current_hp <= 0:
                self._action = "dead"
            else:
                self._action = "hurt"
            self._current_frame = 0
            self._animation_timer = 0

    def update(self, game_areas, player=None, *args, **kwargs):
        if not self._is_alive: return
        if self._action != "dead":
            if getattr(self, '_stun_timer', 0) > 0:
                self._stun_timer -= 1
                self._is_stunned = True
                if self._stun_timer <= 0: self._is_stunned = False
            else: self._is_stunned = False

            if not self._is_stunned:
                self._handle_ai(player, game_areas)

        if self._display_hp > self._current_hp:
            self._display_hp -= (self._display_hp - self._current_hp) * 0.1
        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1
            
        self._velocity_y += 0.5
        self._rect.y += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0:
                    self._rect.bottom = area.rect.top
                    self._velocity_y = 0
            
        self._update_animation(player)

    def _handle_ai(self, player, game_areas):
        if player and player.is_alive:
            distance = player.rect.centerx - self._rect.centerx
            self._facing_right = distance > 0
            abs_dist = abs(distance)
            abs_y = abs(player.rect.centery - self._rect.centery)
            
            if self._attack_cooldown > 0: self._attack_cooldown -= 1
                
            if self._action != "hurt":
                # ตรวจสอบระยะโจมตี
                if abs_dist <= self._attack_range and abs_y < 100 and self._attack_cooldown == 0 and self._action != "attack":
                    self.attack(player)
                elif self._action != "attack":
                    # พฤติกรรม Hit & Run: ถ้าเพิ่งตีเสร็จ (Cooldown สูง) ให้พยายามเว้นระยะห่าง
                    move_dir = 0
                    if self._attack_cooldown > 80:
                        move_dir = -1 if self._facing_right else 1 # เดินถอยหลังหลังโจมตี
                    elif abs_dist <= self._detect_range:
                        move_dir = 1 if self._facing_right else -1 # เดินเข้าหาเพื่อล่า
                        
                    if move_dir != 0:
                        # เร่งความเร็วเป็น 1.5 เท่าตอนถอยฉุกเฉิน
                        adjusted_speed = self._speed * 1.5 if move_dir != (1 if self._facing_right else -1) else self._speed
                        new_x = self._rect.x + (move_dir * adjusted_speed)
                        # Check edge (ขอบพื้น)
                        check_x = new_x + (self._rect.width if move_dir > 0 else 0)
                        check_rect = pygame.Rect(check_x, self._rect.bottom + 5, 2, 2)
                        if any(a.is_walkable() and a.rect.colliderect(check_rect) for a in game_areas):
                            self._rect.x = new_x
                            self._action = "walk"
                        else: self._action = "idle"
                    else:
                        # สุ่มขยับตัวเล็กน้อยเมื่อยืนเฉยๆ
                        if random.random() < 0.02: self._action = "walk"
                        else: self._action = "idle"
        else:
            if self._action not in ("attack", "hurt"): self._action = "idle"

    def attack(self, target):
        self._action = "attack"
        self._current_frame = 0
        self._attack_cooldown = 120
        if self._attack_sound: self._attack_sound.play()
        # ดาเมจทำตอนเฟรมอนิเมชั่น (LSP)
        self._player_ref = target

    def _update_animation(self, player=None):
        self._animation_timer += 1
        anim_data = {
            "dead": (23, 4, 4), "hurt": (5, 6, 3), "attack": (12, 5, 2), "walk": (6, 5, 1), "idle": (9, 7, 0)
        }
        max_f, speed, row = anim_data.get(self._action, (9, 7, 0))
        
        if self._animation_timer >= speed:
            self._animation_timer = 0
            self._current_frame += 1
            self._current_row = row
            
            # ดรอปดาเมจตอนเฟรมที่ 11 (จังหวะดาบฟันลงพื้นพอดีเป๊ะ)
            if self._action == "attack" and self._current_frame == 11 and hasattr(self, '_player_ref') and self._player_ref:
                dist = abs(self._player_ref.rect.centerx - self._rect.centerx)
                if dist <= self._attack_range + 50:
                    self._player_ref.take_damage(self._damage)

            if self._current_frame >= max_f:
                if self._action == "dead":
                    self._current_frame = max_f - 1
                    self._is_alive = False
                elif self._action in ("hurt", "attack"):
                    self._current_frame = 0
                    self._action = "idle" if self._current_hp > 0 else "dead"
                else: self._current_frame = 0

    def draw(self, screen):
        if not self._is_alive: return
        img = self._sprite_manager.get_frame(self._current_row, self._current_frame, scale=4.5, flip=not self._facing_right)
        if self._hit_flash_timer > 0:
            f = img.copy(); f.fill((255,255,255), special_flags=pygame.BLEND_RGB_ADD); f.set_alpha(150); img.blit(f, (0,0))
        r = img.get_rect(); r.midbottom = (self._rect.centerx, self._rect.bottom + 95)
        screen.blit(img, r)
        if self._current_hp < self._max_hp:
            ratio = self._current_hp / self._max_hp
            pygame.draw.rect(screen, (50,50,50), (self._rect.centerx-20, self._rect.top-15, 40, 5))
            pygame.draw.rect(screen, (200,0,0), (self._rect.centerx-20, self._rect.top-15, int(40*ratio), 5))
