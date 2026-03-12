import pygame
import time

class DialogueManager:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # ลองโหลดฟอนต์หลายๆ แบบ
        # ปรับฟอนต์ให้ดูดีขึ้น
        thai_fonts = ["Segoe UI", "Tahoma", "Arial", "Verdana"]
        self.font = None
        for f in thai_fonts:
            try:
                self.font = pygame.font.SysFont(f, 26, bold=True)
                if self.font: break
            except: continue
        
        self.active_message = ""
        self.display_text = ""
        self.start_time = 0
        self.duration = 7.0 # ให้อยู่ยาวขึ้นเพื่อให้คนอ่านทัน
        self.is_showing = False
        
        # สำหรับ Typewriter Effect
        self.char_index = 0
        self.last_char_time = 0
        self.char_delay = 0.035 

        # ตำแหน่งแถบข้อความ (เพิ่มความสูงเพื่อกันข้อความตก)
        self.box_width = 760
        self.box_height = 140
        self.box_x = (screen_width - self.box_width) // 2
        self.box_y = screen_height - self.box_height - 30 
        
        # ปุ่มปิด
        self.close_btn_rect = pygame.Rect(self.box_x + self.box_width - 110, self.box_y + self.box_height - 35, 100, 25)
        self.small_font = pygame.font.SysFont("Arial", 14, bold=True)
        
    def show_message(self, text):
        if not text: return
        self.active_message = text
        self.display_text = ""
        self.char_index = 0
        self.start_time = time.time()
        self.last_char_time = time.time()
        self.is_showing = True

    def handle_event(self, event):
        """คืนค่า True หากมีการกดปิดกล่องข้อความ"""
        if not self.is_showing:
            return False
            
        # ปิดเมื่อกดปุ่มเมาส์บนปุ่ม CLOSE
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_btn_rect.collidepoint(event.pos):
                self.is_showing = False
                return True
        # ปิดเมื่อกด Space หรือ F
        elif event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_f]:
                self.is_showing = False
                return True
        return False

    def update(self):
        if not self.is_showing: return
        
        if self.char_index < len(self.active_message):
            if time.time() - self.last_char_time > self.char_delay:
                self.display_text += self.active_message[self.char_index]
                self.char_index += 1
                self.last_char_time = time.time()

    def draw(self, screen):
        if not self.is_showing: return

        # 1. วาดแถบพื้นหลัง
        overlay = pygame.Surface((self.box_width, self.box_height))
        overlay.set_alpha(230)
        overlay.fill((15, 15, 25)) 
        screen.blit(overlay, (self.box_x, self.box_y))

        # 2. วาดขอบ
        pygame.draw.rect(screen, (0, 100, 200), (self.box_x-2, self.box_y-2, self.box_width+4, self.box_height+4), 2)
        pygame.draw.rect(screen, (0, 200, 255), (self.box_x, self.box_y, self.box_width, self.box_height), 1)

        # 3. แบ่งบรรทัด
        words = self.display_text.split(' ')
        lines = []
        current_line = ""
        max_line_width = self.box_width - 60

        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < max_line_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        # 4. วาดตัวอักษร
        y_offset = self.box_y + 20
        for line in lines:
            if not line.strip(): continue
            line_surf = self.font.render(line.strip(), True, (255, 215, 0))
            line_rect = line_surf.get_rect(centerx=self.box_x + self.box_width // 2, y=y_offset)
            
            # Shadow
            shadow_surf = self.font.render(line.strip(), True, (0, 0, 0))
            screen.blit(shadow_surf, (line_rect.x + 2, line_rect.y + 2))
            # Main
            screen.blit(line_surf, line_rect)
            y_offset += 35

        # 5. วาดปุ่มปิด เมื่อพิมพ์เสร็จแล้ว
        if self.char_index >= len(self.active_message):
            mouse_pos = pygame.mouse.get_pos()
            btn_color = (60, 60, 80)
            if self.close_btn_rect.collidepoint(mouse_pos):
                btn_color = (200, 50, 50) # Highlight สีแดง
                
            pygame.draw.rect(screen, btn_color, self.close_btn_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), self.close_btn_rect, 1, border_radius=5)
            
            btn_text = self.small_font.render("CLOSE [F]", True, (255, 255, 255))
            screen.blit(btn_text, btn_text.get_rect(center=self.close_btn_rect.center))
            
            # ชวนให้กดนิดนึง (กระพริบ)
            if int(time.time() * 2) % 2 == 0:
                prompt = self.small_font.render("Press SPACE or F to continue...", True, (200, 200, 200))
                screen.blit(prompt, (self.box_x + 20, self.box_y + self.box_height - 25))

# Story Data in English
STORY_DATA = {
    "SCENE_1_START": "I am the Wayward Knight... waking up in this misty forest with no memory. This glowing blade... I feel it drawing evil towards me.",
    "SCENE_2_START": "This shrine... it wants me to 'reflect' the void away.",
    "SCENE_3_START": "The gate is near, but the air feels heavy with magic.",
    "SCENE_4_START": "The Cursed Guardian... at last, we meet.",
    "WIZARD_DEFEATED": "You can kill me... but you cannot kill the 'Past' that awaits in the next room!",
    "BOSS_DEFEATED": "Finally... the echoes are fading. My memory is returning...",
    "ENDING_DAWN": "The mist fades with the fear... I remember now. I am not just a wanderer, but the Guardian of this sunlit realm."
}
