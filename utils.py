from settings import *
import pygame as pg
import os.path as path

# Object or class
from pygame.sprite import Sprite

vec = pg.math.Vector2


class Map:
    def __init__(self, filename):
        # creates empty list for map data
        self.data = []
        # open a specific file and close with 'with'
        with open(filename, "rt") as f:
            for line in f:
                self.data.append(line.strip())
        # properties of Map that allow us to define length and width
        # also allows for
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.map_width = self.tilewidth * 32
        self.map_height = self.tileheight * 32


class Camera:
    def __init__(self, player, game):
        self.game = game
        self.player = player
        self.offset = vec(0, 0)
        self.center = vec(WIDTH / 4, HEIGHT / 2)

    def update(self):
        self.offset = self.player.pos - self.center

    def apply(self, sprite):
        return sprite.rect.move(-self.offset.x, -self.offset.y)


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image


# This class can be used to create a Cooldwon
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        self.time = time

    def start(self,time = None):
        if time == None:
            time = self.time
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # sets current time to
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time:
            return True
        return False
    def reset(self):
        self.start_time = 0


class HealthBar(Sprite):
    def __init__(self, sprite):
        self.sprite = sprite
        Sprite.__init__(self, self.sprite.game.all_sprites)

        self.update()

    def update(self):
        index = self.sprite.health
        percent = self.sprite.health / HEALTH

        index = int(index / 2)
        bar_surf = pg.Surface((index, 10))
        # 2. Fill it with color
        bar_surf.fill((int(255 * (1 - percent)), int(255 * (percent)), 50))

        # 3. Create the main image surface (the full 100-width bar)
        self.image = pg.Surface((100, 20))
        # 4. Fill it with a background color (optional, e.g., black)
        # self.image.fill((0, 0, 0))
        # 5. blit the health bar onto the main surface
        self.image.blit(bar_surf, (25 + 25 - index // 2, 5))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.sprite.pos.x, self.sprite.pos.y)
        self.rect.top = self.sprite.rect.bottom


# loads an image file and creates an image surface for blitting or drawing images on the surface
