import pygame
import random
import time
import math

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size=24):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("Arial", size, bold=True)
        self.velocity_y = -2
        self.alpha = 255
        self.alive = True
        self.creation_time = time.time()
        self.lifetime = 1.0 # 1 second

    def update(self):
        self.y += self.velocity_y
        elapsed = time.time() - self.creation_time
        if elapsed > self.lifetime:
            self.alive = False
        else:
            # Fade out
            self.alpha = int(255 * (1 - (elapsed / self.lifetime)))

    def draw(self, screen):
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        screen.blit(text_surf, (self.x, self.y))

class Particle:
    def __init__(self, x, y, color=(0, 200, 255)):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2, 0)
        self.radius = random.randint(2, 5)
        self.lifetime = random.uniform(0.5, 1.0)
        self.creation_time = time.time()
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius -= 0.1
        elapsed = time.time() - self.creation_time
        if elapsed > self.lifetime or self.radius <= 0:
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

class ImpactParticle:
    """อนุภาคแรงปะทะ (เลือด หรือ ประกายไฟ)"""
    def __init__(self, x, y, color=(255, 0, 0), size=None):
        self.x = x
        self.y = y
        self.color = color
        self.size = size or random.randint(3, 5)
        # กระจายรอบทิศทางด้วยความเร็วสูง
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.25
        self.friction = 0.96
        self.lifetime = 1.0 # 1 วินาที
        self.start_time = time.time()
        self.alive = True

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity # แรงโน้มถ่วง
        self.vx *= self.friction
        self.vy *= self.friction
        
        elapsed = time.time() - self.start_time
        if elapsed > self.lifetime:
            self.alive = False

    def draw(self, screen):
        elapsed = time.time() - self.start_time
        alpha = int(255 * (1 - (elapsed / self.lifetime)))
        if alpha < 0: alpha = 0
        
        # วาดสี่เหลี่ยมตามทิศทางความเร็ว (Motion Blur)
        if abs(self.vx) + abs(self.vy) > 0.1:
            end_x = self.x - self.vx * 1.5
            end_y = self.y - self.vy * 1.5
            pygame.draw.line(screen, (*self.color, alpha), (int(self.x), int(self.y)), (int(end_x), int(end_y)), int(self.size))
        else:
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            screen.blit(s, (int(self.x), int(self.y)))

