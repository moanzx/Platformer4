import pygame, math
from scripts.particles import *

class projectile:
    def __init__(self, player, game, level, pos) -> None:
        self.game = game
        self.level = level
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.velocity = pygame.math.Vector2(0, 0)
        self.player = player
        self.radius = 5
        self.rect = pygame.rect.Rect(self.pos.x - self.radius,self.pos.x - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.pos += self.velocity

        self.rect.x = self.pos.x - self.radius
        self.rect.y = self.pos.y - self.radius


    def render(self):
        pygame.draw.rect(self.level.surface, "blue", self.rect.move(-self.level.scroll.x, - self.level.scroll.y))
        # pygame.draw.circle(self.level.surface, "white", (self.pos.x - self.level.scroll.x, self.pos.y - self.level.scroll.y), self.radius)

    
class Ba_projectile(projectile):
    def __init__(self, player, game, level, pos) -> None:
        super().__init__(player, game, level, pos)
        speed = 3
        strength = ((self.pos[0]- self.player.rect.centerx)**2 + (self.pos[1]- self.player.rect.centery)**2) ** 0.5 
        self.velocity = pygame.math.Vector2(speed * (self.player.rect.centerx- self.pos[0])/strength, speed * (self.player.rect.centery- self.pos[1])/strength)

    def update(self):
        super().update()
        if self.level.tilemap.solid_check(self.pos):
            self.level.enemy_projectiles.remove(self)
            for i in range(36):
                angle = i * (2 * math.pi / 36)
                speed = 1.5
                self.level.particle_list.append(Ba_Particle(self.game, self.level, self.pos, pygame.math.Vector2(random.random() * speed * math.cos(angle), random.random() * speed * math.sin(angle))))


    def render(self):
        pygame.draw.circle(self.level.surface, "white", (self.pos.x - self.level.scroll.x, self.pos.y - self.level.scroll.y), self.radius)
