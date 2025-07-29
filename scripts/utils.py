import pygame, importlib

DISPLAY_WIDTH, DISPLAY_HEIGHT = 1280, 720
ALPHA_COLOR = (255, 0 , 255)

def transparent_surface(coords):
    surf = pygame.Surface(coords, pygame.SRCALPHA)
    surf.fill(ALPHA_COLOR)
    surf.set_colorkey(ALPHA_COLOR)
    return surf

def get_mob_class(mob_name):
    module = importlib.import_module("scripts.mobs")
    mob_name = mob_name[0].upper() + mob_name[1:]
    return getattr(module, mob_name)

class Sprite:
    def __init__(self, rect, surface) -> None:
        self.rect = rect
        self.img = surface

    