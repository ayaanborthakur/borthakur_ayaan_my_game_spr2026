import pygame as pg
from state_machine import *

TILESIZE = 32
TILES_W = 40
TILES_H = 28
WIDTH = TILESIZE * TILES_W
HEIGHT = TILESIZE * TILES_H
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (150, 150, 150)
PLAYER_SPEED = 7
MOB_SPEED = 35
FPS = 60
SCORE = 0


def Dino_STATES(player):
    return [Running(False, player), Idle(True, player), Airborne(False, player)]


TITLE = "hello"
HEALTH = 100
MOB_ACCELERATION = 1.2
FRICTION = 4.0
ACCELERATION = 4.5
GRAVITY = 0.5
JUMP_SPEED = 20
# PLAYER_HIT_SIZE = pg.Rect(0, 0, TILESIZE, TILESIZE)
