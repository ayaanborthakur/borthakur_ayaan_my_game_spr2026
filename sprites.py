import pygame as pg
from pygame.sprite import Sprite
from settings import *
import math

vec = pg.math.Vector2


def collide(one, two):
    return two.rect.clipline(one.vel_line)

def collide_walls(sprite, group):
    """
    returns stuff
    """
    
    hits = pg.sprite.spritecollide(sprite, group, False, collide)
    points = []
    for wall in hits:
        line = wall.rect.clipline(sprite.vel_line)
        points.append(line[0])
        points.append(line[1])
        
    if points != []:
        set_point = vec(points[0][0], points[0][1])
            
        for point in points:
            print("point is"+str(point))
            point = vec(point[0],point[1])
            old_point = point
            
            point = point - sprite.pos
            if point.magnitude() < sprite.vel.magnitude():
                set_point = old_point
        
        # offset by half the sprite's size along the velocity direction
        if sprite.vel.magnitude() > 0:
            direction = sprite.vel.normalize()
            extra = vec(direction.x * sprite.rect.width / 2, direction.y * sprite.rect.height / 2)
        else:
            extra = vec(0, 0)

        set_point = set_point - extra
        sprite.pos = set_point
        sprite.vel = vec(0,0)
class Player(Sprite):

    def __init__(self, game, x, y):
        # intializes neccesary values
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        # physics vectors for acceleration postion and velocity
        self.accel = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(300, 300)
        self.rect.center = self.pos
        self.hit_rect = pg.Rect(0, 0, 32, 32)
        self.vel_line = ((0,0),(0,0))
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        # get keys and check if character is even moving

        is_moving = self.get_keys()
        # applying acceleration to velocity and velocity to acceleration
        try:
            self.accel = self.accel.normalize() * ACCELERATION

            self.vel += self.accel
            if self.vel.magnitude() >= PLAYER_SPEED:

                self.vel = self.vel.normalize() * PLAYER_SPEED
            
            
             
        except:
            pass

        
        

        self.vel_line = ((self.pos.x,self.pos.y),(self.pos.x + self.vel.x,self.pos.y + self.vel.y))
        print("vel_line1"+str(self.vel_line))
        self.accel *= 0
        # applysing friciton if player is not actively trying to move
        

        # checking if its hitting anything else
        collide_walls(self,self.game.all_walls)
        self.pos += self.vel
        self.rect.center = self.pos
        if not is_moving:
            self.vel *= 0.89
            if self.vel.magnitude() <= 0.05:
                self.vel *= 0
            
            
    def get_keys(self):
        # gets keys and stuff
        keys = pg.key.get_pressed()

        value = False
        if keys[pg.K_w]:
            self.accel.y -= ACCELERATION
            value = True
        if keys[pg.K_a]:
            self.accel.x -= ACCELERATION
            value = True
        if keys[pg.K_s]:
            self.accel.y += ACCELERATION
            value = True
        if keys[pg.K_d]:
            self.accel.x += ACCELERATION
            value = True
        return value


class Mob(Sprite):
    # initialize the instance
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.accel = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(x * 32, y * 32)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        # calls movement toward player
        self.move(self.game.player.pos)
        # same as player
        try:

            if self.accel.magnitude() >= MOB_ACCELERATION:

                self.accel = self.accel.normalize() * MOB_ACCELERATION

            self.vel += self.accel
            if self.vel.magnitude() >= MOB_SPEED:

                self.vel = self.vel.normalize() * MOB_SPEED

            self.accel *= 0
            self.vel *= 0.95
        except:
            pass

        self.pos += self.vel
        self.rect.center = self.pos

    # gets teh neccesrary accleration to get to the player
    def move(self, pos):

        prevel = self.vel
        self.accel = pos - self.pos


class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)
        self.pos = vec(x * 32, y * 32)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos
