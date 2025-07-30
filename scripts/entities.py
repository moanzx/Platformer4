import pygame

class Entity:
    def __init__(self, game, level, pos, entity_name) -> None:
        self.game = game
        self.level = level
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.entity_name = entity_name
        # self.size = None
        self.rect = None
        self.rect_update()
        self.velocity = pygame.math.Vector2(0,0)
        self.gravity = 0.3  # th = 1 ->  g= 6.5, th = 0.5 -> g = 26
        self.speed = 2.5
        self.movement = {"left": False, "right": False}
        # x = x0 + v0t + 0.5at^2 -> t = 1 (one frame) -> 
        self.draw_offset = pygame.math.Vector2(0,0)
        self.status = "idle"
        self.img = None
        self.flip = False
        self.animation_speed = {}
        self.animation_index = 0
        self.hit = False
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.dying = False
        self.death = False

        self.health = 1


    def update(self):
        if self.health <= 0:
            self.dying = True

        
        if self.dying: 
            if round(self.animation_index) == len(self.game.entities_assets[self.entity_name + "/" + self.status]):
                self.death = True
        # if not self.dying:
        else:
            # Check for special tiles before moving
            self.check_special_tiles()
            
            self.handle_x_velocity()
            self.handle_x_position()
            self.rect_update()
            self.handle_horizontal_collision()

            self.handle_y_velocity()
            self.handle_y_position()
            self.rect_update()
            self.handle_vertical_collision()

        self.handle_img_animation()
        self.handle_status()

        if self.hit:
            if round(self.animation_index) == len(self.game.entities_assets[self.entity_name + "/" + self.status]):
                self.hit = False

    def check_end_tile_at_pos(self, pos):
        """Check if there's an end tile (kill_tile or victory_tile) at the specific position"""
        tile_loc = (int(pos[0] // self.level.game.tile_size), int(pos[1] // self.level.game.tile_size))
        for layer in self.level.tilemap.layer_list:
            check_loc = str(tile_loc[0]) + ';' + str(tile_loc[1])
            if check_loc in layer["grid"]:
                element = layer["grid"][check_loc]["element"]
                if element == "kill_tile":
                    return "death"
                elif element == "victory_tile":
                    return "victory"
        return None

    def check_special_tiles(self):
        """Check for special tiles (kill tiles, victory tiles, etc.) at the player's current position"""
        # Check current position for end tiles
        end_type = self.check_end_tile_at_pos((self.rect.centerx, self.rect.centery))
        if end_type:
            self.level.trigger_game_end(end_type)
            return


    def handle_x_position(self):
        self.pos.x += self.velocity.x
        
    def handle_horizontal_collision(self):
        # Reseting collisions
        self.collisions["left"] = False
        self.collisions["right"] = False

        # Going left
        if self.velocity.x < 0:
            for tile_rect, element in self.level.tilemap.physics_rect_around((self.rect.left, self.rect.centery)):
                if self.rect.colliderect(tile_rect) and element not in ["kill_tile", "victory_tile"]:
                    self.rect.left = tile_rect.right
                    self.pos.x =  self.rect.left
                    self.collisions["left"] = True
        else: #self.velocity.x >= 0
            for tile_rect, element in self.level.tilemap.physics_rect_around((self.rect.right, self.rect.centery)):
                if self.rect.colliderect(tile_rect) and element not in ["kill_tile", "victory_tile"]:
                    self.rect.right = tile_rect.left
                    self.pos.x =  self.rect.left

                    self.collisions["right"] = True

    def handle_y_velocity(self):
        self.velocity.y = min(self.velocity.y + self.gravity, 8) # add maximum speed

    def handle_y_position(self):
        self.pos.y += self.velocity.y

    def handle_vertical_collision(self):
        # Reseting collisions
        self.collisions["bottom"] = False
        self.collisions["top"] = False

        # Going down
        if self.velocity.y >= 0:
            for tile_rect, element in self.level.tilemap.physics_rect_around((self.rect.centerx, self.rect.bottom)):
                if (self.rect.colliderect(tile_rect) or self.rect.move(0,1).colliderect(tile_rect)) and element not in ["kill_tile", "victory_tile"]:
                    self.rect.bottom = tile_rect.top
                    self.velocity.y = 0
                    self.pos.y = self.rect.top
                    self.collisions["bottom"] = True
        # Going up
        else:
            for tile_rect, element in self.level.tilemap.physics_rect_around((self.rect.centerx, self.rect.top)):
                if self.rect.colliderect(tile_rect) and element not in ["kill_tile", "victory_tile"]:
                    self.rect.top = tile_rect.bottom
                    self.velocity.y = 0
                    self.pos.y = self.rect.top
                    self.collisions["top"] = True
        

        

    def rect_update(self):
        # Method for updating rect position (since rect can only work on integers)
        self.rect = pygame.Rect((self.pos[0]), (self.pos[1]) , self.size[0], self.size[1])

    def render(self):
        int_pos = pygame.math.Vector2(int(self.pos[0]), int(self.pos[1]))
        self.level.surface.blit(self.img, int_pos - self.level.scroll - self.draw_offset)



    def handle_img_animation(self):
        dict_path = self.entity_name + "/" + self.status
        self.animation_index = (self.animation_index + self.animation_speed[self.status]) % len(self.game.entities_assets[dict_path])
        img = self.game.entities_assets[dict_path][int(self.animation_index)]
        if self.flip: 
            self.img = pygame.transform.flip(img,True,False)
        else:
            self.img = img

    def handle_status(self):
        if self.dying:
            self.status = "death"
        elif self.hit:
            self.status = "hit"
        elif self.velocity.y <= -1:
            self.status = "jump"
        elif self.velocity.y >= 1:
            self.status = "fall"
        elif abs(self.velocity.x) > 0:
            self.status = "run"
        else:
            self.status = "idle"

    def movement_by_flip_direction(self):
        if self.flip:
            self.velocity.x = -self.speed
        else:
            self.velocity.x = self.speed


class Mob(Entity):
    def __init__(self, game, level, pos, entity_name, player) -> None:
        super().__init__(game, level, pos, entity_name)
        self.player = player
        self.attack_cd = 180
        self.attack_range_rect = pygame.rect.Rect(0,0,0,0)

    def check_special_tiles(self):
        pass

    def update(self):
        super().update()
        if self.attack_cd != 180:
            self.attack_cd += 1
        if self.attack_range_rect.colliderect(self.player.rect) and self.attack_cd == 180 and not self.dying:
            self.attack_cd = 0
            self.attack()
            #self.level.enemy_projectiles.append(String_Projectile)




    def attack(self):
        pass
    
    def update_attack_rect(self):
        pass







        