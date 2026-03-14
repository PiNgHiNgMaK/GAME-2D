import pygame
import math
import random
import time
import os
from abc import ABC, abstractmethod

# =====================================================================
# 1. ABSTRACTION
# =====================================================================
class IPuzzleElement(ABC):
    @abstractmethod
    def update(self, player): pass
    @abstractmethod
    def draw(self, screen): pass

# =====================================================================
# 2. ENCAPSULATION: Projectile Logic
# =====================================================================
class VoidOrb:
    def __init__(self, x, y, target_pos):
        self._pos = pygame.Vector2(x, y)
        direction = pygame.Vector2(target_pos) - self._pos
        if direction.length() > 0:
            self._velocity = direction.normalize() * 5
        else:
            self._velocity = pygame.Vector2(5, 0)
        
        self._radius = 12
        self._is_reflected = False
        self._is_active = True
        self._color = (150, 0, 255) # สีม่วงเข้ม

    @property
    def is_active(self): return self._is_active
    @property
    def is_reflected(self): return self._is_reflected
    @property
    def pos(self): return self._pos

    def reflect(self, target_pos):
        self._is_reflected = True
        direction = pygame.Vector2(target_pos) - self._pos
        if direction.length() > 0:
            self._velocity = direction.normalize() * 12 # พุ่งไวและแรงขึ้น!
        self._color = (0, 255, 255) # เปลี่ยนเป็นสีฟ้าเท่ๆ

    def update(self):
        self._pos += self._velocity
        # ออกนอกจอให้หายไป
        if self._pos.x < -200 or self._pos.x > 1000 or self._pos.y < -200 or self._pos.y > 700:
            self._is_active = False

    def draw(self, screen):
        # วาดแสงเรืองแสง (Glow)
        glow_size = self._radius * 2 + (math.sin(time.time() * 15) * 6)
        s = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
        # ถ้าสะท้อนแล้วให้มีแสงหางทาง (Trail)
        pygame.draw.circle(s, (*self._color, 80), (int(glow_size), int(glow_size)), int(glow_size))
        screen.blit(s, (int(self._pos.x - glow_size), int(self._pos.y - glow_size)))
        
        # แกนกลาง
        pygame.draw.circle(screen, (255, 255, 255), (int(self._pos.x), int(self._pos.y)), self._radius // 2)

# =====================================================================
# 3. INHERITANCE: Target Crystals
# =====================================================================
class FloatingCrystal(IPuzzleElement):
    def __init__(self, x, y):
        self._pos = pygame.Vector2(x, y)
        self._is_broken = False
        self._rect = pygame.Rect(x - 30, y - 40, 60, 80) # ขยาย hitbox ให้ใหญ่ขึ้นเล็กน้อย
        self._hover_offset = random.random() * math.pi * 2

    @property
    def is_broken(self): return self._is_broken
    @property
    def pos(self): return self._pos

    def break_crystal(self):
        self._is_broken = True

    def update(self, player):
        pass # ขยับลอยนิ่งๆ ใน draw

    def draw(self, screen):
        if self._is_broken: return
        
        # ลอยขึ้นลง (Hover animation)
        y_offset = math.sin(time.time() * 3 + self._hover_offset) * 15
        draw_rect = self._rect.move(0, y_offset)
        
        # วาดผลึกทรงหยดน้ำ/สี่เหลี่ยมข้าวหลามตัด
        points = [
            (draw_rect.midtop),
            (draw_rect.midright),
            (draw_rect.midbottom),
            (draw_rect.midleft)
        ]
        pygame.draw.polygon(screen, (0, 200, 255), points)
        pygame.draw.polygon(screen, (255, 255, 255), points, 2)
        
        # ออร่า
        s = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 100, 255, 70), (60, 60), 45 + int(y_offset//2))
        screen.blit(s, (draw_rect.centerx - 60, draw_rect.centery - 60))

# =====================================================================
# 4. POLYMORPHISM: The Deflector Manager
# =====================================================================
class DeflectorPuzzleManager:
    def __init__(self):
        self._eye_pos = pygame.Vector2(400, 120)
        self._orbs = []
        self._crystals = [
            FloatingCrystal(150, 120),
            FloatingCrystal(650, 120),
            FloatingCrystal(400, 300)
        ]
        self._spawn_timer = 0
        self._is_cleared = False
        self._message = "PARRY THE ORBS TO DESTROY CRYSTALS!"

    @property
    def is_cleared(self): return self._is_cleared

    def update(self, player, game_areas):
        if self._is_cleared: return

        # 1. จัดการการยิงลูกพลัง
        if time.time() > self._spawn_timer:
            # ยิงตรงไปหา Player
            new_orb = VoidOrb(self._eye_pos.x, self._eye_pos.y, player.rect.center)
            self._orbs.append(new_orb)
            self._spawn_timer = time.time() + 1.5 # ยิงเร็วขึ้นนิดนึง

        # 2. อัปเดตลูกพลังและการสะท้อน
        for orb in self._orbs[:]:
            orb.update()
            
            # การชนกับ Player (ขยายระยะให้ปัดง่ายขึ้น)
            dist_to_player = orb.pos.distance_to(pygame.Vector2(player.rect.center))
            if dist_to_player < 70 and not orb.is_reflected:
                # ถ้าผู้เล่นโจมตีถูกจังหวะ (ปัดออก)
                if player.is_attacking:
                    # หาผลึกที่ใกล้ที่สุดที่ยังไม่แตกเพื่อเป็นเป้าหมายสะท้อน
                    active_crystals = [c for c in self._crystals if not c.is_broken]
                    if active_crystals:
                        # เลือกผลึกที่ใกล้ลูกพลังที่สุด
                        target_crystal = min(active_crystals, key=lambda c: orb.pos.distance_to(c.pos))
                        orb.reflect(target_crystal.pos)
                else:
                    # ถ้าปัดไม่ทัน โดนดาเมจ
                    if dist_to_player < 40:
                        player.take_damage(20)
                        orb._is_active = False

            # การชนระหว่างลูกที่สะท้อนแล้วกับผลึก (ใช้ Rect เช็คจะแม่นกว่า)
            if orb.is_reflected:
                for crystal in self._crystals:
                    if not crystal.is_broken and crystal._rect.collidepoint(orb.pos):
                        crystal.break_crystal()
                        # เล่นเสียงเมื่อผลึกแตกแต่ละอัน (ใช้เสียงที่ยูสเซอร์เลือกมาใหม่)
                        try:
                            s_path = "assets/sound/universfield-glass-bottle-breaking-351297.mp3"
                            if not os.path.exists(s_path):
                                s_path = "assets/sound/1.mp3"
                                
                            if os.path.exists(s_path):
                                s = pygame.mixer.Sound(s_path)
                                s.set_volume(0.5)
                                s.play()
                        except: pass
                        
                        orb._is_active = False
                        # เช็คว่าเคลียร์หมดหรือยัง
                        if all(c.is_broken for c in self._crystals):
                            self._is_cleared = True
                            self._message = "RITUAL COMPLETE - PORTAL OPENED!"

            if not orb.is_active:
                self._orbs.remove(orb)

    def draw(self, screen):
        # วาด "ดวงตาผู้คุมวิญญาณ"
        eye_color = (100, 0, 200)
        pygame.draw.circle(screen, (20, 0, 40), self._eye_pos, 45)
        pygame.draw.circle(screen, eye_color, self._eye_pos, 35)
        # รูม่านตาสีแดงเรืองแสง
        pupil_x = self._eye_pos.x + math.sin(time.time()*2)*10
        pygame.draw.circle(screen, (255, 0, 50), (int(pupil_x), int(self._eye_pos.y)), 15)
        
        # วาดผลึก
        for crystal in self._crystals:
            crystal.draw(screen)
            
        # วาดลูกพลัง
        for orb in self._orbs:
            orb.draw(screen)

        # UI
        font = pygame.font.SysFont("Arial", 22, bold=True)
        color = (255, 255, 255) if not self._is_cleared else (0, 255, 150)
        txt = font.render(self._message, True, color)
        
        bg_rect = pygame.Rect(400 - txt.get_width()//2 - 10, 440, txt.get_width() + 20, 40)
        s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        screen.blit(s, bg_rect.topleft)
        screen.blit(txt, (400 - txt.get_width()//2, 448))
