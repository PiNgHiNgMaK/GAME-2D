import pygame

class background:
    def __init__(self, screen, layers_info):
        """
        layers_info: List ของ tuple หรือ list [(path, speed_factor), ...]
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.layers = []
        
        # ตรวจสอบว่าเป็นรูปแบบเก่า (String path) หรือรูปแบบใหม่ (List layers)
        if isinstance(layers_info, str):
            layers_info = [(layers_info, 1.0)]
        
        for path, speed in layers_info:
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (self.width, self.height))
                self.layers.append({
                    "image": image,
                    "speed": speed
                })
            except Exception as e:
                print(f"Error loading background layer {path}: {e}")

    def draw(self, camera_x=0):
        """
        camera_x: ตำแหน่ง x ของกล้อง/ผู้เล่น สำหรับทำ Parallax
        """
        if not self.layers:
            return
            
        for layer in self.layers:
            # คำนวณตำแหน่ง x ของเลเยอร์ตามความเร็ว (Speed Factor)
            # ใช้ modulo เพื่อให้ภาพวนลูป (Infinite Scrolling)
            rel_x = -(camera_x * layer["speed"]) % self.width
            
            # วาดภาพที่ 1
            self.screen.blit(layer["image"], (rel_x, 0))
            
            # วาดภาพที่ 2 ต่อท้ายเพื่อให้เห็นภาพต่อเนื่องเวลาเลื่อน
            if rel_x < 0:
                self.screen.blit(layer["image"], (rel_x + self.width, 0))
            else:
                self.screen.blit(layer["image"], (rel_x - self.width, 0))