import math
import random
import sys
import pygame as pg
from settings import *
from sprites import *
from os import path
from utils import *
from math import floor
import json


# overview - CONCISE AND INFORMATIVE
class Game:
    # initializes game instance
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        pg.display.set_caption("Chris Cozort's awesome game!!!!!")
        self.playing = True
        # instanciates a 15 millisecond cooldown that can be used
        self.cooldown = Cooldown(15)
        self.left_side = pg.Surface((WIDTH / 2, HEIGHT))
        self.right_side = pg.Surface((WIDTH / 2, HEIGHT))

    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, "spritesheets")
        self.wall_img = pg.image.load(
            path.join(self.img_dir, "wall_image.png")
        ).convert_alpha()
        self.coin_img = pg.image.load(
            path.join(self.img_dir, "coin.png")
        ).convert_alpha()
       

    def new(self):
        # creating all the sprites and mobs and walls
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        # self.all_mobs.add(Mob(self, 10, 10))

        self.load_map()

        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == "1":
        #             self.all_walls.add(Wall(self, col, row))
        #
        #         if tile == "c":
        #             self.all_coins.add(Coin(self, col, row))
        #     for col, tile in enumerate(tiles):
        #         if tile == "a":
        #             self.dino = Player1(self, col, row)
        #
        #         if tile == "b":
        #             self.alien = Alien(self, col, row)

    def load_map(self):
        map_path = path.join(self.game_dir, "maps", "main_map.json")
        with open(map_path, "r") as f:
            map_data = json.load(f)

        walls_layer = None
        sprites_layer = None
        for layer in map_data.get("layers", []):
            if layer["name"] == "walls":
                walls_layer = layer
            elif layer["name"] == "sprites":
                sprites_layer = layer

        if walls_layer:
            # Algorithm to find the farthest wall (max col and max row)
            max_col = -1
            max_row = -1
            for chunk in walls_layer.get("chunks", []):
                for i, tile in enumerate(chunk["data"]):
                    # non-zero means wall
                    if tile == 1:
                        col = chunk["x"] + (i % chunk["width"])
                        row = chunk["y"] + (i // chunk["width"])
                        max_col = max(max_col, col)
                        max_row = max(max_row, row)
            
            # Instantiate walls up to max_col and max_row
            for chunk in walls_layer.get("chunks", []):
                for i, tile in enumerate(chunk["data"]):
                    if tile == 1:
                        col = chunk["x"] + (i % chunk["width"])
                        row = chunk["y"] + (i // chunk["width"])
                        if col <= max_col and row <= max_row:
                            self.all_walls.add(Wall(self, col * TILESIZE, row * TILESIZE))

        if sprites_layer:
            for obj in sprites_layer.get("objects", []):
                
                grid_x = obj["x"]
                grid_y = obj["y"]
                
                if obj["type"] == "Player":
                    if obj["name"] == "player1":
                        self.dino = Dino(self, grid_x, grid_y)
                    elif obj["name"] == "player2":
                        self.alien = Alien(self, grid_x, grid_y)
                elif obj["type"] == "Mob":
                    self.all_mobs.add(Mob(self, grid_x, grid_y))
        
        # Failsafe if player 1 or 2 are missing in map JSON
        if not hasattr(self, 'dino'):
            self.dino = Dino(self, 10, 10)
        if not hasattr(self, 'alien'):
            self.alien = Alien(self, 12, 10)

    def run(self):
        # runs the game
        while self.playing == True:
            self.dt = self.clock.tick(FPS) / 1000

            self.events()
            self.update()
            self.draw()
        # if game loop ends quit pygame
        pg.quit()

    # manages keyboard and mouse events
    def events(self):
        for event in pg.event.get():
            if self.cooldown.ready() == True:
                self.cooldown.start()
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False

                    self.running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    pass
                if event.type == pg.MOUSEMOTION:
                    pass

    def update(self):

        self.all_sprites.update()

    # not used anymore
    def draw_text(self, surface, text, size, color, x, y):
        font_name = pg.font.match_font("arial")
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)

    # draws all sprites

    def draw(self):
        self.screen.fill(WHITE)
        
        self.left_side.fill(WHITE)
        self.right_side.fill(WHITE)
        self.dino.camera.update()
        self.alien.camera.update()
        for sprite in self.all_sprites:
            self.left_side.blit(sprite.image, self.dino.camera.apply(sprite))
            self.right_side.blit(sprite.image, self.alien.camera.apply(sprite))
        self.screen.blit(self.left_side, (0, 0))
        self.screen.blit(self.right_side, (WIDTH / 2, 0))
        pg.display.flip()


if __name__ == "__main__":
    #    creating an instance or instantiating the Game class
    g = Game()
    g.new()
    g.run()
