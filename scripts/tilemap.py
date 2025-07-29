import pygame, json
from scripts.utils import *

FIX1_TILES = ['dirt', 'castle_stone']
TILE_AROUND = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1), (0,0)]
TILE_NEIGHBOURS = {(0,-1) : "up",(1,0) : "right",(0,1): "down",(-1,0): "left"}
PHYSICS_TILES = ['dirt', 'mossy_stone','castle_stone', 'kill_tile', "victory_tile"]

class Tilemap:
    def __init__(self, game, name) -> None:
        self.game = game
        self.name = name
        self.layer_list,self.background_list,self.borders = self.load()
        # self.layer_list = []
        # self.layer_list.append({"collision": True, "visible": True, "off_grid" : {}, "grid": {}}) #, "surface": transparent_surface(self.game.display.get_size())})
        self.layer_surfaces = [transparent_surface(self.game.display.get_size()) for _ in self.layer_list]
        self.layer_index = 0

        # self.background_list = []
        self.background_index = 0

        self.surface =  transparent_surface((self.game.display.get_size()))

        # self.borders = {"top":0, "bottom": 0, "left": 0, "right": 0}

    def add_element_tile(self, element, pos, layer_index = 0):
        loc = str(pos[0]) + ";" + str(pos[1])
        self.layer_list[layer_index]["grid"][loc] = {"world_element_type": element.world_element_type, "element": element.element, "variance":0, "pos": pos}

    def add_offgrid_element(self, element, pos, layer_index = 0):
        loc = str(int(pos[0])) + ";" + str(int(pos[1]))
        self.layer_list[layer_index]["off_grid"][loc] = {"world_element_type": element.world_element_type, "element": element.element, "variance":0, "pos": pos}

    def delete_element_tile(self, pos, layer_index = 0):
        loc = str(pos[0]) + ";" + str(pos[1])
        if loc in self.layer_list[layer_index]["grid"]:
            del self.layer_list[layer_index]["grid"][loc]

    def delete_offgrid_element(self, pos, scroll, layer_index = 0):
        for tile in self.layer_list[layer_index]["off_grid"].copy().values():
            loc = str(tile["pos"][0]) + ";" + str(tile["pos"][1])
            offset_pos = (tile["pos"][0] + scroll[0], tile["pos"][1] + scroll[1])
            if self.game.static_assets[tile["world_element_type"] + "/" + tile["element"]][tile["variance"]].get_rect(topleft = offset_pos).collidepoint(pos):
                del self.layer_list[layer_index]["off_grid"][loc]
    def add_layer(self, layer_index):
        self.layer_list.insert(layer_index + 1, {"collision": True, "visible": True, "off_grid" : {}, "grid": {}}) #, "surface": transparent_surface(self.game.display.get_size())})
        self.layer_surfaces.insert(layer_index + 1, transparent_surface(self.game.display.get_size()))
    def delete_layer(self, layer_index):
        if layer_index != 0:
            del self.layer_list[layer_index]
            del self.layer_surfaces[layer_index]

    def update_border(self, border_rect):
        self.borders["top"] = int(border_rect.top // self.game.tile_size)
        self.borders["bottom"] = int(border_rect.bottom // self.game.tile_size)
        self.borders["left"] = int(border_rect.left // self.game.tile_size)
        self.borders["right"] = int(border_rect.right // self.game.tile_size)

    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.game.tile_size), int(pos[1] // self.game.tile_size))
        for offset in TILE_AROUND:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            for layer in self.layer_list:
                if check_loc in layer["grid"]:
                    tiles.append({"tile": layer["grid"][check_loc], "collision": layer["collision"]})
        return tiles
    
    def physics_rect_around(self, pos):
        tiles_att_list = self.tiles_around(pos)
        rects_with_elements = []
        for tile_attr in tiles_att_list:
            tile_pos = tile_attr["tile"]["pos"]
            if tile_attr["tile"]["element"] in PHYSICS_TILES and tile_attr["collision"]:
                rect = pygame.rect.Rect(tile_pos[0] * self.game.tile_size, tile_pos[1] * self.game.tile_size, self.game.tile_size, self.game.tile_size)
                element = tile_attr["tile"]["element"]
                rects_with_elements.append((rect, element))
        return rects_with_elements
    
    def solid_check(self, pos):
        tile_loc = (str(int(pos[0] // self.game.tile_size))+ ';' + str( int(pos[1] // self.game.tile_size)))
        # if tile_loc in self.grid:
        for layer in self.layer_list:
            if tile_loc in layer["grid"] and layer["grid"][tile_loc]["element"] in PHYSICS_TILES:
                return True

    def tile_fix(self, layer_index = 0):
        for tile in self.layer_list[layer_index]["grid"]:
            if self.layer_list[layer_index]["grid"][tile]["element"] in FIX1_TILES:
                # checking which blocks are next to the tile to calculate its variant
                tiles_next = {"right": False, "left": False, "up": False, "down": False}
                for tup in TILE_NEIGHBOURS:
                    neighbour_tile = str(self.layer_list[layer_index]["grid"][tile]["pos"][0] + tup[0]) + ";" + str(self.layer_list[layer_index]["grid"][tile]["pos"][1] + tup[1])
                    if neighbour_tile in self.layer_list[layer_index]["grid"] and self.layer_list[layer_index]["grid"][neighbour_tile]["element"] in FIX1_TILES:
                        tiles_next[TILE_NEIGHBOURS[tup]] = True
                
                if tiles_next["right"] and not tiles_next["left"] and not tiles_next["up"] and tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 0
                elif tiles_next["right"] and tiles_next["left"] and not tiles_next["up"] and tiles_next["down"]:
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 1
                elif not tiles_next["right"] and tiles_next["left"] and not tiles_next["up"] and tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 2
                elif tiles_next["right"] and not tiles_next["left"] and tiles_next["up"] and tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 3
                elif tiles_next["right"] and tiles_next["left"] and tiles_next["up"] and tiles_next["down"]:
                    directions_bool = {}
                    left_up = str(self.layer_list[layer_index]["grid"][tile]["pos"][0] - 1) + ";" + str(self.layer_list[layer_index]["grid"][tile]["pos"][1] - 1)
                    right_up = str(self.layer_list[layer_index]["grid"][tile]["pos"][0] + 1) + ";" + str(self.layer_list[layer_index]["grid"][tile]["pos"][1] - 1)
                    left_down = str(self.layer_list[layer_index]["grid"][tile]["pos"][0] - 1) + ";" + str(self.layer_list[layer_index]["grid"][tile]["pos"][1] + 1)
                    right_down = str(self.layer_list[layer_index]["grid"][tile]["pos"][0] + 1) + ";" + str(self.layer_list[layer_index]["grid"][tile]["pos"][1] + 1)
                    directions_bool["left_up"] = False
                    directions_bool["right_up"] = False
                    directions_bool["left_down"] = False
                    directions_bool["right_down"] = False
                    if left_up in self.layer_list[layer_index]["grid"]:
                        if self.layer_list[layer_index]["grid"][left_up]["element"] in FIX1_TILES:
                            directions_bool["left_up"] = True
                    if right_up in self.layer_list[layer_index]["grid"]:
                        if self.layer_list[layer_index]["grid"][right_up]["element"] in FIX1_TILES:
                            directions_bool["right_up"] = True
                    if left_down in self.layer_list[layer_index]["grid"]:
                        if self.layer_list[layer_index]["grid"][left_down]["element"] in FIX1_TILES:
                            directions_bool["left_down"] = True
                    if right_down in self.layer_list[layer_index]["grid"]:
                        if self.layer_list[layer_index]["grid"][right_down]["element"] in FIX1_TILES:
                            directions_bool["right_down"] = True

                    if directions_bool["left_up"] and not directions_bool["right_up"] and directions_bool["left_down"] and directions_bool["right_down"]:
                        self.layer_list[layer_index]["grid"][tile]["variance"] = 9
                    elif not directions_bool["left_up"] and directions_bool["right_up"] and directions_bool["left_down"] and directions_bool["right_down"]:
                        self.layer_list[layer_index]["grid"][tile]["variance"] = 10
                    elif directions_bool["left_up"] and directions_bool["right_up"] and directions_bool["left_down"] and not directions_bool["right_down"]:
                        self.layer_list[layer_index]["grid"][tile]["variance"] = 11
                    elif directions_bool["left_up"] and directions_bool["right_up"] and not directions_bool["left_down"] and directions_bool["right_down"]:
                        self.layer_list[layer_index]["grid"][tile]["variance"] = 12 
                    else:
                        self.layer_list[layer_index]["grid"][tile]["variance"] = 4  
                elif not tiles_next["right"] and tiles_next["left"] and tiles_next["up"] and tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 5
                elif tiles_next["right"] and not tiles_next["left"] and tiles_next["up"] and  not tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 6
                elif tiles_next["right"] and ["left"] and tiles_next["up"] and not tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 7
                elif not tiles_next["right"] and tiles_next["left"] and tiles_next["up"] and not tiles_next["down"]: 
                    self.layer_list[layer_index]["grid"][tile]["variance"] = 8

    def save(self):
        level_dict = {"layer_list": self.layer_list, "background_list": self.background_list, "borders": self.borders}
        file = open("levels/" + self.name, 'w')
        json.dump(level_dict, file)
        file.close()

    def load(self):
        try:
            file = open("levels/" + self.name, 'r')
            level_dict = json.load(file)
            file.close()
            return level_dict["layer_list"], level_dict["background_list"], level_dict["borders"]
        except FileNotFoundError:
            file = open("levels/" + "clean_level", 'r')
            level_dict = json.load(file)
            file.close()
            return level_dict["layer_list"], level_dict["background_list"], level_dict["borders"]


        




    
    






