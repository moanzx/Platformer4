import pygame
from scripts.entities import Mob
from scripts.projectiles import *

class Mushroom(Mob):
    def __init__(self, game, level, pos, entity_name, player) -> None:
        self.size = (30,28)
        super().__init__(game, level, pos, entity_name, player)
        self.speed = 1

        self.animation_speed = {"idle": 0.15,"run": 0.25,"jump": 0,"fall": 0,"hit": 0.10, "death": 0.10}
        self.draw_offset = pygame.math.Vector2(0,6)

        self.health = 1

    def handle_x_velocity(self):
        if self.status == "idle":
            self.velocity.x = 0
            if round(self.animation_index) == len(self.game.entities_assets[self.entity_name + "/" + self.status]):
                self.movement_by_flip_direction()

        else:
            if self.collisions["left"] or self.collisions["right"] or not self.level.tilemap.solid_check((self.rect.centerx + 10, self.pos[1] + 35)) or not self.level.tilemap.solid_check((self.rect.centerx - 10, self.pos[1] + 35)):
                self.flip = not self.flip
                self.velocity.x = 0
                self.animation_index = 0
            else:
                self.movement_by_flip_direction()

class Ba(Mob):
    def __init__(self, game, level, pos, entity_name, player) -> None:
        self.size = (32,32)
        super().__init__(game, level, pos, entity_name, player)
        self.gravity = 0
        self.animation_speed = {"idle": 0.10,"death": 0.10} #{"idle": 0.15,"run": 0.25,"jump": 0,"fall": 0,"hit": 0.10, "death": 0.10}
        self.attack_range_rect = pygame.rect.Rect(self.pos.x - self.game.tile_size * 4, self.pos.y, self.game.tile_size * 9, self.game.tile_size * 5)

    def handle_x_velocity(self):
        if self.player.pos[0] > self.pos[0]:
            self.flip = True
        else:
            self.flip = False
    

    def attack(self):
        self.level.enemy_projectiles.append(Ba_projectile(self.player, self.game,self.level,(self.rect.centerx, self.rect.bottom)))
                    


        
