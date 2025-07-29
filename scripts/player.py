import pygame
from scripts.entities import Entity

class Player(Entity):
    def __init__(self, game, level, pos, entity_name) -> None:
        self.size = (16,26)
        super().__init__(game, level, pos, entity_name)
        self.speed = 2.5
        self.animation_speed = {"idle": 0.15,"run": 0.25,"jump": 0,"fall": 0,"hit": 0.10, "death": 0}
        self.draw_offset = pygame.math.Vector2(7,4)
        self.health = 3
        self.max_health = self.health

    def update(self):
        super().update()

    def handle_x_velocity(self):
        if self.movement["left"] and not self.movement["right"]:
            self.velocity.x = -self.speed
            self.flip = True
        elif self.movement["right"] and not self.movement["left"]:
            self.velocity.x = self.speed
            self.flip = False
        else:
            self.velocity.x = 0