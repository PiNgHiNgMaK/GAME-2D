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
        # ลองใช้ฟอนต์ที่ดูเป็นทางการขึ้น
        self.font = pygame.font.SysFont("Arial", 32)
        self.large_font = pygame.font.SysFont("Arial", 72, bold=True)
        self.title_font = pygame.font.SysFont("Georgia", 64, bold=True, italic=True)
        
        self.name_text = ""
        self.input_rect = pygame.Rect(width//2 - 150, height//2 - 20, 300, 50)
        self.is_input_active = False
        
        button_width = 250
        self.play_btn_rect = pygame.Rect(width//2 - button_width//2, height//2 + 60, button_width, 50)
        self.settings_btn_rect = pygame.Rect(width//2 - button_width//2, height//2 + 125, button_width, 50)
        self.quit_btn_rect = pygame.Rect(width//2 - button_width//2, height//2 + 190, button_width, 50)
        
        # โหลดภาพพื้นหลังหน้าจอหลัก (ตัวคลีนที่ไม่มีตัวหนังสือติดมา)
        try:
            bg_path = "background/game_menu_background_clean_1773374248931.png"
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (width, height))
            else:
                self.background = None
        except:
            self.background = None
            
        self.bg_color = (15, 15, 25)

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
        if self.background:
            screen.blit(self.background, (0, 0))
            # ใส่ Overlay มืดๆ จางๆ เพื่อให้ตัวหนังสืออ่านง่ายขึ้น
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
        else:
            screen.fill(self.bg_color)
        
        # ชื่อเกม (The Echo of the Abyss)
        title_surf = self.large_font.render("The Echo of the Abyss", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.width//2, 110))
        # Shadow
        shadow_surf = self.large_font.render("The Echo of the Abyss", True, (0, 0, 0))
        screen.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
        screen.blit(title_surf, title_rect)
        
        # Subtitle (Reversed Fate)
        sub_surf = self.font.render("--- Reversed Fate ---", True, (0, 200, 255))
        sub_rect = sub_surf.get_rect(center=(self.width//2, 160))
        screen.blit(sub_surf, sub_rect)
        
        # ส่วนชื่อผู้เล่น
        label_surf = self.font.render("Warrior's Name:", True, (200, 200, 210))
        screen.blit(label_surf, (self.input_rect.x, self.input_rect.y - 45))
        
        # กล่องสำหรับรับชื่อ
        box_color = (0, 200, 255) if self.is_input_active else (100, 100, 120)
        pygame.draw.rect(screen, (20, 20, 30), self.input_rect) # พื้นหลังกล่อง
        pygame.draw.rect(screen, box_color, self.input_rect, 2, border_radius=5)
        
        text_surf = self.font.render(self.name_text, True, (255, 255, 255))
        screen.blit(text_surf, (self.input_rect.x + 15, self.input_rect.y + 7))
        
        # คำเตือนถ้ายังไม่ใส่ชื่อ
        if self.name_text.strip() == "":
            warn_surf = pygame.font.SysFont("Arial", 18, italic=True).render("* Enter your name to start your destiny", True, (255, 120, 120))
            screen.blit(warn_surf, (self.input_rect.x, self.input_rect.y + 55))
        
        # วาดปุ่มต่างๆ
        mouse_pos = pygame.mouse.get_pos()
        
        # ปุ่ม PLAY
        is_hover_play = self.play_btn_rect.collidepoint(mouse_pos)
        play_base_color = (0, 180, 80) if self.name_text.strip() != "" else (80, 80, 80)
        if is_hover_play and self.name_text.strip() != "": play_base_color = (0, 230, 100)
        
        pygame.draw.rect(screen, play_base_color, self.play_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.play_btn_rect, 2, border_radius=10)
        play_surf = self.font.render("BEGIN JOURNEY", True, (255, 255, 255))
        screen.blit(play_surf, play_surf.get_rect(center=self.play_btn_rect.center))
        
        # ปุ่ม SETTINGS
        is_hover_set = self.settings_btn_rect.collidepoint(mouse_pos)
        set_color = (60, 60, 80) if not is_hover_set else (80, 80, 110)
        pygame.draw.rect(screen, set_color, self.settings_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.settings_btn_rect, 1, border_radius=10)
        set_surf = self.font.render("SETTINGS", True, (255, 255, 255))
        screen.blit(set_surf, set_surf.get_rect(center=self.settings_btn_rect.center))
        
        # ปุ่ม QUIT
        is_hover_quit = self.quit_btn_rect.collidepoint(mouse_pos)
        quit_color = (150, 40, 40) if not is_hover_quit else (200, 50, 50)
        pygame.draw.rect(screen, quit_color, self.quit_btn_rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.quit_btn_rect, 1, border_radius=10)
        quit_surf = self.font.render("ABANDON", True, (255, 255, 255))
        screen.blit(quit_surf, quit_surf.get_rect(center=self.quit_btn_rect.center))

# =====================================================================
# เมนูตั้งค่า (Settings)
# =====================================================================
class SettingsMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 28)
        self.label_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.back_btn_rect = pygame.Rect(width//2 - 100, height - 80, 200, 50)
        
        # ตั้งค่าเริ่มต้น
        self.fps = 60
        self.music_volume = 0.4
        self.sfx_volume = 0.6
        self.screen_shake_on = True
        
        # UI Elements Positions - Unified for Init & Draw
        self.control_x = 250
        self.start_y = 150
        self.gap = 55
        
        # FPS Buttons
        self.fps30_btn_rect = pygame.Rect(self.control_x, self.start_y - 5, 80, 40)
        self.fps60_btn_rect = pygame.Rect(self.control_x + 90, self.start_y - 5, 80, 40)
        
        # Volume Sliders
        slider_width = 180
        self.music_slider_rect = pygame.Rect(self.control_x, self.start_y + self.gap + 15, slider_width, 10)
        self.sfx_slider_rect = pygame.Rect(self.control_x, self.start_y + self.gap*2 + 15, slider_width, 10)
        
        # Screen Shake Toggle
        self.shake_on_rect = pygame.Rect(self.control_x, self.start_y + self.gap*3 - 5, 80, 40)
        self.shake_off_rect = pygame.Rect(self.control_x + 90, self.start_y + self.gap*3 - 5, 80, 40)
        
        self.back_btn_rect = pygame.Rect(0, 0, 200, 50)
        self.back_btn_rect.center = (self.width//2, self.height - 50)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Back Button
            if self.back_btn_rect.collidepoint(mouse_pos):
                play_click_sound()
                return "back"
                
            # FPS
            if self.fps30_btn_rect.collidepoint(mouse_pos):
                play_click_sound()
                self.fps = 30
            if self.fps60_btn_rect.collidepoint(mouse_pos):
                play_click_sound()
                self.fps = 60
                
            # Volume Sliders (Click & Drag simulation)
            if self.music_slider_rect.inflate(0, 20).collidepoint(mouse_pos):
                self._update_music_vol(mouse_pos[0])
            if self.sfx_slider_rect.inflate(0, 20).collidepoint(mouse_pos):
                self._update_sfx_vol(mouse_pos[0])
                
                
            # Screen Shake
            if self.shake_on_rect.collidepoint(mouse_pos):
                play_click_sound()
                self.screen_shake_on = True
            if self.shake_off_rect.collidepoint(mouse_pos):
                play_click_sound()
                self.screen_shake_on = False
                
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]: # Pressed
                if self.music_slider_rect.inflate(0, 40).collidepoint(event.pos):
                    self._update_music_vol(event.pos[0])
                if self.sfx_slider_rect.inflate(0, 40).collidepoint(event.pos):
                    self._update_sfx_vol(event.pos[0])
                    
        return None

    def _update_music_vol(self, x):
        rel_x = x - self.music_slider_rect.x
        val = max(0, min(1, rel_x / self.music_slider_rect.width))
        self.music_volume = val
        pygame.mixer.music.set_volume(self.music_volume)

    def _update_sfx_vol(self, x):
        rel_x = x - self.sfx_slider_rect.x
        val = max(0, min(1, rel_x / self.sfx_slider_rect.width))
        self.sfx_volume = val
        # In main loop, this will be applied to sound effects

    def draw(self, screen):
        # 1. พื้นหลังโปร่งแสงแบบมืด (Darker contrast)
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(235)
        overlay.fill((10, 10, 20))
        screen.blit(overlay, (0, 0))
        
        # วาดเส้นแบ่งหัวข้อ
        pygame.draw.line(screen, (0, 200, 255), (50, 110), (self.width-50, 110), 2)
        
        title_surf = self.large_font.render("SYSTEM SETTINGS", True, (0, 200, 255))
        screen.blit(title_surf, title_surf.get_rect(center=(self.width//2, 65)))
        
        white = (240, 240, 240)
        cyan = (0, 200, 255)
        
        # --- LEFT COLUMN: SETTINGS ---
        label_x = 70
        start_y = 150
        gap = 55
        
        # FPS
        screen.blit(self.label_font.render("FRAME RATE", True, white), (label_x, start_y))
        for rect, label, val in [(self.fps30_btn_rect, "30", 30), (self.fps60_btn_rect, "60", 60)]:
            color = cyan if self.fps == val else (60, 60, 80)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            txt = self.font.render(label, True, white)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # Music Vol
        screen.blit(self.label_font.render("MUSIC VOL", True, white), (label_x, start_y + gap))
        pygame.draw.rect(screen, (50, 50, 70), self.music_slider_rect, border_radius=5)
        filled_width = self.music_slider_rect.width * self.music_volume
        pygame.draw.rect(screen, cyan, (self.music_slider_rect.x, self.music_slider_rect.y, filled_width, self.music_slider_rect.height), border_radius=5)
        handle_x = self.music_slider_rect.x + filled_width
        pygame.draw.circle(screen, (255, 255, 255), (int(handle_x), self.music_slider_rect.centery), 10)
        vol_pct = self.font.render(f"{int(self.music_volume * 100)}%", True, white)
        screen.blit(vol_pct, (self.music_slider_rect.right + 15, self.music_slider_rect.y - 12))

        # SFX Vol
        screen.blit(self.label_font.render("SFX VOL", True, white), (label_x, start_y + gap*2))
        pygame.draw.rect(screen, (50, 50, 70), self.sfx_slider_rect, border_radius=5)
        filled_width = self.sfx_slider_rect.width * self.sfx_volume
        pygame.draw.rect(screen, cyan, (self.sfx_slider_rect.x, self.sfx_slider_rect.y, filled_width, self.sfx_slider_rect.height), border_radius=5)
        handle_x = self.sfx_slider_rect.x + filled_width
        pygame.draw.circle(screen, (255, 255, 255), (int(handle_x), self.sfx_slider_rect.centery), 10)
        vol_pct = self.font.render(f"{int(self.sfx_volume * 100)}%", True, white)
        screen.blit(vol_pct, (self.sfx_slider_rect.right + 15, self.sfx_slider_rect.y - 12))

        # Screen Shake
        screen.blit(self.label_font.render("SHAKE", True, white), (label_x, start_y + gap*3))
        for rect, label, val in [(self.shake_on_rect, "ON", True), (self.shake_off_rect, "OFF", False)]:
            color = cyan if self.screen_shake_on == val else (60, 60, 80)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            txt = self.font.render(label, True, white)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # --- กะระยะฝั่งขวา (Controls) ---
        div_x = self.width // 2 + 120
        pygame.draw.line(screen, (60, 60, 80), (div_x - 30, 150), (div_x - 30, 420), 2)
        
        screen.blit(self.label_font.render("CONTROLS", True, cyan), (div_x, 150))
        controls = [
            ("WASD / ARROW", "Move & Jump"),
            ("Z / LMB", "Heavy Attack"),
            ("C / LMB", "Slash Attack"),
            ("X / RMB", "Defend / Parry"),
            ("L-SHIFT", "Sprint"),
            ("ESC / P", "Pause Game")
        ]
        
        cf = pygame.font.SysFont("Arial", 19)
        for i, (key, act) in enumerate(controls):
            ky_txt = cf.render(key, True, cyan)
            ac_txt = cf.render(act, True, (180, 180, 180))
            screen.blit(ky_txt, (div_x, 200 + i*38))
            screen.blit(ac_txt, (div_x + 130, 200 + i*38))

        # SAVE & RETURN Button (Centered Bottom)
        is_hover = self.back_btn_rect.collidepoint(pygame.mouse.get_pos())
        color = (200, 40, 40) if not is_hover else (230, 50, 50)
        self.back_btn_rect.center = (self.width//2, self.height - 50)
        pygame.draw.rect(screen, color, self.back_btn_rect, border_radius=25)
        pygame.draw.rect(screen, white, self.back_btn_rect, 2, border_radius=25)
        back_surf = self.font.render("SAVE & RETURN", True, white)
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
