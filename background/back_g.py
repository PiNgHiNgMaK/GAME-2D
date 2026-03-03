import pygame

class background:
    def __init__(self, screen, image_path):
        self.screen = screen
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (screen.get_width(), screen.get_height()))

    def draw(self):
        self.screen.blit(self.image, (0, 0))