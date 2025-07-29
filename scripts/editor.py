import pygame, sys, os
from pygame.math import Vector2
from pygame.mouse import get_pos as mouse_pos

from scripts.tilemap import Tilemap
from scripts.utils import *
from scripts.level import Level

class Editor:
    def __init__(self, game, level_name) -> None:
        self.game = game
        self.scroll = Vector2()
        self.scale_ratio = 1
        self.surface = pygame.Surface(self.game.display.get_size())
        self.surface.fill(ALPHA_COLOR)
        self.surface.set_colorkey(ALPHA_COLOR)
        self.scaled_display = pygame.Surface(self.game.display.get_size())

        self.drag_offset = Vector2()
        self.left_click = False
        self.middle_click = False
        self.right_click = False
        self.ctrl_click = False

        self.grid_lines_surf = pygame.Surface(self.game.display.get_size())
        self.grid_lines_surf.set_colorkey(ALPHA_COLOR)
        self.grid_lines_surf.set_alpha(30)

        self.world_elements_matrix = self.load_world_elements_matrix()
        # self.world_elements_dict = self.load_world_elements_dict()

        self.editor_interface = Editor_interface(self.game, self)
        self.dont_place_tiles_timer = 0

        self.current_element = self.world_elements_matrix[self.editor_interface.selected_index][self.editor_interface.hotbar[self.editor_interface.selected_index].button_index]

        self.grid_mouse_position = (0,0)  

        self.level_name = level_name
        self.tilemap =  Tilemap(self.game, self.level_name)
        self.layer_index = 0

        self.border_click = False
        self.first_border_point = (0,0)
        self.second_border_point = (0,0)
        self.border_rect = pygame.rect.Rect(self.tilemap.borders["left"] * self.game.tile_size,self.tilemap.borders["top"] * self.game.tile_size, (self.tilemap.borders["right"] - self.tilemap.borders["left"])* self.game.tile_size,(self.tilemap.borders["bottom"] - self.tilemap.borders["top"])* self.game.tile_size)
        self.tilemap.update_border(self.border_rect)

        self.movement = {"right": False, "left": False, "up": False, "down": False}



    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.left_click = True

                if event.button == 2:
                    self.middle_click = True
                    self.drag_offset = Vector2(mouse_pos()) - self.scroll

                if event.button == 3:
                    self.right_click = True

                if event.button == 4:
                    # if self.scale_ratio < 2:
                    #     self.scale_ratio += 1
                    if self.layer_index < len(self.tilemap.layer_list) - 1:
                        self.layer_index += 1
                
                if event.button == 5:
                #     if self.scale_ratio > 1:
                #         self.scale_ratio -= 1
                    if self.layer_index > 0:
                        self.layer_index -= 1
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.left_click = False
                if event.button == 2:
                    self.middle_click = False
                if event.button == 3:
                    self.right_click = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True  # Return to menu
                    
                if event.key == pygame.K_b:
                    if self.border_click:
                        self.border_click = False
                        self.tilemap.update_border(self.border_rect)
                    else:
                        self.border_click = True
                        self.first_border_point = self.grid_mouse_position
                    
                if event.key == pygame.K_LCTRL:
                    self.ctrl_click = True

                if event.key == pygame.K_o:
                    self.tilemap.save()

                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.movement["right"] = True
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.movement["left"] = True
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.movement["up"] = True
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.movement["down"] = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    self.ctrl_click = False
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.movement["right"] = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.movement["left"] = False
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.movement["up"] = False
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.movement["down"] = False

    def handle_scroll(self):
        if self.middle_click:
            self.scroll = Vector2(mouse_pos()) - self.drag_offset

        if self.movement["right"]:
            self.scroll.x -= self.game.tile_size
        if self.movement["left"]:
            self.scroll.x += self.game.tile_size              
        if self.movement["up"]:
            self.scroll.y += self.game.tile_size
        if self.movement["down"]:
            self.scroll.y -= self.game.tile_size

    def handle_left_click(self):
        if self.left_click == True:

            for i, but in enumerate(self.editor_interface.hotbar):
                # Press a first time
                if but.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and not self.editor_interface.selected_index == i and self.dont_place_tiles_timer == 0:
                    # Make all the options menu for each button to be closed if a new button was chosen
                    for but in self.editor_interface.hotbar:
                        but.clicked = False
                    self.editor_interface.selected_index = i
                    self.dont_place_tiles_timer = 10
                # Press a second time
                elif but.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.editor_interface.selected_index == i and self.dont_place_tiles_timer == 0:
                    but.clicked = True
                    self.dont_place_tiles_timer = 10

            # Press the option button to change the element of a button
            for but in self.editor_interface.hotbar:
                if but.clicked:
                    for i, opt_rect in enumerate(but.options_rects):
                        if opt_rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                            but.button_index = i
                            self.dont_place_tiles_timer = 10
                            but.clicked = False

            if self.editor_interface.add_layer_button.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                self.tilemap.add_layer(self.layer_index)
                self.layer_index += 1
                self.dont_place_tiles_timer = 10
            if self.editor_interface.remove_layer_button.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                self.tilemap.delete_layer(self.layer_index)
                if self.layer_index != 0:
                    self.layer_index -=1
                self.dont_place_tiles_timer = 10
            if self.editor_interface.save_button.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                self.tilemap.save()
                self.dont_place_tiles_timer = 10
            if self.editor_interface.run_button.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                temp_level = Level(self.game, self.level_name)
                temp_level.run()
                self.left_click = False
                self.dont_place_tiles_timer = 10
            if self.editor_interface.collision_button_unpressed.rect.collidepoint(mouse_pos()[0], mouse_pos()[1]) and self.dont_place_tiles_timer == 0:
                self.tilemap.layer_list[self.layer_index]["collision"] = not self.tilemap.layer_list[self.layer_index]["collision"]
                self.dont_place_tiles_timer = 10



            # If the self.dont_place_timer is 0 it means none other buttons were pressed since we reset the time everytime on button press so put tile
            if self.dont_place_tiles_timer == 0:
                if self.ctrl_click:
                    self.tilemap.add_offgrid_element(self.current_element, mouse_pos(),self.layer_index)
                else:
                    self.tilemap.add_element_tile(self.current_element, self.grid_mouse_position,self.layer_index)
                for but in self.editor_interface.hotbar:
                    but.clicked = False

    def handle_right_click(self):
        if self.dont_place_tiles_timer == 0 and self.right_click: # maybe change the timer but it should be okay
            if self.ctrl_click:
                self.tilemap.delete_offgrid_element(mouse_pos(), self.scroll, self.layer_index)
            else:
                self.tilemap.delete_element_tile(self.grid_mouse_position, self.layer_index)
    
    def draw_grid_lines(self):
        self.grid_lines_surf.fill(ALPHA_COLOR)
        for x in range(int(self.scroll.x % self.game.tile_size), self.game.width, self.game.tile_size):
            pygame.draw.line(self.grid_lines_surf,"black",(x,0), (x,self.game.height))
        for y in range(int(self.scroll.y % self.game.tile_size), self.game.height, self.game.tile_size):
            pygame.draw.line(self.grid_lines_surf,"black",(0,y), (self.game.width,y))
        self.surface.blit(self.grid_lines_surf, (0,0))

    def draw_tile_highlight(self):
        current_block_img = self.current_element.surface.copy()
        current_block_img.set_alpha(128)
        if self.ctrl_click:
            self.surface.blit(current_block_img , mouse_pos())
        else:
            self.surface.blit(current_block_img , (self.grid_mouse_position[0] * self.game.tile_size + self.scroll.x, self.grid_mouse_position[1] * self.game.tile_size + self.scroll.y))

    def update_grid_mouse_pos(self):
        distance_to_origin = Vector2(mouse_pos()) - self.scroll
        if distance_to_origin.x > 0:
            x = int(distance_to_origin.x / self.game.tile_size)
        else:
            x = int(distance_to_origin.x / self.game.tile_size) - 1
        if distance_to_origin.y > 0:
            y = int(distance_to_origin.y / self.game.tile_size)
        else:
            y = int(distance_to_origin.y / self.game.tile_size) - 1
        self.grid_mouse_position = (x, y)
    
    def draw_tilemap(self):
        self.tilemap.surface.fill("lightblue")
        mult = 1
        for layer_index, layer in enumerate(self.tilemap.layer_list):
            # layer["surface"].fill(ALPHA_COLOR)
            self.tilemap.layer_surfaces[layer_index].fill(ALPHA_COLOR)
            for cord_keys in layer["grid"]:
                element_surface_list = self.game.static_assets[layer["grid"][cord_keys]["world_element_type"] + "/" + layer["grid"][cord_keys]["element"]]
                element_variance = layer["grid"][cord_keys]["variance"]
                element_pos = layer["grid"][cord_keys]["pos"]
                self.tilemap.layer_surfaces[layer_index].blit(element_surface_list[element_variance], (element_pos[0] * self.game.tile_size + self.scroll[0], element_pos[1] * self.game.tile_size + self.scroll[1]))
            for cord_keys in layer["off_grid"]:
                element_surface_list = self.game.static_assets[layer["off_grid"][cord_keys]["world_element_type"] + "/" + layer["off_grid"][cord_keys]["element"]]
                element_variance = layer["off_grid"][cord_keys]["variance"]
                element_pos = layer["off_grid"][cord_keys]["pos"]
                self.tilemap.layer_surfaces[layer_index].blit(element_surface_list[element_variance], (element_pos[0] + self.scroll[0], element_pos[1] + self.scroll[1]))
            layer_surface_copy = self.tilemap.layer_surfaces[layer_index].copy()
            if layer_index > self.layer_index:
                mult *= 2
            layer_surface_copy.set_alpha(255//mult)
            self.tilemap.surface.blit(layer_surface_copy, (0,0))

        self.surface.blit(self.tilemap.surface, (0,0))

    def handle_border(self):
        if self.border_click: # we are rendering a new border
            first_pos = (min(self.first_border_point[0], self.second_border_point[0]) * self.game.tile_size, min(self.first_border_point[1], self.second_border_point[1]) * self.game.tile_size)
            second_pos = (max(self.first_border_point[0], self.second_border_point[0]) * self.game.tile_size ,max(self.first_border_point[1], self.second_border_point[1]) * self.game.tile_size)
            self.border_rect = pygame.rect.Rect(first_pos[0],first_pos[1], abs(first_pos[0]-second_pos[0]), second_pos[1] - first_pos[1])

    def run(self):
        font = pygame.font.SysFont('Arial', 32)
        while True:
            # Update timers maybe function in the future
            self.dont_place_tiles_timer = max(self.dont_place_tiles_timer - 1, 0)
            # Check events
            if self.event_loop():
                return # Return to menu
            # Drag the screen
            self.handle_scroll()

            # Update borders
            if self.border_click:
                self.second_border_point = self.grid_mouse_position
            # Handle clicks
            self.handle_left_click()
            self.handle_right_click()
            
            # Handle border
            self.handle_border()

            # Auto fix tiles
            self.tilemap.tile_fix(self.layer_index)
            # Update Current Tile
            self.current_element = self.world_elements_matrix[self.editor_interface.selected_index][self.editor_interface.hotbar[self.editor_interface.selected_index].button_index]
            self.update_grid_mouse_pos()
            # Rendering and updating the screen with the map and the menu
            self.render(font)

    def render(self, font):
        # Render background
        self.surface.fill("lightblue")

        # Render tilemap
        self.draw_tilemap()

        # Render origin point
        pygame.draw.circle(self.surface, "red", self.scroll, 7)

        # Render tile in muse position
        self.draw_tile_highlight()

        # Render border rect
        rect_border_offset = self.border_rect.move(self.scroll[0], self.scroll[1])
        pygame.draw.rect(self.surface, "red", rect_border_offset, 1)

        # Render grid lines
        self.draw_grid_lines()

        # Making sure the map is within the added zoom ratio
        self.scaled_display = pygame.transform.scale_by(self.surface, self.scale_ratio)

        # Render editor interface onto the scaled_display
        self.editor_interface.render()


        # Rendering the finished scaled_display with the menu on top to the screen
        self.game.display.blit(self.scaled_display, (0,0))
        # Render debugging text
        # text = font.render(str(self.tilemap.layer_surfaces), True, "white", pygame.SRCALPHA)
        # text = font.render(str(self.scroll.x % self.game.tile_size) + "|" + str(self.grid_mouse_position) + "|" + str(self.scroll.x), True, "white", pygame.SRCALPHA)
        text = font.render(str(self.grid_mouse_position),True, "white", pygame.SRCALPHA)
        self.game.display.blit(text, (self.game.width - text.get_width(), 0))
        # Updating/refreshing the screen
        pygame.display.update()

    def load_world_elements_matrix(self):
        
        world_elements_path = "assets/world_elements"
        mat = []
        for  folder_type in list(reversed(os.listdir(world_elements_path))):
            element_list = []
            for folder_element in os.listdir(world_elements_path + "/" + folder_type):
                if not (folder_type == "entities" and folder_element == "player"):
                    element_path = world_elements_path + "/" + folder_type + "/" + folder_element
                    element_list.append(Element(folder_type, folder_element, element_path))
            mat.append(element_list)
        return mat


class Editor_interface:
    def __init__(self, game, editor) -> None:
        self.game = game
        self.editor = editor
        self.world_elements_path = "assets/world_elements"
        self.margin = 4
        self.hotbar = self.get_hotbar() # Holds all the button objects
        self.selected_index = 1
        self.add_layer_button, self.remove_layer_button, self.layer_text_rect, self.collision_button_unpressed, self.collision_button_pressed = self.get_modify_layer_buttons()
        self.save_button, self.run_button = self.get_control_buttons()
        self.font = pygame.font.SysFont("Arial", 16)
        self.surface = transparent_surface(self.game.display.get_size())

        self.layer_display_rect = pygame.rect.Rect(self.game.width - self.game.tile_size * 2 - self.margin * 4 - self.game.tile_size * 4,  self.game.height - self.game.tile_size * 2 - self.margin * 3, self.game.tile_size * 4, self.game.tile_size * 2 + self.margin * 2)
        # pygame.rect.Rect()

    def get_hotbar(self):
        hotbar_list = []
        for i, x in enumerate(range(self.margin, (self.game.tile_size * 2 + self.margin*2 ) * len(self.editor.world_elements_matrix), self.game.tile_size * 2 + self.margin *2)):
            rect = pygame.rect.Rect(x, self.margin, self.game.tile_size * 2, self.game.tile_size * 2)
            hotbar_list.append(Button(self.game, rect, self.editor.world_elements_matrix[i] , self.editor.world_elements_matrix[i][0].world_element_type))
        return hotbar_list

    def get_modify_layer_buttons(self):
        add = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size * 2 - self.margin * 2, self.game.height - self.game.tile_size - self.margin,self.game.tile_size,self.game.tile_size), pygame.image.load("assets/interface/editor/add_button.png").convert_alpha())
        remove = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size - self.margin, self.game.height - self.game.tile_size - self.margin,self.game.tile_size,self.game.tile_size), pygame.image.load("assets/interface/editor/remove_button.png").convert_alpha())
        text_box_rect = pygame.rect.Rect(self.game.width - self.game.tile_size * 2 - self.margin * 2, self.game.height - self.game.tile_size * 2 - self.margin * 3, self.game.tile_size * 2 + self.margin , self.game.tile_size)
        collison_un = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size - self.margin, self.game.height - self.game.tile_size * 3 - self.margin *4,self.game.tile_size,self.game.tile_size), pygame.image.load("assets/interface/editor/collision_button_un.png").convert_alpha())
        colllision_tru = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size - self.margin, self.game.height - self.game.tile_size * 3 - self.margin *4,self.game.tile_size,self.game.tile_size), pygame.image.load("assets/interface/editor/collision_button_tru.png").convert_alpha())
        return add , remove, text_box_rect, collison_un, colllision_tru
    
    def get_control_buttons(self):
        save = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size * 2 - self.margin * 2, self.game.tile_size + self.margin, self.game.tile_size, self.game.tile_size), pygame.image.load("assets/interface/editor/save_button.png").convert_alpha())
        run = Sprite(pygame.rect.Rect(self.game.width - self.game.tile_size - self.margin, self.game.tile_size + self.margin, self.game.tile_size, self.game.tile_size), pygame.image.load("assets/interface/editor/play_button.png").convert_alpha())
        return save, run

    def render(self):
        # Hotbar menu
        self.surface.fill(ALPHA_COLOR)
        for i, but in enumerate(self.hotbar):
            current_rect = but.rect.inflate(self.margin,self.margin)
            pygame.draw.rect(self.surface, (50,50,50), current_rect,0,self.margin)
            self.surface.blit(pygame.transform.scale(but.element_list[but.button_index].surface,(self.game.tile_size * 2,self.game.tile_size * 2)), but.rect)
            if i == self.selected_index:
                pygame.draw.rect(self.surface, "yellow", current_rect,self.margin//2,self.margin)
            if but.clicked:
                for i, elem in enumerate(but.element_list):
                    self.surface.blit(pygame.transform.scale(elem.surface,(self.game.tile_size * 2,self.game.tile_size * 2)), but.options_rects[i])

        # Layers
        text = self.font.render("layer " + str(self.editor.layer_index),True, "white")
        pygame.draw.rect(self.surface,"black", self.layer_text_rect, 0, 4)
        self.surface.blit(text, text.get_rect(center = self.layer_text_rect.center))
        self.surface.blit(self.add_layer_button.img, self.add_layer_button.rect)
        self.surface.blit(self.remove_layer_button.img, self.remove_layer_button.rect)
        self.surface.blit(self.save_button.img, self.save_button.rect)
        self.surface.blit(self.run_button.img, self.run_button.rect)
        if self.editor.tilemap.layer_list[self.editor.layer_index]["collision"]:
            self.surface.blit(self.collision_button_pressed.img,self.collision_button_pressed.rect)
        else: 
            self.surface.blit(self.collision_button_unpressed.img,self.collision_button_unpressed.rect)


        layer_display_surf = pygame.Surface((self.game.width // 10 , self.game.height // 10))
        layer_display_surf.fill((0,0,0))
        # source = pygame.transform.scale(self.editor.tilemap.layer_list[self.editor.layer_index]["surface"], (128,72))
        source = pygame.transform.scale(self.editor.tilemap.layer_surfaces[self.editor.layer_index], (128,72))

        source.set_alpha(255)
        layer_display_surf.blit(source, (0,0))
        self.surface.blit(layer_display_surf, self.layer_display_rect)
        pygame.draw.rect(self.surface, "white", self.layer_display_rect, 1)


        self.editor.scaled_display.blit(self.surface, (0,0))


class Button:
    def __init__(self, game, rect, elem_list, world_element_type) -> None:
        self.game = game
        self.rect = rect
        self.element_list = elem_list

        self.world_element_type = world_element_type

        self.button_index = self.handle_deafult_index()

        self.option_margin = 2
        self.options_rects = self.get_options_rects()

        self.clicked = False
    
    def handle_deafult_index(self):
        # the config for the deafult starter iconts
        index_dict = {"decor": 0, "entities": 1, "tiles": 0, "utils": 1}
        if self.world_element_type in index_dict:
            return index_dict[self.world_element_type]
        return 0
    
    def get_options_rects(self):
        opt_rect = []
        for y in range(self.rect.bottom + 2 + self.option_margin,self.rect.bottom + len(self.element_list) * (self.game.tile_size * 2 + self.option_margin * 2), self.game.tile_size * 2  + self.option_margin * 2):
            opt_rect.append(pygame.rect.Rect(self.rect.left, y, self.game.tile_size * 2,self.game.tile_size * 2))
        return opt_rect

        
class Element:
    def __init__(self, world_element_type, element , path) -> None:
        self.world_element_type = world_element_type
        self.element = element
        self.surface = pygame.image.load(path + "/icon/00.png")

    def __str__(self) -> str:
        return f"type: {self.world_element_type}, element: {self.element}"
    
    def __repr__(self) -> str:
        return f"|type: {self.world_element_type}, element: {self.element}|"