class AmbientParticle:
    """อนุภาคบรรยากาศ เช่น ใบไม้ร่วง หรือละอองเวทมนตร์"""
    def __init__(self, x, y, p_type="leaf", color=None):
        self.x = x
        self.y = y
        self.p_type = p_type
        self.alive = True
        self.start_time = time.time()
        self.lifetime = random.uniform(4.0, 8.0)
        
        if p_type == "leaf":
            self.color = color or (random.randint(100, 200), random.randint(150, 255), 50)
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(1.0, 2.5)
            self.size = random.randint(3, 6)
            self.oscillation_speed = random.uniform(2.0, 4.0)
            self.oscillation_amp = random.uniform(10, 30)
        elif p_type == "magic":
            self.color = color or (150, 50, 255)
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(-0.5, -1.2)
            self.size = random.randint(2, 4)
            self.oscillation_speed = random.uniform(1.0, 2.0)
            self.oscillation_amp = random.uniform(5, 15)
        elif p_type == "glow_orb":
            self.color = color or (200, 240, 255) # สีฟ้าอ่อนใสๆ
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = random.uniform(-0.1, -0.4)
            self.size = random.randint(2, 4)
            self.oscillation_speed = random.uniform(0.5, 1.2)
            self.oscillation_amp = random.uniform(5, 10)
        else: # sparkle
            self.color = color or (255, 215, 0)
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = random.uniform(-0.2, -0.5)
            self.size = random.randint(1, 3)

    def update(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.lifetime:
            self.alive = False
            return

        if self.p_type == "leaf":
            # ใบไม้ร่วงแบบแกว่งไปมา (Fluttering)
            self.y += self.vy
            offset_x = math.sin(elapsed * self.oscillation_speed) * self.oscillation_amp
            self.actual_x = self.x + offset_x
        elif self.p_type == "magic" or self.p_type == "glow_orb":
            # ละอองมนต์/ลูกไฟวิญญาณ ลอยขึ้นช้าๆ
            self.y += self.vy
            self.x += self.vx + math.sin(elapsed * self.oscillation_speed) * 0.3
            self.actual_x = self.x
        else:
            self.x += self.vx
            self.y += self.vy
            self.actual_x = self.x

    def draw(self, screen):
        elapsed = time.time() - self.start_time
        alpha = int(255 * (1 - (elapsed / self.lifetime)))
        if alpha < 0: alpha = 0
        
        # วาดเงา/แสงเรือง
        if self.p_type in ["magic", "sparkle", "glow_orb"]:
            glow_multiplier = 4 if self.p_type == "glow_orb" else 3
            glow_size = self.size * glow_multiplier
            glow_surf = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha // 4), (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (int(self.actual_x - glow_size), int(self.y - glow_size)))

        # วาดแกนกลาง
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        if self.p_type == "leaf":
            # วาดรูปใบไม้สี่เหลี่ยมข้าวหลามตัดเอียงๆ
            points = [(self.size, 0), (self.size*2, self.size), (self.size, self.size*2), (0, self.size)]
            pygame.draw.polygon(s, (*self.color, alpha), points)
        else:
            pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        
        screen.blit(s, (int(self.actual_x - self.size), int(self.y - self.size)))

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.start_time = 0

    def trigger(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.start_time = time.time()

    def get_offset(self):
        if time.time() - self.start_time < self.duration:
            offset_x = random.randint(-self.intensity, self.intensity)
            offset_y = random.randint(-self.intensity, self.intensity)
            return offset_x, offset_y
        return 0, 0
class SlashFX:
    """เอฟเฟกต์วิถีดาบ (Sword Slash Arc)"""
    def __init__(self, x, y, facing_right, color=(200, 240, 255)):
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.color = color
        self.alive = True
        self.start_time = time.time()
        self.lifetime = 0.25 # แสดงผลสั้นๆ 0.25 วินาที
        self.alpha = 255

    def update(self, player_pos=None):
        if player_pos:
            self.x, self.y = player_pos
            
        elapsed = time.time() - self.start_time
        if elapsed > self.lifetime:
            self.alive = False
        else:
            # ค่อยๆ จางหายไป
            self.alpha = int(255 * (1 - (elapsed / self.lifetime)))

    def draw(self, screen):
        # สร้าง Surface สำหรับวาดดาบที่มี Alpha
        surf_size = 140
        s = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        
        # วาดเส้นโค้งวิถีดาบ (Arc/Polygon)
        rect = pygame.Rect(10, 10, 120, 120)
        
        # กำหนดมุมตามทิศทาง
        if self.facing_right:
            start_angle = -math.pi / 2.5
            end_angle = math.pi / 2.5
        else:
            start_angle = math.pi - math.pi / 2.5
            end_angle = math.pi + math.pi / 2.5
            
        # วาดหลายเส้นทับกันให้ดูหนาและนุ่มนวล
        for i in range(5):
            a = max(0, self.alpha - (i * 40))
            pygame.draw.arc(s, (*self.color, a), rect.inflate(-i*2, -i*2), start_angle, end_angle, 8 - i)

        # วาดหัวดาบให้ดูแหลมคม
        # tip_x = 60 + math.cos(end_angle) * 55
        # tip_y = 60 - math.sin(end_angle) * 55
        
        screen.blit(s, (self.x - surf_size//2, self.y - surf_size//2))

class ShockwaveFX:
    """คลื่นกระแทกวงกลม (Shockwave)"""
    def __init__(self, x, y, color=(255, 255, 255), max_radius=150):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.max_radius = max_radius
        self.alive = True
        self.alpha = 200
        self.thickness = 5

    def update(self):
        # ขยายวงกลมออกไปเรื่อยๆ
        self.radius += 10
        # ค่อยๆ จางหายไป
        self.alpha -= 12
        if self.radius >= self.max_radius or self.alpha <= 0:
            self.alive = False

    def draw(self, screen):
        # สร้าง Surface พิเศษสำหรับวาดวงกลมที่มี Alpha
        s = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        # วาดวงกลม (ขอบ)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.max_radius, self.max_radius), self.radius, self.thickness)
        # วาดแสงฟุ้งๆ รอบๆ วงกลมหลัก
        if self.alpha > 50:
             pygame.draw.circle(s, (*self.color, self.alpha // 2), (self.max_radius, self.max_radius), self.radius + 5, self.thickness + 2)
        
        screen.blit(s, (int(self.x - self.max_radius), int(self.y - self.max_radius)))

class DustParticle:
    """ธุลีดิน (Dust) เมื่อกระโดด/ลงพื้น"""
    def __init__(self, x, y, color=(200, 200, 200)):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, -0.2) # ลอยขึ้นนิดนึง
        self.radius = random.randint(4, 7)
        self.alpha = 150
        self.alive = True
        self.lifetime = 0.5
        self.start_time = time.time()

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.radius += 0.1 # ขยายออกนิดๆ
        
        elapsed = time.time() - self.start_time
        if elapsed > self.lifetime:
            self.alive = False
        else:
            self.alpha = int(150 * (1 - (elapsed / self.lifetime)))

    def draw(self, screen):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))
