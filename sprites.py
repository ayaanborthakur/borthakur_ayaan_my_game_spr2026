import pygame as pg
from pygame.sprite import Sprite
from settings import *
import math
from state_machine import *
from os import path
from utils import *

vec = pg.math.Vector2


EPSILON = 0  # sub-pixel gap to prevent sticking, but doesn't work


def swept_aabb_collide(sprite, group):
    """
    Swept AABB collision
    inflate walls by size of player
    check if vector of player drawn from player center hits the wall
    move to the hit position closest to the center

    """
    # sprite glitchs on left and top walls
    if sprite.vel.length_squared() == 0:
        return

    start = vec(sprite.pos)
    end = start + sprite.vel

    closest_t = 1.0  # fraction of velocity before first hit (1.0 = no hit)
    hit_normal = None

    for wall in group:

        inflated = wall.rect.inflate(sprite.rect.width, sprite.rect.height)

        if (
            inflated.left < start.x < inflated.right
            and inflated.top < start.y < inflated.bottom
        ):
            # Push out: find smallest penetration axis and resolve
            dx_left = start.x - inflated.left
            dx_right = inflated.right - start.x
            dy_top = start.y - inflated.top
            dy_bottom = inflated.bottom - start.y

            min_pen = min(dx_left, dx_right, dy_top, dy_bottom)
            if min_pen == dx_left:
                sprite.pos.x = inflated.left
                sprite.vel.x = min(sprite.vel.x, 0)
            elif min_pen == dx_right:
                sprite.pos.x = inflated.right
                sprite.vel.x = max(sprite.vel.x, 0)
            elif min_pen == dy_top:
                sprite.pos.y = inflated.top
                sprite.vel.y = min(sprite.vel.y, 0)
            elif min_pen == dy_bottom:
                sprite.pos.y = inflated.bottom
                sprite.vel.y = max(sprite.vel.y, 0)

            start = vec(sprite.pos)
            end = start + sprite.vel
            continue

        clipped = inflated.clipline(start, end)

        if clipped:
            hit_pt = vec(clipped[0])
            dist = (hit_pt - start).length()
            total = sprite.vel.length()
            if total > 0:
                t = dist / total
                if t < closest_t:
                    closest_t = t

                    # Determine collision normal from inflated rect edges
                    normal = vec(0, 0)
                    eps = 1.0  # tolerance for edge detection
                    if abs(hit_pt.x - inflated.left) < eps:
                        normal = vec(-1, 0)
                    elif abs(hit_pt.x - inflated.right) < eps:
                        normal = vec(1, 0)
                    elif abs(hit_pt.y - inflated.top) < eps:
                        normal = vec(0, -1)
                    elif abs(hit_pt.y - inflated.bottom) < eps:
                        normal = vec(0, 1)
                    hit_normal = normal

    if hit_normal is not None:
        # move to the collision point (epsilon commented out for now)
        # vel_len = sprite.vel.length()
        # if vel_len > 0:
        #     pull_t = EPSILON / vel_len
        #     adjusted_t = max(0, closest_t - pull_t)
        # else:
        #     adjusted_t = closest_t
        sprite.pos = start + sprite.vel * closest_t

        remaining = sprite.vel * (1.0 - closest_t)
        # ONLY apply slide if moving TOWARDS the wall (dot product < 0)
        if remaining.dot(hit_normal) < 0:
            slide = remaining - remaining.dot(hit_normal) * hit_normal
            sprite.vel = slide
        if hit_normal == vec(0,-1):
            sprite.state_machine.stateManage("airborne",False)
            print("airborne",False,sprite.pos.y)

        

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
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.last_update = 0
        self.current_frame = 0
        
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.camera = Camera(self, self.game)
        self.state_machine = StateMachine()
        self.state_machine.start_machine(Dino_STATES(self))

    def update(self):
        # get keys and check if character is even moving

        is_moving = self.get_keys()
        # applying acceleration to velocity and velocity to accel
        # eration
        try:

            self.accel = self.accel.normalize() * ACCELERATION

            self.vel.x += self.accel.x

            if abs(self.vel.x) >= PLAYER_SPEED:
                self.vel.x = PLAYER_SPEED * (1 if self.vel.x > 0 else -1)

        except:
            pass

        self.vel.y += GRAVITY

        # checking if its hitting anything else
        swept_aabb_collide(self, self.game.all_walls)
        self.pos += self.vel
        self.rect.center = self.pos

        if not is_moving:

            self.vel.x *= 0.75
            if abs(self.vel.x) <= 0.05:

                self.vel.x = 0

        self.state_machine.update()
        self.accel *= 0
        self.animate()

    def load_images(self):
        # loads images for the player
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

        if now - self.last_update > 75:
            self.last_update = now
            center = self.rect.center
            if self.state_machine.states["running"].active:
                self.current_frame = (self.current_frame + 1) % len(self.running_frames)
                self.image = self.running_frames[self.current_frame]
            elif self.state_machine.states["idle"].active:
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
        if keys[pg.K_w] and not self.state_machine.states["airborne"].active:
            print("jumped")
            self.state_machine.stateManage("airborne",True)

            self.vel.y = -JUMP_SPEED

        if keys[pg.K_a]:
            self.accel.x -= ACCELERATION
            value = True
        if keys[pg.K_d]:
            self.accel.x += ACCELERATION
            value = True
        return value


class Dino(Player):

    def __init__(self, game, x, y):
        Player.__init__(self, game, x, y)
    

class Alien(Player):

    def __init__(self, game, x, y):
        Player.__init__(self, game, x, y)

    def get_keys(self):
        # gets keys and stuff
        keys = pg.key.get_pressed()

        value = False
        if keys[pg.K_UP] and not self.state_machine.states["airborne"].active:
            self.vel.y = -JUMP_SPEED
            value = True
            self.state_machine.stateManage("airborne",True)
        if keys[pg.K_LEFT]:
            self.accel.x -= ACCELERATION
            value = True
        if keys[pg.K_RIGHT]:
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
        self.pos = vec(x, y)
        self.state_machine = StateMachine()
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        # calls movement toward player
        self.move(self.game.dino.pos)
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

        swept_aabb_collide(self, self.game.all_walls)
        self.pos += self.vel
        self.rect.center = self.pos

    # gets teh neccesrary accleration to get to the player
    def move(self, pos):

        self.accel = pos - self.pos


class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.blit(game.wall_img, (0, 0), (0, 0, TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)

        self.pos = vec(x+TILESIZE/2, y+TILESIZE/2)
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
        self.pos = vec(x+TILESIZE/2, y+TILESIZE/2)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos
