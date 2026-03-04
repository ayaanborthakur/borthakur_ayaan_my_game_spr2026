import pygame as pg
from pygame.sprite import Sprite
from settings import *
import math

from os import path
from utils import *

vec = pg.math.Vector2


def collide(one, two):
    return two.rect.clipline(one.vel_line)


# WORK IN THIS ONE
def collide_walls_new(sprite, group):
    """
    Checks collision using vel lines from each corner of the sprite.
    Each corner gets its own vel line (corner -> corner + vel).
    If a corner's line hits a wall, that corner should stop at the hit point.
    """

    # dictionary with the corner position as the key and the vel line from that corner as the value
    corners = {
        "topright": vec(sprite.rect.topright),
        "topleft": vec(sprite.rect.topleft),
        "bottomright": vec(sprite.rect.bottomright),
        "bottomleft": vec(sprite.rect.bottomleft),
    }

    vel_lines = {}
    for name, corner in corners.items():
        # only include "leading" corners - those on the side the sprite is moving toward
        corner_from_center = corner - sprite.pos
        if corner_from_center.dot(sprite.vel) > 0:
            line_start = (corner.x, corner.y)
            line_end = (corner.x + sprite.vel.x, corner.y + sprite.vel.y)
            vel_lines[name] = (line_start, line_end)

    # dictionary: corner name -> (closest hit point, wall that was hit)
    points = {}
    for name, line in vel_lines.items():
        corner = corners[name]
        for wall in group:
            clipped = wall.rect.clipline(line)
            if clipped:
                for pt in clipped:
                    p = vec(pt[0], pt[1])
                    dist = (p - corner).magnitude()
                    # keep the closest point for this corner
                    if (
                        name not in points
                        or dist < (vec(points[name][0]) - corner).magnitude()
                    ):
                        points[name] = (pt, wall)

    if points:
        # find which corner hit is closest to its starting position (i.e. first impact)
        best_name = None
        best_dist = float("inf")

        for name, (pt, wall) in points.items():
            corner = corners[name]
            p = vec(pt[0], pt[1])
            dist = (p - corner).magnitude()
            if dist < best_dist:
                best_dist = dist
                best_name = name

        # set the relevant corner to be the hit point
        best_pt, best_wall = points[best_name]
        hit_point = vec(best_pt[0], best_pt[1])
        corner_offset = (
            corners[best_name] - sprite.pos
        )  # vector from center to that corner
        sprite.pos = hit_point - corner_offset
        # only check the wall that was actually hit
        if "x" in check_side_collision(hit_point, best_wall):
            sprite.vel.x = 0
        if "y" in check_side_collision(hit_point, best_wall):
            sprite.vel.y = 0
        sprite.vel = vec(0, 0)


def check_side_collision(hit_point, wall):
    # find which edge of the wall the hit point is closest to
    dist_left = abs(hit_point.x - wall.rect.left)
    dist_right = abs(hit_point.x - wall.rect.right)
    dist_top = abs(hit_point.y - wall.rect.top)
    dist_bottom = abs(hit_point.y - wall.rect.bottom)

    min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
    return_val = []
    # closest to left or right edge = x axis collision
    if min_dist == dist_left or min_dist == dist_right:
        return_val.append("x")
    # closest to top or bottom edge = y axis collision
    if min_dist == dist_top or min_dist == dist_bottom:
        return_val.append("y")
    return return_val


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
            print("point is" + str(point))
            point = vec(point[0], point[1])
            old_point = point

            point = point - sprite.pos
            if point.magnitude() < sprite.vel.magnitude():
                set_point = old_point

        extra = sprite.edge_offset

        set_point = set_point - extra
        sprite.pos = set_point
        sprite.vel = vec(0, 0)


class Player(Sprite):

    def __init__(self, game, x, y):
        # intializes neccesary values
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        # physics vectors for acceleration postion and velocity
        self.accel = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        self.rect.center = self.pos
        self.hit_rect = pg.Rect(0, 0, 32, 32)
        self.vel_line = ((0, 0), (0, 0))
        self.last_update = 0
        self.current_frame = 0
        self.states = []
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()

    def update(self):
        # get keys and check if character is even moving
        self.states = []
        is_moving = self.get_keys()
        # applying acceleration to velocity and velocity to acceleration
        try:
            self.accel = self.accel.normalize() * ACCELERATION

            self.vel += self.accel
            if self.vel.magnitude() >= PLAYER_SPEED:

                self.vel = self.vel.normalize() * PLAYER_SPEED

        except:
            pass

        # vel_line is only needed for the broad-phase collide check in spritecollide
        # self.vel_line = ((self.pos.x, self.pos.y),(self.pos.x + self.vel.x, self.pos.y + self.vel.y))
        # edge_offset and clipline-based vel_line no longer needed with collide_walls_new
        # if self.vel.magnitude() > 0:
        #     far_end = (self.pos.x + self.vel.x * 100, self.pos.y + self.vel.y * 100)
        #     clipped = self.rect.clipline((self.pos.x, self.pos.y), far_end)
        #     if clipped:
        #         edge_point = clipped[1]
        #         self.edge_offset = vec(edge_point[0] - self.pos.x, edge_point[1] - self.pos.y)
        #         self.vel_line = (edge_point, (edge_point[0] + self.vel.x, edge_point[1] + self.vel.y))
        #     else:
        #         self.edge_offset = vec(0, 0)
        #         self.vel_line = ((self.pos.x, self.pos.y),(self.pos.x + self.vel.x, self.pos.y + self.vel.y))
        # else:
        #     self.edge_offset = vec(0, 0)
        #     self.vel_line = ((self.pos.x, self.pos.y),(self.pos.x, self.pos.y))
        # print("vel_line1"+str(self.vel_line))
        self.accel *= 0
        # applysing friciton if player is not actively trying to move

        # checking if its hitting anything else
        collide_walls_new(self, self.game.all_walls)
        self.pos += self.vel
        self.rect.center = self.pos

        if not is_moving:
            self.states.append("slowing")
            self.vel *= 0.75
            if self.vel.magnitude() <= 0.05:
                self.states.append("standing")
                self.vel *= 0
        else:
            self.states.append("running")

        self.animate()

    def load_images(self):
        self.standing_frames = [
            self.spritesheet.get_image(0, 0, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE, 0, TILESIZE, TILESIZE),
        ]
        self.running_frames = [
            self.spritesheet.get_image(0, TILESIZE, TILESIZE, TILESIZE),
            self.spritesheet.get_image(TILESIZE, TILESIZE, TILESIZE, TILESIZE),
        ]
        # for frame in self.frames:
        #    frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks()

        if now - self.last_update > 35:
            self.last_update = now
            center = self.rect.center
            if "running" in self.states:
                self.current_frame = (self.current_frame + 1) % len(self.running_frames)
                self.image = self.running_frames[self.current_frame]
            else:
                self.current_frame = (self.current_frame + 1) % len(
                    self.standing_frames
                )
                self.image = self.standing_frames[self.current_frame]

            self.rect = self.image.get_rect()
            self.rect.center = center

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
        self.image = pg.Surface((TILESIZE, TILESIZE))
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

        collide_walls_new(self, self.game.all_walls)
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
        self.image = game.wall_img

        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)
        self.pos = vec((x * 32) + 16, (y * 32) + 16)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos


class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.coin_img

        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)
        self.pos = vec((x * 32) + 16, (y * 32) + 16)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos
