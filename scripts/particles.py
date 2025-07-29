import pygame
import random

def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2 ,radius * 2))
    pygame.draw.circle(surf,color,(radius,radius),radius)
    surf.set_colorkey((0,0,0))
    return surf

class Particle:
    def __init__(self, game, level, pos) -> None:
        self.game = game
        self.level = level
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.velocity = pygame.math.Vector2(0, 0)
        self.radius = 1
    def update(self):
        pass

    def render(self):
        pass

class Death_Particle(Particle):
    def __init__(self, game, level, pos) -> None:
        super().__init__(game, level, pos)
        self.velocity = pygame.math.Vector2(random.random() -0.5 ,random.random() -2)
        self.radius = 5

    def update(self):
        self.velocity.y += 0.05
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        self.radius -= 0.05
    
    def render(self,): 
        pygame.draw.circle(self.level.surface, "orange", (self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]), self.radius)
        self.level.surface.blit(circle_surf(self.radius * 1.4 , (50,50,50)),(self.pos[0]- self.level.scroll[0]-self.radius * 1.4 , self.pos[1]- self.level.scroll[1]-self.radius * 1.4), special_flags = pygame.BLEND_RGB_ADD)

class Ba_Particle(Particle):
    def __init__(self, game, level, pos, velocity) -> None:
        super().__init__(game, level, pos)
        self.velocity = velocity
        self.radius = 4

    def update(self):
        self.pos.x += self.velocity.x
        self.pos.y += self.velocity.y
        self.radius -= 0.1

    def render(self): 
            pygame.draw.circle(self.level.surface, "white", (self.pos[0] - self.level.scroll[0], self.pos[1] - self.level.scroll[1]), self.radius)
            self.level.surface.blit(circle_surf(self.radius * 1.4 , (50,50,50)),(self.pos[0]- self.level.scroll[0]-self.radius * 1.4 , self.pos[1]- self.level.scroll[1]-self.radius * 1.4), special_flags = pygame.BLEND_RGB_ADD)
