import pygame
import sys
pygame.init()
pygame.display.set_mode((1, 1))

def check(path):
    try:
        img = pygame.image.load(path)
        print(path, img.get_width(), img.get_height())
    except Exception as e:
        print(path, 'Error:', e)

check("Knight_1/Defend.png")
check("Knight_1/Protect.png")
sys.exit(0)
