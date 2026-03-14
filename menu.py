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

# ─────────────────────────────────────────────────────────────
#  PIXEL-ART FONT LOADER
# ─────────────────────────────────────────────────────────────
def _load_pixel_font(size):
    """Load PressStart2P (pixel-perfect). Fallback to monospace."""
    path = "assets/fonts/PressStart2P-Regular.ttf"
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("Courier New", size, bold=True)

def _load_vt_font(size):
    """Load VT323 for body / labels."""
    path = "assets/fonts/VT323-Regular.ttf"
    if os.path.exists(path):
        return pygame.font.Font(path, size)
    return pygame.font.SysFont("Courier New", size)

# ─────────────────────────────────────────────────────────────
#  PIXEL-ART DRAWING HELPERS
# ─────────────────────────────────────────────────────────────

# Colour palette – dark medieval
C_BG        = (8,  4, 10)          # Almost-black purple
C_BLOOD     = (140, 10, 10)        # Deep blood red
C_CRIMSON   = (200, 30, 30)        # Vivid crimson
C_GOLD      = (210, 160, 20)       # Tarnished gold
C_GOLD_LIT  = (255, 210, 60)       # Bright highlight gold
C_STONE     = (55,  48, 42)        # Dark stone grey-brown
C_STONE2    = (80,  70, 60)        # Lighter stone
C_WHITE     = (230, 220, 200)      # Parchment white
C_DIM       = (110, 100, 90)       # Dim label
C_SHADOW    = (0,   0,   0)
C_ACCENT    = (90,  30,  30)       # Dark red accent
C_HOVER     = (255, 200, 50)       # Gold hover glow
C_SLASH     = (180, 20, 20)        # Red slash decoration


def draw_pixel_border(surface, rect, color, thickness=3, corner=6):
    """Draw a hard-edged, squared pixel-art frame (no rounded corners)."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    # Outer rectangle
    pygame.draw.rect(surface, color, rect, thickness)
    # Pixel corner notches – clip the actual corner pixels
    pygame.draw.rect(surface, C_BG, (x, y, corner, corner))
    pygame.draw.rect(surface, C_BG, (x + w - corner, y, corner, corner))
    pygame.draw.rect(surface, C_BG, (x, y + h - corner, corner, corner))
    pygame.draw.rect(surface, C_BG, (x + w - corner, y + h - corner, corner, corner))
    # Re-draw corner marks in a contrasting accent
    for cx, cy in [(x+1, y+1), (x+w-corner, y+1), (x+1, y+h-corner), (x+w-corner, y+h-corner)]:
        pygame.draw.rect(surface, color, (cx, cy, corner-2, corner-2), 1)


def draw_pixel_button(surface, rect, base_color, hover_color, is_hover, border_color=None):
    """Draw a pixel-art styled button with a 3-D inset look."""
    bc = border_color or C_GOLD
    bg = hover_color if is_hover else base_color
    # Fill
    pygame.draw.rect(surface, bg, rect)
    # Top/Left highlight (lighter edge)
    light = tuple(min(c + 40, 255) for c in bg)
    dark  = tuple(max(c - 40, 0)   for c in bg)
    pygame.draw.line(surface, light, rect.topleft, rect.topright, 2)
    pygame.draw.line(surface, light, rect.topleft, rect.bottomleft, 2)
    pygame.draw.line(surface, dark,  rect.bottomleft, rect.bottomright, 2)
    pygame.draw.line(surface, dark,  rect.topright,   rect.bottomright, 2)
    # Pixel border
    draw_pixel_border(surface, rect, bc, thickness=2, corner=4)


def draw_rune_divider(surface, cx, y, half_width, color=C_GOLD):
    """Draw a horizontal rune-style divider line with centre diamond."""
    pygame.draw.line(surface, color, (cx - half_width, y), (cx + half_width, y), 2)
    # Diamond
    d = 6
    pts = [(cx, y - d), (cx + d, y), (cx, y + d), (cx - d, y)]
    pygame.draw.polygon(surface, color, pts)


def draw_corner_ornament(surface, x, y, size, flip_x=False, flip_y=False, color=C_GOLD):
    """Draw a pixel corner ornament (L-shaped bracket)."""
    sx = -1 if flip_x else 1
    sy = -1 if flip_y else 1
    for i in range(size):
        pygame.draw.rect(surface, color, (x + sx * i, y, 1, 2))
        pygame.draw.rect(surface, color, (x, y + sy * i, 2, 1))
    pygame.draw.rect(surface, C_BLOOD, (x + sx * 2, y + sy * 2, 3, 3))


def draw_blood_drip(surface, x, y, length, color=C_BLOOD):
    """Draw a dripping blood pixel strip."""
    for i in range(length):
        alpha = max(255 - i * 18, 40)
        w = max(3 - i // 3, 1)
        pygame.draw.rect(surface, color, (x, y + i, w, 1))


def render_pixel_text_shadow(surface, font, text, color, shadow_color, pos, shadow_offset=(2, 2)):
    """Render text with a drop shadow."""
    sx, sy = pos[0] + shadow_offset[0], pos[1] + shadow_offset[1]
    shadow_surf = font.render(text, False, shadow_color)
    surface.blit(shadow_surf, (sx, sy))
    text_surf = font.render(text, False, color)
    surface.blit(text_surf, pos)
    return text_surf.get_rect(topleft=pos)

# ─────────────────────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────────────────────
class MainMenu:
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        pygame.font.init()

        # Fonts
        self.font_title    = _load_pixel_font(22)   # "The Echo of the Abyss"
        self.font_sub      = _load_pixel_font(10)   # subtitle
        self.font_btn      = _load_pixel_font(10)   # button labels
        self.font_label    = _load_pixel_font(9)    # small labels
        self.font_warn     = _load_vt_font(26)      # warning text
        self.font_input    = _load_vt_font(32)      # name input

        # Input
        self.name_text     = ""
        self.input_rect    = pygame.Rect(width//2 - 160, height//2 - 10, 320, 42)
        self.is_input_active = False

        # Buttons
        bw = 270
        bx = width//2 - bw//2
        self.play_btn_rect     = pygame.Rect(bx, height//2 + 70, bw, 46)
        self.settings_btn_rect = pygame.Rect(bx, height//2 + 130, bw, 46)
        self.quit_btn_rect     = pygame.Rect(bx, height//2 + 190, bw, 46)

        # Cursor blink
        self._tick = 0

        # Background
        try:
            bg_path = "background/game_menu_background_clean_1773374248931.png"
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path).convert()
                self.background = pygame.transform.scale(self.background, (width, height))
            else:
                self.background = None
        except:
            self.background = None

    # ── Events ──────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_input_active = self.input_rect.collidepoint(event.pos)

            if self.play_btn_rect.collidepoint(event.pos) and self.name_text.strip():
                play_click_sound()
                return "play", self.name_text.strip()
            if self.settings_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "settings", None
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound()
                return "quit", None

        if event.type == pygame.KEYDOWN and self.is_input_active:
            if event.key == pygame.K_BACKSPACE:
                self.name_text = self.name_text[:-1]
            elif len(self.name_text) < 15 and event.unicode.isprintable():
                self.name_text += event.unicode

        return None, None

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, screen):
        self._tick += 1

        # ── Background ──────────────────────────────────────
        if self.background:
            screen.blit(self.background, (0, 0))
            ov = pygame.Surface((self.width, self.height))
            ov.set_alpha(160)
            ov.fill((4, 2, 8))
            screen.blit(ov, (0, 0))
        else:
            screen.fill(C_BG)

        cx = self.width // 2

        # ── Drip decoration (top) ────────────────────────────
        for dx in range(50, self.width - 50, 55):
            drip_len = 6 + (dx * 7 % 14)
            draw_blood_drip(screen, dx, 0, drip_len)

        # ── Corner ornaments ─────────────────────────────────
        draw_corner_ornament(screen, 18,  18,  18, False, False)
        draw_corner_ornament(screen, self.width - 20, 18,  18, True,  False)
        draw_corner_ornament(screen, 18,  self.height - 20, 18, False, True)
        draw_corner_ornament(screen, self.width - 20, self.height - 20, 18, True,  True)

        # ── Title ────────────────────────────────────────────
        title_surf = self.font_title.render("THE ECHO OF THE ABYSS", False, C_GOLD)
        tw = title_surf.get_width()
        # two layers of shadow for depth
        screen.blit(self.font_title.render("THE ECHO OF THE ABYSS", False, (60,0,0)),   (cx - tw//2 + 4, 58))
        screen.blit(self.font_title.render("THE ECHO OF THE ABYSS", False, C_BLOOD),    (cx - tw//2 + 2, 56))
        screen.blit(title_surf, (cx - tw//2, 54))

        # Subtitle
        sub = self.font_sub.render("-- REVERSED FATE --", False, C_CRIMSON)
        screen.blit(sub, sub.get_rect(center=(cx, 98)))

        # Dividers
        draw_rune_divider(screen, cx, 118, 200, C_GOLD)

        # ── Warrior's Name Label ──────────────────────────────
        lbl = self.font_label.render("WARRIOR'S NAME", False, C_DIM)
        screen.blit(lbl, (self.input_rect.x, self.input_rect.y - 22))

        # ── Input Box (pixel-art border) ──────────────────────
        pygame.draw.rect(screen, (12, 6, 6), self.input_rect)
        bc = C_GOLD if self.is_input_active else C_STONE2
        draw_pixel_border(screen, self.input_rect, bc, thickness=2, corner=5)

        # Blinking cursor
        display_text = self.name_text
        if self.is_input_active and (self._tick // 30) % 2 == 0:
            display_text += "_"
        txt_surf = self.font_input.render(display_text, False, C_WHITE)
        screen.blit(txt_surf, (self.input_rect.x + 12, self.input_rect.y + 5))

        # Warning
        if not self.name_text.strip():
            warn = self.font_warn.render("* Enter your name to begin your destiny *", False, C_BLOOD)
            screen.blit(warn, warn.get_rect(center=(cx, self.input_rect.bottom + 18)))

        # ── Buttons ────────────────────────────────────────────
        mouse_pos = pygame.mouse.get_pos()

        # PLAY
        can_play   = bool(self.name_text.strip())
        hover_play = self.play_btn_rect.collidepoint(mouse_pos) and can_play
        play_base  = C_BLOOD if can_play else C_STONE
        draw_pixel_button(screen, self.play_btn_rect, play_base, C_CRIMSON, hover_play, C_GOLD_LIT)
        play_label = self.font_btn.render("BEGIN JOURNEY", False, C_GOLD_LIT if hover_play else C_WHITE)
        screen.blit(play_label, play_label.get_rect(center=self.play_btn_rect.center))

        # SETTINGS
        hover_set = self.settings_btn_rect.collidepoint(mouse_pos)
        draw_pixel_button(screen, self.settings_btn_rect, C_STONE, C_STONE2, hover_set, C_GOLD)
        set_label = self.font_btn.render("SETTINGS", False, C_GOLD if hover_set else C_DIM)
        screen.blit(set_label, set_label.get_rect(center=self.settings_btn_rect.center))

        # QUIT
        hover_quit = self.quit_btn_rect.collidepoint(mouse_pos)
        draw_pixel_button(screen, self.quit_btn_rect, (50, 12, 12), C_ACCENT, hover_quit, C_CRIMSON)
        q_label = self.font_btn.render("ABANDON", False, C_CRIMSON if hover_quit else C_DIM)
        screen.blit(q_label, q_label.get_rect(center=self.quit_btn_rect.center))

        # Bottom divider
        draw_rune_divider(screen, cx, self.height - 28, 160, C_STONE2)


# ─────────────────────────────────────────────────────────────
#  SETTINGS MENU
# ─────────────────────────────────────────────────────────────
class SettingsMenu:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

        self.font_title  = _load_pixel_font(16)
        self.font_label  = _load_pixel_font(9)
        self.font_body   = _load_vt_font(26)
        self.font_val    = _load_vt_font(28)

        # Settings state
        self.fps           = 60
        self.music_volume  = 0.4
        self.sfx_volume    = 0.6
        self.screen_shake_on = True

        # Layout
        self.cx        = width // 2
        self.ctrl_x    = 230
        self.label_x   = 50
        self.start_y   = 145
        self.gap       = 60

        # FPS buttons
        self.fps30_btn_rect = pygame.Rect(self.ctrl_x,       self.start_y - 5, 88, 38)
        self.fps60_btn_rect = pygame.Rect(self.ctrl_x + 100, self.start_y - 5, 88, 38)

        # Sliders
        sw = 200
        self.music_slider_rect = pygame.Rect(self.ctrl_x, self.start_y + self.gap + 14, sw, 10)
        self.sfx_slider_rect   = pygame.Rect(self.ctrl_x, self.start_y + self.gap*2 + 14, sw, 10)

        # Shake buttons
        self.shake_on_rect  = pygame.Rect(self.ctrl_x,       self.start_y + self.gap*3 - 5, 88, 38)
        self.shake_off_rect = pygame.Rect(self.ctrl_x + 100, self.start_y + self.gap*3 - 5, 88, 38)

        # Back button
        self.back_btn_rect = pygame.Rect(0, 0, 220, 46)
        self.back_btn_rect.center = (width // 2, height - 50)

    # ── Events ──────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mp = event.pos
            if self.back_btn_rect.collidepoint(mp):
                play_click_sound(); return "back"
            if self.fps30_btn_rect.collidepoint(mp):
                play_click_sound(); self.fps = 30
            if self.fps60_btn_rect.collidepoint(mp):
                play_click_sound(); self.fps = 60
            if self.music_slider_rect.inflate(0, 20).collidepoint(mp):
                self._update_music_vol(mp[0])
            if self.sfx_slider_rect.inflate(0, 20).collidepoint(mp):
                self._update_sfx_vol(mp[0])
            if self.shake_on_rect.collidepoint(mp):
                play_click_sound(); self.screen_shake_on = True
            if self.shake_off_rect.collidepoint(mp):
                play_click_sound(); self.screen_shake_on = False

        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if self.music_slider_rect.inflate(0, 40).collidepoint(event.pos):
                self._update_music_vol(event.pos[0])
            if self.sfx_slider_rect.inflate(0, 40).collidepoint(event.pos):
                self._update_sfx_vol(event.pos[0])

        return None

    def _update_music_vol(self, x):
        rel = x - self.music_slider_rect.x
        self.music_volume = max(0.0, min(1.0, rel / self.music_slider_rect.width))
        pygame.mixer.music.set_volume(self.music_volume)

    def _update_sfx_vol(self, x):
        rel = x - self.sfx_slider_rect.x
        self.sfx_volume = max(0.0, min(1.0, rel / self.sfx_slider_rect.width))

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, screen):
        # Dark overlay
        ov = pygame.Surface((self.width, self.height))
        ov.set_alpha(240)
        ov.fill((6, 3, 8))
        screen.blit(ov, (0, 0))

        cx = self.cx

        # Title
        title = self.font_title.render("SETTINGS", False, C_GOLD)
        tw = title.get_width()
        screen.blit(self.font_title.render("SETTINGS", False, C_BLOOD), (cx - tw//2 + 2, 32))
        screen.blit(title, (cx - tw//2, 30))
        draw_rune_divider(screen, cx, 68, 220, C_GOLD)

        # Corner ornaments
        draw_corner_ornament(screen, 14, 14,   14, False, False)
        draw_corner_ornament(screen, self.width - 16, 14, 14, True, False)

        white = C_WHITE
        mp    = pygame.mouse.get_pos()

        # ── FPS ──────────────────────────────────────────────
        screen.blit(self.font_label.render("FRAME RATE", False, C_DIM), (self.label_x, self.start_y))
        for rect, label_str, val in [(self.fps30_btn_rect, "30 FPS", 30), (self.fps60_btn_rect, "60 FPS", 60)]:
            active  = self.fps == val
            is_hov  = rect.collidepoint(mp)
            bc      = C_GOLD_LIT if active else (C_STONE2 if is_hov else C_STONE)
            draw_pixel_button(screen, rect, C_BLOOD if active else C_STONE, C_CRIMSON if active else C_STONE2, is_hov, bc)
            txt = self.font_body.render(label_str, False, C_GOLD if active else white)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # ── Music Volume ──────────────────────────────────────
        screen.blit(self.font_label.render("MUSIC VOL", False, C_DIM), (self.label_x, self.start_y + self.gap))
        self._draw_slider(screen, self.music_slider_rect, self.music_volume)

        # ── SFX Volume ────────────────────────────────────────
        screen.blit(self.font_label.render("SFX VOL", False, C_DIM), (self.label_x, self.start_y + self.gap*2))
        self._draw_slider(screen, self.sfx_slider_rect, self.sfx_volume)

        # ── Screen Shake ──────────────────────────────────────
        screen.blit(self.font_label.render("SCREEN SHAKE", False, C_DIM), (self.label_x, self.start_y + self.gap*3))
        for rect, label_str, val in [(self.shake_on_rect, "ON", True), (self.shake_off_rect, "OFF", False)]:
            active  = self.screen_shake_on == val
            is_hov  = rect.collidepoint(mp)
            draw_pixel_button(screen, rect, C_BLOOD if active else C_STONE, C_CRIMSON if active else C_STONE2, is_hov, C_GOLD_LIT if active else C_STONE2)
            txt = self.font_body.render(label_str, False, C_GOLD if active else white)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # ── Controls column ───────────────────────────────────
        div_x = self.width // 2 + 100
        pygame.draw.line(screen, C_STONE2, (div_x - 20, 90), (div_x - 20, self.height - 90), 1)
        ctrl_head = self.font_label.render("CONTROLS", False, C_GOLD)
        screen.blit(ctrl_head, (div_x, 90))
        draw_rune_divider(screen, div_x + 80, 110, 80, C_STONE2)

        controls = [
            ("WASD / ARROW", "Move & Jump"),
            ("Z / LMB",      "Heavy Attack"),
            ("C / LMB",      "Slash Attack"),
            ("X / RMB",      "Defend / Parry"),
            ("L-SHIFT",      "Sprint"),
            ("ESC / P",      "Pause Game"),
        ]
        for i, (key, act) in enumerate(controls):
            ky  = self.font_body.render(key, False, C_GOLD)
            ac  = self.font_body.render(act, False, C_DIM)
            y   = 130 + i * 40
            screen.blit(ky, (div_x, y))
            screen.blit(ac, (div_x + 155, y))

        # ── Back button ───────────────────────────────────────
        self.back_btn_rect.center = (cx, self.height - 50)
        is_hov = self.back_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.back_btn_rect, C_BLOOD, C_CRIMSON, is_hov, C_GOLD)
        bl = self.font_label.render("SAVE & RETURN", False, C_GOLD_LIT if is_hov else C_WHITE)
        screen.blit(bl, bl.get_rect(center=self.back_btn_rect.center))

        draw_rune_divider(screen, cx, self.height - 80, 200, C_STONE2)

    def _draw_slider(self, surface, rect, value):
        """Pixel-art slider."""
        # Track background
        pygame.draw.rect(surface, C_STONE, rect)
        # Filled portion
        fw = int(rect.width * value)
        pygame.draw.rect(surface, C_BLOOD, (rect.x, rect.y, fw, rect.height))
        # Pixel frame
        draw_pixel_border(surface, rect, C_STONE2, thickness=1, corner=2)
        # Handle
        hx = rect.x + fw
        pygame.draw.rect(surface, C_GOLD, (hx - 4, rect.y - 5, 8, rect.height + 10))
        draw_pixel_border(surface, pygame.Rect(hx - 4, rect.y - 5, 8, rect.height + 10), C_GOLD_LIT, thickness=1, corner=2)
        # Percentage label
        pct = self.font_val.render(f"{int(value * 100)}%", False, C_DIM)
        surface.blit(pct, (rect.right + 12, rect.y - 10))


# ─────────────────────────────────────────────────────────────
#  PAUSE MENU
# ─────────────────────────────────────────────────────────────
class PauseMenu:
    def __init__(self, width, height):
        self.width  = width
        self.height = height

        self.font_title = _load_pixel_font(28)
        self.font_btn   = _load_pixel_font(11)

        bw = 230
        bx = width // 2 - bw // 2
        self.resume_btn_rect   = pygame.Rect(bx, height//2 - 20, bw, 48)
        self.settings_btn_rect = pygame.Rect(bx, height//2 + 48, bw, 48)
        self.quit_btn_rect     = pygame.Rect(bx, height//2 + 116, bw, 48)

    # ── Events ──────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.resume_btn_rect.collidepoint(event.pos):
                play_click_sound(); return "resume"
            if self.settings_btn_rect.collidepoint(event.pos):
                play_click_sound(); return "settings"
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound(); return "quit"
        return None

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, screen):
        ov = pygame.Surface((self.width, self.height))
        ov.set_alpha(200)
        ov.fill((0, 0, 0))
        screen.blit(ov, (0, 0))

        cx = self.width // 2

        # Panel background
        panel = pygame.Rect(cx - 170, self.height//2 - 80, 340, 280)
        pygame.draw.rect(screen, (10, 5, 5), panel)
        draw_pixel_border(screen, panel, C_GOLD, thickness=3, corner=8)

        # Title
        title = self.font_title.render("PAUSED", False, C_GOLD)
        tw = title.get_width()
        screen.blit(self.font_title.render("PAUSED", False, C_BLOOD), (cx - tw//2 + 2, 90))
        screen.blit(title, (cx - tw//2, 88))

        draw_rune_divider(screen, cx, 136, 130, C_STONE2)

        mp = pygame.mouse.get_pos()

        # RESUME
        hov = self.resume_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.resume_btn_rect, (15, 50, 15), (20, 100, 20), hov, C_GOLD)
        rl = self.font_btn.render("RESUME", False, C_GOLD if hov else C_WHITE)
        screen.blit(rl, rl.get_rect(center=self.resume_btn_rect.center))

        # SETTINGS
        hov = self.settings_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.settings_btn_rect, C_STONE, C_STONE2, hov, C_GOLD)
        sl = self.font_btn.render("SETTINGS", False, C_GOLD if hov else C_DIM)
        screen.blit(sl, sl.get_rect(center=self.settings_btn_rect.center))

        # QUIT
        hov = self.quit_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.quit_btn_rect, C_ACCENT, C_BLOOD, hov, C_CRIMSON)
        ql = self.font_btn.render("QUIT", False, C_CRIMSON if hov else C_DIM)
        screen.blit(ql, ql.get_rect(center=self.quit_btn_rect.center))


# ─────────────────────────────────────────────────────────────
#  GAME-OVER / VICTORY MENU
# ─────────────────────────────────────────────────────────────
class GameOverMenu:
    def __init__(self, width, height, title="GAME OVER", color=(200, 30, 30)):
        self.width  = width
        self.height = height
        self.title  = title
        self.color  = color

        self.font_title = _load_pixel_font(24)
        self.font_btn   = _load_pixel_font(11)

        bw = 260
        bx = width  // 2 - bw // 2
        self.play_again_btn_rect = pygame.Rect(bx, height//2 + 10, bw, 48)
        self.quit_btn_rect       = pygame.Rect(bx, height//2 + 78, bw, 48)

    # ── Events ──────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_again_btn_rect.collidepoint(event.pos):
                play_click_sound(); return "play_again"
            if self.quit_btn_rect.collidepoint(event.pos):
                play_click_sound(); return "quit"
        return None

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, screen):
        ov = pygame.Surface((self.width, self.height))
        ov.set_alpha(200)
        ov.fill((0, 0, 0))
        screen.blit(ov, (0, 0))

        cx = self.width // 2

        # Panel (Increased width significantly to fit long text comfortably)
        panel_width = 800
        panel_height = 280
        panel = pygame.Rect(cx - (panel_width//2), self.height//2 - 130, panel_width, panel_height)
        pygame.draw.rect(screen, (8, 4, 4), panel)
        draw_pixel_border(screen, panel, self.color, thickness=3, corner=8)

        # Title
        t = self.font_title.render(self.title, False, self.color)
        tw = t.get_width()
        screen.blit(self.font_title.render(self.title, False, C_SHADOW), (cx - tw//2 + 3, self.height//2 - 95))
        screen.blit(t, (cx - tw//2, self.height//2 - 98))

        draw_rune_divider(screen, cx, self.height//2 - 28, 200, C_STONE2)

        mp = pygame.mouse.get_pos()

        # PLAY AGAIN
        hov = self.play_again_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.play_again_btn_rect, (15, 50, 15), (20, 100, 20), hov, C_GOLD)
        pl = self.font_btn.render("PLAY AGAIN", False, C_GOLD if hov else C_WHITE)
        screen.blit(pl, pl.get_rect(center=self.play_again_btn_rect.center))

        # QUIT
        hov = self.quit_btn_rect.collidepoint(mp)
        draw_pixel_button(screen, self.quit_btn_rect, C_ACCENT, C_BLOOD, hov, C_CRIMSON)
        ql = self.font_btn.render("QUIT", False, C_CRIMSON if hov else C_DIM)
        screen.blit(ql, ql.get_rect(center=self.quit_btn_rect.center))
