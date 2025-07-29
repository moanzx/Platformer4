import pygame, sys, math
from scripts.tilemap import Tilemap
from scripts.utils import *
from scripts.player import Player
from scripts.particles import *

NO_SHOW_TILES = ["player_spawner", "kill_tile"]

class Level:
    def __init__(self, game, level_name) -> None:
        self.game = game
        self.level_name = level_name  # Store level name for restart
        self.tilemap = Tilemap(game, level_name) # add loading tilemap instead
        self.enemy_list = []
        self.attack_list = []
        self.particle_list = []
        self.enemy_projectiles = []
        self.scroll = pygame.math.Vector2(0,0)
        self.surface = pygame.Surface(self.game.display.get_size())
        self.render_scale = 2
        self.load_player()
        self.camera_borders = {}
        self.load_camera_borders()
        self.tile_surface = self.draw_tiles()
        self.background_img, self.background_img_size = self.make_background_img()

        
        self.heart_img = [pygame.image.load("assets/interface/hearts/0.png"),pygame.image.load("assets/interface/hearts/1.png")]
        self.heart_width = self.heart_img [0].get_width()

        # Game end system variables
        self.game_end_state = "alive"  # "alive", "ending", "ended"
        self.game_end_timer = 0
        self.game_end_animation_duration = 60  # 1 second at 60 FPS
        self.fade_alpha = 0
        self.game_end_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.game_end_small_font = pygame.font.SysFont('Arial', 24)





    def make_background_img(self):
        img = pygame.image.load("./assets/backgrounds/ellinia.jpeg")
        # img = pygame.image.load("./assets/backgrounds/forest_midj.png")
        
        img_size =  img.get_size()
        new_img = pygame.Surface((img_size[0] * 3, img_size[1] * 3))

        for i in range(3):
            for j in range(3):
                new_img.blit(img,(i*img_size[0], j*img_size[1]))
        return new_img, img_size

    def load_player(self):
        # First load player, then the rest (cause the monster needs the player to be made) need to change this later with a pointer to player_spawner)
        for layer in self.tilemap.layer_list:
            for key in layer["grid"]:
                if layer["grid"][key]["element"] == "player_spawner":
                    self.scroll.x = layer["grid"][key]["pos"][0] * (self.game.tile_size)  - self.game.width / (2 * self.render_scale)
                    self.scroll.y = layer["grid"][key]["pos"][1] * (self.game.tile_size)  - self.game.height  / (2 * self.render_scale)
                    self.player = Player(self.game,self, pygame.math.Vector2(layer["grid"][key]["pos"][0] * (self.game.tile_size), layer["grid"][key]["pos"][1] * (self.game.tile_size)), "player")

    def run(self):
        font = pygame.font.SysFont('Arial', 32)
        while True:
            self.game.clock.tick(60)
            # Event loop and player input
            if self.event_loop():
                return True
            
            # Update death state
            self.update_death_state()
            
            # Only update game if not dead
            if self.game_end_state == "alive":
                self.update()

            self.update_scroll()
            self.render(font)

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                
                # Death state input handling
                if self.game_end_state == "ended":
                    if event.key == pygame.K_r:
                        self.restart_level()
                        return False  # Continue game loop
                    elif event.key == pygame.K_ESCAPE:
                        return True  # Return to menu
                    return False  # Ignore other input when dead

                
                # Normal game input (only when alive)
                if self.game_end_state == "alive":
                    if (event.key == pygame.K_w or event.key == pygame.K_UP) and self.player.collisions["bottom"]:
                        self.player.velocity.y = -8
                    
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.player.movement["left"] = True

                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.player.movement["right"] = True

            if event.type == pygame.KEYUP:
                if (event.key == pygame.K_w or event.key == pygame.K_UP):
                    if self.player.velocity.y < 0:
                        # self.player.velocity.y = -1 * self.player.velocity.y
                        self.player.velocity.y = 0

                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.player.movement["left"] = False

                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.player.movement["right"] = False
    def update(self):
        # print(self.particle_list)
        self.player.update()
        for enemy in self.enemy_list.copy():
            enemy.update()
            if enemy.death:
                self.enemy_list.remove(enemy)
            elif enemy.dying:
                # That means if the enemy is dying you will not be harmed
                pass
            elif enemy.rect.colliderect(self.player.rect):
            # check collision with enemy, and make sure it either hits the player or the mob
                self.handle_enemy_collision(enemy)
        
        for particle in self.particle_list.copy():
            particle.update()
            if particle.radius <= 0:
                self.particle_list.remove(particle)
        
        for projectile in self.enemy_projectiles.copy():
            projectile.update()
            if self.player.rect.colliderect(projectile.rect) and not self.player.hit:
                self.player.health -= 1
                self.player.animation_index = 0
                self.player.hit = True
                self.enemy_projectiles.remove(projectile)
                for i in range(36):
                    angle = i * (2 * math.pi / 36)
                    speed = 1
                    self.particle_list.append(Ba_Particle(self.game, self, projectile.pos, pygame.math.Vector2(random.random() * speed * math.cos(angle), random.random() * speed * math.sin(angle))))

        # General death check - triggers from any source (enemies, projectiles, etc.)
        if self.player.health <= 0 and self.game_end_state == "alive":
            self.trigger_game_end("death")

                
    def handle_enemy_collision(self, enemy):
        if self.player.velocity.y >= 0 and abs(self.player.rect.bottom - enemy.rect.top) < 8:
            enemy.animation_index = 0
            # enemy.dying = True
            enemy.health -= 1
            if enemy.health <= 0:
                # self.create_death_particles((enemy.rect.centerx, enemy.rect.bottom))
                for i in range(50):
                  self.particle_list.append(Death_Particle(self.game, self, (enemy.rect.centerx, enemy.rect.bottom)))
            self.player.velocity.y = -5
        elif not self.player.hit:
            self.player.health -= 1
            self.player.animation_index = 0
            self.player.hit = True

    def trigger_game_end(self, reason="death"):
        """Trigger the game end sequence"""
        if self.game_end_state == "alive":
            self.game_end_state = "ending"
            self.game_end_timer = 0
            self.fade_alpha = 0
            self.game_end_type = reason  # Store whether it's "death" or "victory"
            # Set player to death animation immediately (only for death)
            if reason == "death":
                self.player.animation_index = 0
                self.player.status = "death"

    def update_death_state(self):
        """Update death state and handle transitions"""
        if self.game_end_state == "ending":
            self.game_end_timer += 1
            
            # Fade to black during death animation
            fade_progress = min(self.game_end_timer / 60, 1.0)  # 1 second fade
            self.fade_alpha = int(fade_progress * 255)
            
            # After death animation, show death screen
            if self.game_end_timer >= self.game_end_animation_duration:
                self.game_end_state = "ended"
                self.fade_alpha = 200  # Same alpha as final screen

    def restart_level(self):
        """Restart the current level"""
        # Reset death state
        self.game_end_state = "alive"
        self.game_end_timer = 0
        self.fade_alpha = 0
        
        # Clear all game objects
        self.enemy_list.clear()
        self.attack_list.clear()
        self.particle_list.clear()
        self.enemy_projectiles.clear()
        
        # Reload level data
        self.tilemap = Tilemap(self.game, self.level_name)
        self.load_player()
        self.load_camera_borders()
        self.tile_surface = self.draw_tiles()
        
        # Reset player
        self.player.health = self.player.max_health
        self.player.hit = False
        self.player.status = "idle"

    def render_death_screen(self):
        """Render the game end screen overlay (death or victory)"""
        if self.game_end_state == "ended":
            # Create semi-transparent overlay
            overlay = pygame.Surface((self.game.width, self.game.height))
            overlay.set_alpha(200)  # Semi-transparent
            
            # Set color and text based on game end type
            if self.game_end_type == "victory":
                overlay.fill((100, 80, 0))  # Dark gold
                main_text = "VICTORY!"
                text_color = (255, 215, 0)  # Bright gold
            else:
                overlay.fill((0, 0, 0))  # Black for death
                main_text = "YOU DIED"
                text_color = (255, 0, 0)
            
            self.game.display.blit(overlay, (0, 0))
            
            # Main text
            main_text_surface = self.game_end_font.render(main_text, True, text_color)
            main_rect = main_text_surface.get_rect(center=(self.game.width // 2, self.game.height // 2 - 50))
            self.game.display.blit(main_text_surface, main_rect)
            
            # Instructions
            restart_text = self.game_end_small_font.render("Press R to restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.game.width // 2, self.game.height // 2 + 20))
            self.game.display.blit(restart_text, restart_rect)
            
            menu_text = self.game_end_small_font.render("Press ESC for menu", True, (255, 255, 255))
            menu_rect = menu_text.get_rect(center=(self.game.width // 2, self.game.height // 2 + 50))
            self.game.display.blit(menu_text, menu_rect)
        elif self.game_end_state == "ending" and self.fade_alpha > 0:
            # Fade overlay during animation
            overlay = pygame.Surface((self.game.width, self.game.height))
            overlay.set_alpha(self.fade_alpha)
            
            # Set color based on game end type
            if self.game_end_type == "victory":
                overlay.fill((100, 80, 0))  # Dark gold for victory
            else:
                overlay.fill((0, 0, 0))  # Black for death
            
            self.game.display.blit(overlay, (0, 0))



    


    def render(self, font):
        self.render_background()
        self.draw_tilemap()
        for enemy in self.enemy_list:
            # # for seeing attack_rect_range
            # pygame.draw.rect(self.surface, "white", enemy.attack_range_rect.move(-self.scroll.x, -self.scroll.y))
            # #
            ## for seeing hitboxes
            # pygame.draw.rect(self.surface, "blue", enemy.rect.move(-self.scroll.x, -self.scroll.y))
            ##

            enemy.render()

        for particle in self.particle_list:
            particle.render()

        for projectile in self.enemy_projectiles.copy():
            projectile.render()

        self.player.render()
        self.render_hearts()



        self.game.display.blit(pygame.transform.scale_by(self.surface, self.render_scale), (0,0))

        # self.game.display.blit(self.surface, (0,0))
        # text = font.render(str(int(self.game.clock.get_fps())),True, "white", pygame.SRCALPHA)
        text = font.render(str(int(self.player.velocity.y)),True, "white", pygame.SRCALPHA)

        # print(self.player.velocity)
        self.game.display.blit(text, (self.game.width - text.get_width(), 0))
        
        # Render death screen overlay
        self.render_death_screen()
        
        pygame.display.update()

    def render_hearts(self):
        for heart, x_pos in enumerate(range(10,self.heart_width * self.player.max_health + 2 * self.player.max_health, self.heart_width + 2)):
            if heart < self.player.health:
                self.surface.blit(self.heart_img[0], (x_pos, 10))
            else:
                self.surface.blit(self.heart_img[1], (x_pos, 10))

    def render_background(self):
        fix_x = ((self.player.pos.x / 2) // self.background_img_size[0]) * self.background_img_size[0]
        fix_y = ((self.player.pos.y / 2) // self.background_img_size[1]) * self.background_img_size[1]
        # print(fix_x)
        # self.surface.blit(self.background_img, (fix_x - self.background_img_size[0] + self.scroll[0]* -0.5,self.scroll[1] * -0.5))
        # self.surface.blit(self.background_img, (fix_x + self.scroll[0]* -0.5,self.scroll[1] * -0.5))
        # self.surface.blit(self.background_img, (fix_x + self.scroll[0]* -0.5,-self.background_img_size[1] + self.scroll[1] * -0.5))
        # self.surface.blit(self.background_img, (fix_x + self.background_img_size[0] + self.scroll[0]* -0.5,self.scroll[1] * -0.5))
        self.surface.blit(self.background_img, (fix_x - self.background_img_size[0] + self.scroll[0]* -0.5, fix_y - self.background_img_size[1] + self.scroll[1] * -0.5))
    
    def draw_tiles(self):
        cache_surface = pygame.surface.Surface(((self.tilemap.borders["right"] - self.tilemap.borders["left"]) * self.game.tile_size + self.game.tile_size, (self.tilemap.borders["bottom"] - self.tilemap.borders["top"]) * self.game.tile_size+ self.game.tile_size))
        cache_surface.set_colorkey((0,0,0))
        for layer in self.tilemap.layer_list:
            for x in range(self.tilemap.borders["left"], self.tilemap.borders["right"]):
                for y in range(self.tilemap.borders["top"] ,self.tilemap.borders["bottom"]):
                    loc = str(x) + ';' + str(y)
                    if loc in layer["grid"]:
                        if layer["grid"][loc]["element"] not in NO_SHOW_TILES and layer["grid"][loc]["world_element_type"] != "entities" :
                            element_surface_list = self.game.static_assets[f'{layer["grid"][loc]["world_element_type"]}/{layer["grid"][loc]["element"]}']
                            element_variance = layer["grid"][loc]["variance"]
                            element_pos = layer["grid"][loc]["pos"]
                            cache_surface.blit(element_surface_list[element_variance], (element_pos[0] * self.game.tile_size - self.tilemap.borders["left"] * self.game.tile_size, element_pos[1] * self.game.tile_size - self.tilemap.borders["top"] * self.game.tile_size))
                        elif layer["grid"][loc]["world_element_type"] == "entities":
                            pos = pygame.math.Vector2(layer["grid"][loc]["pos"][0] * self.game.tile_size, layer["grid"][loc]["pos"][1] * self.game.tile_size)
                            self.enemy_list.append(get_mob_class(layer["grid"][loc]["element"])(self.game, self, pos , layer["grid"][loc]["element"], self.player))
     #self.player = Player(self.game,self, pygame.math.Vector2(layer["grid"][key]["pos"][0] * (self.game.tile_size), layer["grid"][key]["pos"][1] * (self.game.tile_size)), "player")

        return Cache_tiles(self.game, self, cache_surface)

            
        

    def draw_tilemap(self):
        self.tile_surface.render(self.scroll)
    


    def update_scroll(self):
        if self.player.rect.left < self.camera_borders["left"]:
            self.scroll.x += (self.camera_borders["left"] - self.game.width/ (2 * self.render_scale) - self.scroll.x) / 30
        elif self.player.rect.right > self.camera_borders["right"]:
            self.scroll.x += (self.camera_borders["right"] - self.game.width/ (2 * self.render_scale) - self.scroll.x) / 30
        else:
            self.scroll.x += (self.player.rect.centerx - self.game.width/ (2 * self.render_scale) - self.scroll.x) / 30

        if self.player.rect.top < self.camera_borders["top"]:
            self.scroll.y += (self.camera_borders["top"] - self.game.height / (2 * self.render_scale) - self.scroll.y) / 15
        elif self.player.rect.bottom > self.camera_borders["bottom"]:
            self.scroll.y += (self.camera_borders["bottom"] - self.game.height / (2 * self.render_scale) - self.scroll.y) / 15
        else:
            self.scroll.y += (self.player.rect.centery - self.game.height / (2 * self.render_scale) - self.scroll.y) / 15

    def load_camera_borders(self):
        self.camera_borders["top"] =  self.tilemap.borders["top"] * self.game.tile_size + self.game.height / (2* self.render_scale)
        self.camera_borders["bottom"] = self.tilemap.borders["bottom"] * self.game.tile_size - self.game.height / (2* self.render_scale)
        self.camera_borders["left"] = self.tilemap.borders["left"] * self.game.tile_size + self.game.width / (2* self.render_scale)
        self.camera_borders["right"] = self.tilemap.borders["right"] * self.game.tile_size - self.game.width / (2* self.render_scale)


class Cache_tiles:
    def __init__(self, game, level, surface) -> None:
        self.game = game
        self.level = level
        self.surface= surface
        # self.rect = surface.get_rect(topleft = (self.level.tilemap.borders["left"] * self.game.tile_size, self.level.tilemap.borders["top"] * self.game.tile_size))
        self.pos = pygame.math.Vector2(self.level.tilemap.borders["left"] * self.game.tile_size, self.level.tilemap.borders["top"] * self.game.tile_size)
    
    def render(self, scroll):
        self.level.surface.blit(self.surface, self.pos - scroll)

