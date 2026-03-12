import pygame
import random
import time

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
