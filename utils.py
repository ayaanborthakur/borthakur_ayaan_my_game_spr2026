from settings import *
import pygame as pg
import os.path as path

# Object or class
from pygame.sprite import Sprite

vec = pg.math.Vector2


#map class
class Map:
    #function for map initialization
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


#camera class
class Camera:
    #function for camera initialization
    def __init__(self, player, game):
        self.game = game
        self.player = player
        self.offset = vec(0, 0)
        self.center = vec(WIDTH / 4, HEIGHT / 2)

    #function for camera update: rigidly tracks player horizontally while applying a vertical deadzone buffer to prevent jerking during small jumps
    def update(self):
        # rigidly follow on X axis
        self.offset.x = self.player.pos.x - self.center.x

        # apply a Deadzone on the Y axis so the camera doesn't pan vertically for small jumps!
        current_y_focus = self.offset.y + self.center.y
        dist_y = self.player.pos.y - current_y_focus

        if dist_y > 100:
            self.offset.y += dist_y - 100
        elif dist_y < -100:
            self.offset.y += dist_y + 100

    #function to apply camera offset
    def apply(self, sprite):
        return sprite.rect.move(-self.offset.x, -self.offset.y)


#spritesheet class
class Spritesheet:
    #function for spritesheet initialization
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    #function to get image from spritesheet
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image
        return image


# This class can be used to create a Cooldwon
#cooldown class
class Cooldown:
    #function for cooldown initialization
    def __init__(self, time):
        self.start_time = 0
        self.time = time
        self.current_time = None

    #function to start cooldown
    def start(self, time=None):
        if time is not None:
            self.time = time
        self.start_time = pg.time.get_ticks()

    #function to check if cooldown is ready
    def ready(self):
        # sets current time to
        self.current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if self.current_time - self.start_time >= self.time:
            return True
        return False

    #function to reset cooldown
    def reset(self):
        self.start_time = 0


#health bar class
class HealthBar(Sprite):
    #function for health bar initialization
    def __init__(self, sprite):
        self.sprite = sprite
        Sprite.__init__(self, self.sprite.game.all_sprites)
        self.prevhealth = sprite.health

        self.width = 50
        self.update()

    #function for health bar update: calculates smooth health percentage and scales colored surface width to represent remaining health
    def update(self):
        health = int((self.prevhealth + self.sprite.health) / 2)
        self.prevhealth = health
        max_health = getattr(self.sprite, 'max_health', HEALTH)
        percent = health / max_health
        percent = max(0.0, min(1.0, percent))

        index = max(0, int(percent * self.width))
        if index == 0:
            index = 1
        bar_surf = pg.Surface((index, 10))
        # 2. Fill it with color
        bar_surf.fill((int(255 * (1 - percent)), int(255 * (percent)), 10))

        # 3. Create the main image surface (the full 100-width bar)
        self.image = pg.Surface((54, 14))
        # 4. Fill it with a background color (optional, e.g., black)
        # self.image.fill((0, 0, 0))
        # 5. blit the health bar onto the main surface

        self.image.blit(bar_surf, (2, 2))
        pg.draw.rect(self.image, (1, 1, 1), (0, 0, 54, 14), 2, 3)

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (self.sprite.pos.x, self.sprite.pos.y)
        self.rect.bottom = self.sprite.rect.top - 10


#player health bar class
class PlayerHealthBar(Sprite):
    #function for player health bar initialization
    def __init__(self, player):
        self.player = player
        self.prevhealth = player.health
        self.pos = vec(0, 0)
        self.update()

    #function for player health bar update: calculates smooth health percentage and scales colored surface width to represent remaining health
    def update(self):

        health = int((self.prevhealth + self.player.health) / 2)

        self.prevhealth = health

        max_health = getattr(self.player, 'max_health', HEALTH)
        percent = health / max_health
        percent = max(0.0, min(1.0, percent))

        index = max(0, int(health * 1.5))

        if index == 0:

            bar_surf = pg.Surface((1, 20))
            bar_surf.fill((255, 255, 255))
            # 2. Fill it with color

        else:
            bar_surf = pg.Surface((index, 20))

            # 2. Fill it with color
            bar_surf.fill((int(255 * (1 - percent)), int(255 * (percent)), 10))

        # 3. Create the main image surface (the full 100-width bar)
        self.image = pg.Surface((153, 23))
        self.image.fill((255, 255, 255))
        if index != 0:
            pg.draw.rect(self.image, (0, 0, 0), (3, 3, index, 20))
        # 4. Fill it with a background color (optional, e.g., black)
        # self.image.fill((0, 0, 0))
        # 5. blit the health bar onto the main surface
        self.image.blit(bar_surf, (0, 0))

        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.pos.x = 20
        self.pos.y = 20


# loads an image file and creates an image surface for blitting or drawing images on the surface
