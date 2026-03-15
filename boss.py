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
    บอส Demon Slime จอมเขมือบจากอเวจี — Elden Ring Edition
    โหดขึ้น: Dash Charge, Combo 2-hit, Stagger Resistance, Enrage Phase 2
    """
    ENRAGE_HP_RATIO  = 0.35   # Enrage เมื่อ HP < 35%
    DASH_RANGE       = 400    # ระยะเริ่ม Dash Charge
    DASH_SPEED       = 16     # ความเร็ว Dash
    BASE_ATTACK_CD   = 100    # cooldown ปกติ
    ENRAGE_ATTACK_CD = 55     # cooldown ตอน Enrage

    def __init__(self, x, y):
        super().__init__(x, y, speed=2, hp=1000, name="Demon Slime")

        self._animations = {
            "idle":   self._load_frames("01_demon_idle",    "demon_idle",    6),
            "walk":   self._load_frames("02_demon_walk",    "demon_walk",    12),
            "attack": self._load_frames("03_demon_cleave",  "demon_cleave",  15),
            "hurt":   self._load_frames("04_demon_take_hit","demon_take_hit",5),
            "dead":   self._load_frames("05_demon_death",   "demon_death",   22),
        }

        self._action        = "idle"
        self._current_frame = 0
        self._animation_timer = 0
        self._attack_cooldown = 0

        self._rect = pygame.Rect(x, y, 140, 100)
        self._detect_range  = 600
        self._attack_range  = 180
        self._facing_right  = False
        self._damage        = 30

        # ── Elden Ring systems ──────────────────────────────────────────────
        self._is_berserk    = False   # Phase 2 (Enrage)
        self._enrage_flash  = 0       # transition flash timer

        # Dash Charge state
        self._is_dashing    = False
        self._dash_vx       = 0
        self._dash_timer    = 0

        # Combo state
        self._combo_pending = False
        self._combo_timer   = 0

        self._player_ref    = None

        try:
            if os.path.exists("assets/sound/mino1.wav"):
                self._roar_sound = pygame.mixer.Sound("assets/sound/mino1.wav")
                self._roar_sound.set_volume(0.7)
            else: self._roar_sound = None
        except: self._roar_sound = None

        try:
            import os as _os
            if _os.path.exists("assets/sound/1.mp3"):
                self._spawn_sound = pygame.mixer.Sound("assets/sound/1.mp3")
                self._spawn_sound.set_volume(0.8)
                self._spawn_sound.play()
        except: pass

        try:
            if os.path.exists("assets/sound/2.mp3"):
                self._death_sound = pygame.mixer.Sound("assets/sound/2.mp3")
                self._death_sound.set_volume(0.8)
            else: self._death_sound = None
        except: self._death_sound = None

    @property
    def action(self): return self._action
    @property
    def frame_index(self): return self._current_frame

    def _load_frames(self, folder, prefix, count):
        frames = []
        base  = f"assets/boss/boss_demon_slime_FREE_v1.0/individual sprites/{folder}/{prefix}_"
        for i in range(1, count + 1):
            try:
                img = pygame.image.load(f"{base}{i}.png").convert_alpha()
                frames.append(img)
            except:
                print(f"Error loading: {base}{i}.png")
        return frames

    # ─── Damage / Stagger Resistance ─────────────────────────────────────
    def take_damage(self, amount):
        if self._current_hp <= 0:
            return
        # Hyper Armor ขณะโจมตีหรือ Dash — โดนดาเมจแต่ไม่สะดุด
        if self._action == "attack" or self._is_dashing:
            self._current_hp -= amount
            if self._current_hp <= 0:
                self._current_hp = 0
                self._action = "dead"
                self._current_frame = 0
                self._is_dashing = False
                if hasattr(self, '_death_sound') and self._death_sound:
                    self._death_sound.play()
            self._hit_flash_timer = 6
            self._animation_timer = 0
            return
        # ถูกสะดุดปกติ
        self._current_hp -= amount
        if self._current_hp <= 0:
            self._current_hp = 0
            self._action = "dead"
            self._current_frame = 0
            if hasattr(self, '_death_sound') and self._death_sound:
                self._death_sound.play()
        else:
            self._action = "hurt"
            self._current_frame = 0
        self._animation_timer = 0
        self._hit_flash_timer = 12

    def attack(self, target):
        if self._attack_cooldown == 0 and self._is_alive and self._action not in ("dead", "hurt"):
            self._action        = "attack"
            self._current_frame = 0
            self._animation_timer = 0
            if hasattr(self, '_roar_sound') and self._roar_sound:
                self._roar_sound.play()

    def update(self, game_areas, player=None, shockwave_list=None):
        if not self._is_alive: return

        self._shockwave_list = shockwave_list

        # ── Enrage Phase 2 ─────────────────────────────────────────────────
        if not self._is_berserk and self._current_hp < self._max_hp * self.ENRAGE_HP_RATIO:
            self._is_berserk   = True
            self._enrage_flash = 50             # flash แดง 50 frame
            self._speed       *= 1.6
            self._damage      += 20
            if hasattr(self, '_roar_sound') and self._roar_sound:
                self._roar_sound.play()
            if self._action not in ("dead", "hurt"):
                self._action        = "idle"    # roar moment
                self._current_frame = 0

        if self._enrage_flash > 0:
            self._enrage_flash -= 1

        if self._hit_flash_timer > 0:
            self._hit_flash_timer -= 1

        # HP smooth
        if self._display_hp > self._current_hp:
            self._display_hp -= (self._display_hp - self._current_hp) * 0.05
        elif self._display_hp < self._current_hp:
            self._display_hp += (self._current_hp - self._display_hp) * 0.05

        # Stun system
        if self._stun_timer > 0:
            self._stun_timer -= 1
            self._is_stunned  = True
            if self._stun_timer <= 0:
                self._is_stunned = False
                self._action = "idle" if self._current_hp > 0 else "dead"

        if self._is_stunned:
            pass
        else:
            if self._action != "dead":
                self._handle_ai(player, game_areas)

        # ── Dash Charge movement ──────────────────────────────────────────
        if self._is_dashing:
            self._rect.x   += self._dash_vx
            self._dash_timer -= 1
            if self._dash_timer <= 0:
                self._is_dashing = False
                self._dash_vx    = 0
                if self._action != "dead":
                    self._action        = "attack"
                    self._current_frame = 0
                    self._animation_timer = 0

        # Gravity
        self._velocity_y += 0.5
        self._rect.y     += self._velocity_y
        for area in game_areas:
            if area.is_walkable() and self._rect.colliderect(area.rect):
                if self._velocity_y > 0 and self._rect.bottom <= area.rect.bottom:
                    self._rect.bottom = area.rect.top
                    self._velocity_y  = 0

        # ── Combo timer ──────────────────────────────────────────────────
        if self._combo_pending:
            self._combo_timer -= 1
            if self._combo_timer <= 0:
                self._combo_pending = False
                p = self._player_ref
                if p is not None and getattr(p, 'is_alive', False) and self._action != "dead":
                    dist = abs(p.rect.centerx - self._rect.centerx)
                    if dist <= self._attack_range + 60:
                        self._action        = "attack"
                        self._current_frame = 0
                        self._animation_timer = 0
                        self._attack_cooldown = self.BASE_ATTACK_CD

        # ── Animation ────────────────────────────────────────────────────
        frames = self._animations.get(self._action, self._animations["idle"])
        if not frames: return

        self._animation_timer += 1
        anim_speed = {"attack": 4, "hurt": 7, "dead": 5}.get(self._action, 6)
        if self._is_berserk and self._action == "walk":
            anim_speed = 4  # วิ่งไวขึ้นตอน Enrage

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
                # ดาเมจที่เฟรม 12
                if self._current_frame == 12:
                    p = self._player_ref
                    if p is not None and getattr(p, 'is_alive', False):
                        dist = abs(p.rect.centerx - self._rect.centerx)
                        if dist <= self._attack_range + 20:
                            if p.take_damage(self._damage,
                                             shockwave_list=getattr(self, '_shockwave_list', None)):
                                self.stun(120)
                if self._current_frame >= len(frames):
                    self._current_frame = 0
                    self._action = "idle" if self._current_hp > 0 else "dead"
                    cd = self.ENRAGE_ATTACK_CD if self._is_berserk else self.BASE_ATTACK_CD
                    self._attack_cooldown = cd
                    # ตั้ง Combo สำหรับ Phase 2
                    if self._is_berserk and not self._combo_pending:
                        self._combo_pending = True
                        self._combo_timer   = 30
            else:
                self._current_frame += 1
                if self._current_frame >= len(frames):
                    self._current_frame = 0

    def _handle_ai(self, player, game_areas):
        if not (player and getattr(player, 'is_alive', True)):
            if self._action not in ("attack", "hurt", "dead"):
                self._action = "idle"
            return

        distance        = player.rect.centerx - self._rect.centerx
        self._facing_right = distance > 0
        abs_dist        = abs(distance)
        self._player_ref = player

        if self._attack_cooldown > 0:
            self._attack_cooldown -= 1

        # ขณะ Dash ไม่ต้อง AI อื่น
        if self._is_dashing: return

        if self._action not in ("hurt", "attack", "dead"):
            move_dir = 0

            if self._attack_cooldown == 0:
                # Dash Charge ถ้าระยะกลาง
                if self._attack_range < abs_dist <= self.DASH_RANGE:
                    self._is_dashing  = True
                    self._dash_vx     = self.DASH_SPEED if self._facing_right else -self.DASH_SPEED
                    self._dash_timer  = 12
                    self._action      = "walk"
                    self._attack_cooldown = self.BASE_ATTACK_CD
                    return

                # Melee
                if abs_dist <= self._attack_range:
                    self.attack(player)
                    self._attack_cooldown = self.ENRAGE_ATTACK_CD if self._is_berserk else self.BASE_ATTACK_CD
                    return

            # เดิน / ไล่
            if self._is_berserk:
                if abs_dist > self._attack_range:
                    move_dir = 1 if self._facing_right else -1
            else:
                if abs_dist <= self._attack_range:
                    if self._attack_cooldown > 0 and abs_dist < 100:
                        move_dir = -1 if self._facing_right else 1
                elif abs_dist <= self._detect_range:
                    move_dir = 1 if self._facing_right else -1

            if move_dir != 0:
                new_x   = self._rect.x + (move_dir * self._speed)
                check_x = new_x + (self._rect.width if move_dir > 0 else 0)
                check_r = pygame.Rect(check_x, self._rect.bottom + 5, 2, 2)
                has_ground = any(a.is_walkable() and a.rect.colliderect(check_r) for a in game_areas)
                if has_ground:
                    self._rect.x = new_x
                    self._action = "walk"
                elif self._action not in ("attack", "dead"):
                    self._action = "idle"
            elif self._action not in ("attack", "dead"):
                self._action = "idle"

    def draw(self, screen):
        if not self._is_alive or self._action not in self._animations:
            return
        frames = self._animations[self._action]
        if not frames: return

        current_idx  = min(self._current_frame, len(frames) - 1)
        frame_image  = frames[current_idx]

        scale = 1.8
        if self._is_berserk: scale = 2.0
        w, h = frame_image.get_size()
        frame_image = pygame.transform.scale(frame_image, (int(w * scale), int(h * scale)))

        # Dash trail (เงาม่วง)
        if self._is_dashing:
            ghost = frame_image.copy()
            ghost.set_alpha(70)
            gr = ghost.get_rect()
            gr.midbottom = (self._rect.centerx - self._dash_vx * 3,
                            self._rect.midbottom[1] + 10)
            screen.blit(ghost, gr)

        # Hit flash ขาว
        if self._hit_flash_timer > 0:
            flash = frame_image.copy()
            flash.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
            flash.set_alpha(150)
            frame_image.blit(flash, (0, 0))

        # Enrage tint แดง
        if self._is_berserk:
            alpha = min(160, 80 + self._enrage_flash * 2)
            tint = frame_image.copy()
            tint.fill((160, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            tint.set_alpha(alpha)
            frame_image.blit(tint, (0, 0))

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

        bar_width  = 500
        bar_height = 25
        x = (800 - bar_width) // 2
        y = 50

        hp_ratio         = self._boss.current_hp / self._boss.max_hp
        display_hp_ratio = getattr(self._boss, '_display_hp', self._boss.current_hp) / self._boss.max_hp

        # พื้นหลัง
        pygame.draw.rect(screen, (30, 30, 30), (x, y, bar_width, bar_height))
        # หลอด "เลือดลด" (trailing)
        pygame.draw.rect(screen, (200, 50, 50), (x, y, int(bar_width * display_hp_ratio), bar_height))
        # หลอดเลือดจริง
        bar_color = (150, 0, 200) if not getattr(self._boss, '_is_berserk', False) else (220, 30, 30)
        pygame.draw.rect(screen, bar_color, (x, y, int(bar_width * hp_ratio), bar_height))
        # กรอบสีทอง
        pygame.draw.rect(screen, (255, 215, 0), (x, y, bar_width, bar_height), 2)

        # ชื่อ Boss เหนือหลอดเลือด
        name_surface = self._font.render(self._boss.name, True, (255, 255, 255))
        screen.blit(name_surface, (x + (bar_width - name_surface.get_width()) // 2, y - 35))

        # แสดง "ENRAGED" ตอน Phase 2
        if getattr(self._boss, '_is_berserk', False):
            try:
                fnt = pygame.font.SysFont("Arial", 14, bold=True)
                lbl = fnt.render("⚠ ENRAGED ⚠", True, (255, 80, 0))
                screen.blit(lbl, (x + (bar_width - lbl.get_width()) // 2, y + bar_height + 4))
            except Exception:
                pass

