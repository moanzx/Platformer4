import pygame, sys, os, json
from scripts.editor import Editor
from scripts.level import Level
from scripts.menu import Menu
# import ez_profile


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.width = 1280
        self.height = 720
        self.display = pygame.display.set_mode((self.width,self.height))
        self.tile_size = 32
        self.clock = pygame.time.Clock()
        self.entities_assets = {}
        self.animations_speed_dict = {}
        self.draw_offset_dict = {}
        self.load_entities_assets()

        self.static_assets = {}
        self.load_static_assets()

        

    def load_entities_assets(self):
        path_entities = "assets/world_elements/entities"
        for folder_element in os.listdir(path_entities):
            path_element = path_entities + "/" + folder_element
            for status_element in os.listdir(path_element):
                if status_element == "config":
                    self.load_entity_configs(path_element + "/" + status_element, folder_element)
                    # print(folder_element)
                else:
                    self.entities_assets[folder_element + "/" + status_element] = self.load_images(path_element + "/" + status_element)

    def load_entity_configs(self, path, entity_name):
        file = open(path, 'r')
        data_dict = json.load(file)
        # print(data_dict)
        # d = {}
        for key, value in data_dict.items():
            # print(key,value)
            if key == "draw_offset":
                pass
            else:
                self.animations_speed_dict[entity_name + "/" + key] = value


    def load_static_assets(self):
        path_world_elements = "assets/world_elements"
        for folder_type in os.listdir(path_world_elements):
            path_element = path_world_elements + "/" + folder_type
            for folder_element in os.listdir(path_element):
                full_path = path_element + "/" + folder_element
                if folder_type == "tiles":
                    self.static_assets[folder_type + "/" + folder_element] = self.load_images(full_path, True)
                else: # if not tile, load icon folder may change later if we want to animate decor
                    self.static_assets[folder_type + "/" + folder_element] = self.load_images(full_path + "/" + "icon")


    def run(self):
        while True:
            # Show main menu
            menu = Menu(self)
            result = menu.run()
            
            if result == "exit":
                break
            elif isinstance(result, tuple):
                mode, level_name = result
                if mode == "editor":
                    editor = Editor(self, level_name)
                    editor.run()
                elif mode == "game":
                    level = Level(self, level_name)
                    level.run()
            elif result == "play":
                # Handle play action (this will be updated when we add level selection)
                level = Level(self, "level1")
                level.run()


    def load_images(self,path, is_tile = False):
        images = []
        for img_name in sorted(os.listdir(path)):
            if not (is_tile and img_name == "icon"):
                images.append(pygame.image.load(path + "/" + img_name).convert_alpha())
        return images

game = Game()
game.run()