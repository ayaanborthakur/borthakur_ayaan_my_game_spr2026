from settings import *
import pygame as pg

# Object or class


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

    def start(self):
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # sets current time to
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time:
            return True
        return False


# loads an image file and creates an image surface for blitting or drawing images on the surface


class Camera:

    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Move an entity's rect by the camera offset
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Center the camera on target
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # Limit scrolling to map boundaries
        x = min(0, x)  # left
        x = max(-(self.width - WIDTH), x)  # right
        y = min(0, y)  # top
        y = max(-(self.height - HEIGHT), y)  # bottom

        self.camera = pg.Rect(x, y, self.width, self.height)
