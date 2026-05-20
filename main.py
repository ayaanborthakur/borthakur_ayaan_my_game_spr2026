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
#game class
class Game:
    # initializes game instance
    #function for game initialization
    def __init__(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))

        pg.display.set_caption("Dino vs Alien")
        self.playing = True
        # instanciates a 15 millisecond cooldown that can be used
        self.cooldown = Cooldown(15)
        self.left_side = pg.Surface((WIDTH / 2, HEIGHT))
        self.right_side = pg.Surface((WIDTH / 2, HEIGHT))
        self.stat_font = pg.font.SysFont("arial", 16)

    #function to load game data
    def load_data(self):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, "spritesheets")
        self.wall_img = pg.image.load(
            path.join(self.img_dir, "wall_image.png")
        ).convert_alpha()
        self.coin_img = pg.image.load(
            path.join(self.img_dir, "coin.png")
        ).convert_alpha()
        
        # Pre-load and scale the background image
        bg_image = pg.image.load(path.join(self.img_dir, "jungle.png")).convert_alpha()
        self.bg_image_scaled = pg.transform.scale(bg_image, (WIDTH/2, HEIGHT))

    #function for new game setup
    def new(self):
        # creating all the sprites and mobs and walls
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_coins = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_players = pg.sprite.Group()
        self.all_attacks = pg.sprite.Group()
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

    #function to load map: parses tiled json map data to instantiate walls within map bounds and spawn players and mobs with custom properties
    def load_map(self):
        map_path = path.join(self.game_dir, "maps", "main_map.json")
        with open(map_path, "r") as f:
            map_data = json.load(f)

        tile_layer = None
        object_layer = None
        for layer in map_data.get("layers", []):
            if layer["type"] == "tilelayer":
                tile_layer = layer
            elif layer["type"] == "objectgroup":
                object_layer = layer

        # Load walls from tile layer
        if tile_layer:
            map_w = tile_layer["width"]
            data = tile_layer.get("data", [])
            for i, tile in enumerate(data):
                if tile != 0:  # any non-zero tile is a wall
                    col = i % map_w
                    row = i // map_w
                    self.all_walls.add(
                        Wall(self, col * TILESIZE, row * TILESIZE)
                    )

        # Load objects (players, mobs, coins)
        if object_layer:
            # Load players first so mobs can reference them
            for obj in object_layer.get("objects", []):
                if obj["type"] == "Dino":
                    self.dino = Dino(self, obj["x"], obj["y"])
                    self.all_players.add(self.dino)
                elif obj["type"] == "Alien":
                    self.alien = Alien(self, obj["x"], obj["y"])
                    self.all_players.add(self.alien)

            # Then load mobs with custom properties
            for obj in object_layer.get("objects", []):
                if obj["type"] == "Mob":
                    mob_props = {}
                    for prop in obj.get("properties", []):
                        mob_props[prop["name"]] = prop["value"]
                    self.all_mobs.add(Mob(self, obj["x"], obj["y"], self.dino, **mob_props))
                elif obj["type"] == "Coin":
                    Coin(self, obj["x"], obj["y"])

        if not hasattr(self, "dino"):
            self.dino = Dino(self, 10, 10)
        if not hasattr(self, "alien"):
            self.alien = Alien(self, 12, 10)

    #function to run game loop
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
    #function to handle events
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

    #function to update game state
    def update(self):

        self.all_sprites.update()
        
        # check coin collisions
        for player in self.all_players:
            hits = pg.sprite.spritecollide(player, self.all_coins, True)
            for coin in hits:
                player.health = min(getattr(player, 'max_health', 100), player.health + 10)

        if hasattr(self, "dino"):
            self.dino.healthbar.update()
        if hasattr(self, "alien"):
            self.alien.healthbar.update()

    #function to draw text
    def draw_text(self, surface, text, size, color, x, y):
        font_name = pg.font.match_font("arial")
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)

    def show_start_screen(self):
        self.screen.fill(WHITE)
        self.draw_text(self.screen, "Dino vs Alien", 64, BLACK, WIDTH / 2, HEIGHT / 6)
        self.draw_text(self.screen, "Goal: Defeat your opponent!", 32, BLACK, WIDTH / 2, HEIGHT / 4 + 20)
        
        self.draw_text(self.screen, "Dino Controls:", 28, BLACK, WIDTH / 4, HEIGHT / 2 - 50)
        self.draw_text(self.screen, "Move: A / D", 24, BLACK, WIDTH / 4, HEIGHT / 2 - 10)
        self.draw_text(self.screen, "Jump: W", 24, BLACK, WIDTH / 4, HEIGHT / 2 + 20)
        self.draw_text(self.screen, "Dash: S", 24, BLACK, WIDTH / 4, HEIGHT / 2 + 50)
        self.draw_text(self.screen, "Melee: LSHIFT", 24, BLACK, WIDTH / 4, HEIGHT / 2 + 80)
        self.draw_text(self.screen, "Ranged: LALT", 24, BLACK, WIDTH / 4, HEIGHT / 2 + 110)

        self.draw_text(self.screen, "Alien Controls:", 28, BLACK, WIDTH * 3 / 4, HEIGHT / 2 - 50)
        self.draw_text(self.screen, "Move: L / '", 24, BLACK, WIDTH * 3 / 4, HEIGHT / 2 - 10)
        self.draw_text(self.screen, "Jump: P", 24, BLACK, WIDTH * 3 / 4, HEIGHT / 2 + 20)
        self.draw_text(self.screen, "Dash: ;", 24, BLACK, WIDTH * 3 / 4, HEIGHT / 2 + 50)
        self.draw_text(self.screen, "Melee: RSHIFT", 24, BLACK, WIDTH * 3 / 4, HEIGHT / 2 + 80)
        self.draw_text(self.screen, "Ranged: RALT", 24, BLACK, WIDTH * 3 / 4, HEIGHT / 2 + 110)

        self.draw_text(self.screen, "Press ANY KEY to start", 32, BLACK, WIDTH / 2, HEIGHT * 5 / 6)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.playing = False
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYUP:
                    waiting = False

    # draws all sprites
    #function to draw game screen: updates split screen cameras, performs viewport culling for left and right surfaces, and renders all visible sprites
    def draw(self):
        self.screen.fill(WHITE)

        self.left_side.fill(WHITE)
        self.left_side.blit(self.bg_image_scaled, (0, 0))
        self.right_side.fill(WHITE)
        self.right_side.blit(self.bg_image_scaled, (0, 0))
        self.dino.camera.update()
        self.alien.camera.update()
        left_rect = self.left_side.get_rect()
        right_rect = self.right_side.get_rect()
        
        for sprite in self.all_sprites:
            # left side culling
            left_pos = self.dino.camera.apply(sprite)
            if left_pos.colliderect(left_rect):
                self.left_side.blit(sprite.image, left_pos)
            
            # right side culling
            right_pos = self.alien.camera.apply(sprite)
            if right_pos.colliderect(right_rect):
                self.right_side.blit(sprite.image, right_pos)

        # Draw borders ONCE and correctly sized after all sprites are blitted
        pg.draw.rect(self.left_side, BLACK, (0, 0, (WIDTH / 2)+5, HEIGHT), width=10)
        pg.draw.rect(self.right_side, BLACK, (-5, 0, (WIDTH / 2)+5, HEIGHT), width=10)
        self.left_side.blit(self.dino.healthbar.image, (self.dino.healthbar.pos.x,self.dino.healthbar.pos.y))
        
        # Display Dino stats
        dino_mods = self.dino.state_machine.base_modifiers
        dino_text = f"Spd: {dino_mods.get('speed', 1.0):.2f} | Jmp: {dino_mods.get('jump', 1.0):.2f} | Dsh: {dino_mods.get('dash', 1.0):.2f} | Atk: {dino_mods.get('attack', 1.0):.2f}"
        dino_surf = self.stat_font.render(dino_text, True, BLACK)
        self.left_side.blit(dino_surf, (self.dino.healthbar.pos.x, self.dino.healthbar.pos.y + 25))
        
        self.right_side.blit(self.alien.healthbar.image, (self.alien.healthbar.pos.x,self.alien.healthbar.pos.y))
        
        # Display Alien stats
        alien_mods = self.alien.state_machine.base_modifiers
        alien_text = f"Spd: {alien_mods.get('speed', 1.0):.2f} | Jmp: {alien_mods.get('jump', 1.0):.2f} | Dsh: {alien_mods.get('dash', 1.0):.2f} | Atk: {alien_mods.get('attack', 1.0):.2f}"
        alien_surf = self.stat_font.render(alien_text, True, BLACK)
        self.right_side.blit(alien_surf, (self.alien.healthbar.pos.x, self.alien.healthbar.pos.y + 25))
        
        self.screen.blit(self.left_side, (0, 0))
        self.screen.blit(self.right_side, (WIDTH / 2, 0))
        pg.display.flip()


if __name__ == "__main__":
    #    creating an instance or instantiating the Game class
    g = Game()
    g.show_start_screen()
    g.new()
    g.run()
