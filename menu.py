import pygame
import os

try:
    pygame.mixer.init()
    if os.path.exists("assets/sound/Menu Selection Click.wav"):
        CLICK_SOUND = pygame.mixer.Sound("assets/sound/Menu Selection Click.wav")
    else:
        CLICK_SOUND = None
except:
    CLICK_SOUND = None

def play_click_sound():
    if CLICK_SOUND:
        CLICK_SOUND.play()
        
# =====================================================================
# คลาสสำหรับจัดการเมนูหลัก (Single Responsibility Principle)
# =====================================================================
class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 36)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
        
        self.name_text = ""
        self.input_rect = pygame.Rect(width//2 - 150, height//2 - 40, 300, 50)
        self.is_input_active = False # เช็คว่าเรากำลังพิมพ์ช่องนี้อยู่หรือไม่
        
        self.play_btn_rect = pygame.Rect(width//2 - 100, height//2 + 50, 200, 50)
        self.settings_btn_rect = pygame.Rect(width//2 - 100, height//2 + 120, 200, 50)
        self.quit_btn_rect = pygame.Rect(width//2 - 100, height//2 + 190, 200, 50)
        
        self.bg_color = (30, 30, 30)

    def handle_event(self, event):
        """จัดการการกรอกข้อมูลและคลิกเมาส์ในหน้าเมนู"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # ตรวจสอบการคลิกที่กล่องรับชื่อ
            if self.input_rect.collidepoint(event.pos):
                self.is_input_active = True
            else:
                self.is_input_active = False

            # ตรวจสอบการคลิกปุ่ม Play 
            if self.play_btn_rect.collidepoint(event.pos) and self.name_text.strip() != "":
                play_click_sound()
                return "play", self.name_text.strip()
                
            # ตรวจสอบการคลิกปุ่ม Settings
            if self.settings_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "settings", None

            # ตรวจสอบการคลิกปุ่ม Quit
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "quit", None

        # รองรับการพิมพ์ชื่อเมื่อกล่องรับชื่อแอคทีฟขึ้นมา
        if event.type == pygame.KEYDOWN and self.is_input_active:
            if event.key == pygame.K_BACKSPACE:
                self.name_text = self.name_text[:-1] # ลากตัวอักษรสุดท้ายทิ้ง
            elif len(self.name_text) < 15 and event.unicode.isprintable():
                self.name_text += event.unicode # เติมข้อความลงไป
                
        return None, None

    def draw(self, screen):
        """วาดองค์ประกอบของหน้าเมนู"""
        screen.fill(self.bg_color)
        
        # ชื่อเกม
        title_surf = self.large_font.render("Jao Ting nong", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(self.width//2, 100))
        screen.blit(title_surf, title_rect)
        
        # ข้อความให้กรอกชื่อ
        label_surf = self.font.render("Enter Name:", True, (255, 255, 255))
        screen.blit(label_surf, (self.input_rect.x, self.input_rect.y - 40))
        
        # กล่องสำหรับรับชื่อและข้อความที่พิมพ์
        color = (255, 255, 255) if self.is_input_active else (150, 150, 150)
        pygame.draw.rect(screen, color, self.input_rect, 2)
        text_surf = self.font.render(self.name_text, True, (255, 255, 255))
        screen.blit(text_surf, (self.input_rect.x + 10, self.input_rect.y + 5))
        
        # คำเตือนถ้าหากยังไม่ได้ใส่ชื่อ
        if self.name_text.strip() == "":
            warn_surf = pygame.font.SysFont("Arial", 20).render("* Please enter name to play", True, (255, 100, 100))
            screen.blit(warn_surf, (self.input_rect.x, self.input_rect.y + 55))
        
        # ปุ่ม Play ตัวหนังสือและกรอบ
        play_color = (0, 200, 0) if self.name_text.strip() != "" else (100, 100, 100)
        pygame.draw.rect(screen, play_color, self.play_btn_rect, border_radius=10)
        play_surf = self.font.render("PLAY", True, (255, 255, 255))
        screen.blit(play_surf, play_surf.get_rect(center=self.play_btn_rect.center))
        
        # ปุ่ม Settings ตัวหนังสือและกรอบ
        pygame.draw.rect(screen, (50, 50, 200), self.settings_btn_rect, border_radius=10)
        settings_surf = self.font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(settings_surf, settings_surf.get_rect(center=self.settings_btn_rect.center))
        
        # ปุ่ม Quit ตัวหนังสือและกรอบ
        pygame.draw.rect(screen, (200, 50, 50), self.quit_btn_rect, border_radius=10)
        quit_surf = self.font.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_surf, quit_surf.get_rect(center=self.quit_btn_rect.center))

# =====================================================================
# เมนูตั้งค่า (Settings)
# =====================================================================
class SettingsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 36)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.back_btn_rect = pygame.Rect(width//2 - 100, height - 100, 200, 50)
        
        # ตั้งค่าเริ่มต้น
        self.fps = 60
        self.sound_on = True
        
        # ตำแหน่งปุ่มปรับ FPS
        self.fps30_btn_rect = pygame.Rect(width//2 + 20, 200, 80, 40)
        self.fps60_btn_rect = pygame.Rect(width//2 + 120, 200, 80, 40)
        
        # ตำแหน่งปุ่มปรับเปิด-ปิดเสียง
        self.sound_on_btn_rect = pygame.Rect(width//2 + 20, 280, 80, 40)
        self.sound_off_btn_rect = pygame.Rect(width//2 + 120, 280, 80, 40)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "back"
            if self.fps30_btn_rect.collidepoint(event.pos):
                play_click_sound()
                self.fps = 30
            if self.fps60_btn_rect.collidepoint(event.pos):
                play_click_sound()
                self.fps = 60
            if self.sound_on_btn_rect.collidepoint(event.pos):
                play_click_sound()
                self.sound_on = True
            if self.sound_off_btn_rect.collidepoint(event.pos):
                play_click_sound()
                self.sound_on = False
        return None
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        
        title_surf = self.large_font.render("SETTINGS", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(self.width//2, 100))
        screen.blit(title_surf, title_rect)
        
        # แสดงเมนูการตั้งค่า FPS
        fps_label = self.font.render("FPS:", True, (255, 255, 255))
        screen.blit(fps_label, (self.width//2 - 140, 200))
        
        color_30 = (0, 200, 0) if self.fps == 30 else (100, 100, 100)
        pygame.draw.rect(screen, color_30, self.fps30_btn_rect, border_radius=5)
        fps30_surf = pygame.font.SysFont("Arial", 24).render("30", True, (255, 255, 255))
        screen.blit(fps30_surf, fps30_surf.get_rect(center=self.fps30_btn_rect.center))

        color_60 = (0, 200, 0) if self.fps == 60 else (100, 100, 100)
        pygame.draw.rect(screen, color_60, self.fps60_btn_rect, border_radius=5)
        fps60_surf = pygame.font.SysFont("Arial", 24).render("60", True, (255, 255, 255))
        screen.blit(fps60_surf, fps60_surf.get_rect(center=self.fps60_btn_rect.center))

        # แสดงเมนูตั้งค่าเสียง (Sound)
        sound_label = self.font.render("Sound:", True, (255, 255, 255))
        screen.blit(sound_label, (self.width//2 - 140, 280))
        
        color_on = (0, 200, 0) if self.sound_on else (100, 100, 100)
        pygame.draw.rect(screen, color_on, self.sound_on_btn_rect, border_radius=5)
        on_surf = pygame.font.SysFont("Arial", 24).render("ON", True, (255, 255, 255))
        screen.blit(on_surf, on_surf.get_rect(center=self.sound_on_btn_rect.center))

        color_off = (200, 0, 0) if not self.sound_on else (100, 100, 100)
        pygame.draw.rect(screen, color_off, self.sound_off_btn_rect, border_radius=5)
        off_surf = pygame.font.SysFont("Arial", 24).render("OFF", True, (255, 255, 255))
        screen.blit(off_surf, off_surf.get_rect(center=self.sound_off_btn_rect.center))
        
        # ปุ่ม Back
        pygame.draw.rect(screen, (200, 50, 50), self.back_btn_rect, border_radius=10)
        back_surf = self.font.render("BACK", True, (255, 255, 255))
        screen.blit(back_surf, back_surf.get_rect(center=self.back_btn_rect.center))

# =====================================================================
# เมนูหยุดเกมชั่วคราว (Pause Menu)
# =====================================================================
class PauseMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 36)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
        
        self.resume_btn_rect = pygame.Rect(width//2 - 100, height//2 - 20, 200, 50)
        self.settings_btn_rect = pygame.Rect(width//2 - 100, height//2 + 50, 200, 50)
        self.quit_btn_rect = pygame.Rect(width//2 - 100, height//2 + 120, 200, 50)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.resume_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "resume"
            if self.settings_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "settings"
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "quit"
        return None
        
    def draw(self, screen):
        # วาดพื้นหลังทำโปร่งแสงทับเกม
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title_surf = self.large_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width//2, 120))
        screen.blit(title_surf, title_rect)
        
        # ปุ่ม Resume
        pygame.draw.rect(screen, (0, 200, 0), self.resume_btn_rect, border_radius=10)
        resume_surf = self.font.render("RESUME", True, (255, 255, 255))
        screen.blit(resume_surf, resume_surf.get_rect(center=self.resume_btn_rect.center))
        
        # ปุ่ม Settings
        pygame.draw.rect(screen, (50, 50, 200), self.settings_btn_rect, border_radius=10)
        settings_surf = self.font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(settings_surf, settings_surf.get_rect(center=self.settings_btn_rect.center))
        
        # ปุ่ม Quit
        pygame.draw.rect(screen, (200, 50, 50), self.quit_btn_rect, border_radius=10)
        quit_surf = self.font.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_surf, quit_surf.get_rect(center=self.quit_btn_rect.center))

# =====================================================================
# เมนูจบเกม (Game Over / Victory Menu)
# =====================================================================
class GameOverMenu:
    def __init__(self, width, height, title="Game Over", color=(255, 0, 0)):
        self.width = width
        self.height = height
        self.title = title
        self.color = color
        
        self.font = pygame.font.SysFont("Arial", 36)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
        
        self.play_again_btn_rect = pygame.Rect(width//2 - 125, height//2, 250, 50)
        self.quit_btn_rect = pygame.Rect(width//2 - 125, height//2 + 70, 250, 50)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_again_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "play_again"
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "quit"
        return None

    def draw(self, screen):
        # วาดพื้นหลังทำโปร่งแสงทับเกม
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        title_surf = self.large_font.render(self.title, True, self.color)
        title_rect = title_surf.get_rect(center=(self.width//2, self.height//2 - 80))
        screen.blit(title_surf, title_rect)
        
        # ปุ่ม Play Again
        pygame.draw.rect(screen, (0, 200, 0), self.play_again_btn_rect, border_radius=10)
        play_again_surf = self.font.render("PLAY AGAIN", True, (255, 255, 255))
        screen.blit(play_again_surf, play_again_surf.get_rect(center=self.play_again_btn_rect.center))
        
        # ปุ่ม Quit
        pygame.draw.rect(screen, (200, 50, 50), self.quit_btn_rect, border_radius=10)
        quit_surf = self.font.render("QUIT", True, (255, 255, 255))
        screen.blit(quit_surf, quit_surf.get_rect(center=self.quit_btn_rect.center))
