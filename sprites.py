import pygame as pg
from pygame.sprite import Sprite
from settings import *
import math
from state_machine import *
from os import path
from utils import *

vec = pg.math.Vector2


SKIN_WIDTH = 0.001  # tiny gap that prevents flush floating-point sticking
# saw this online so i tried it. apperantly it makes sure when there are multiple collisons
# like a corner, multiple iterations are gooder
MAX_SWEEP_ITERATIONS = 3


def sweep_single(pos, velocity, sprite_rect, wall_rect):
    """
    eaycast the sprite center point along velocity against the mickey mouse walls


    """
    # nuild the minkowski "mickey mouse"-inflated AABB
    half_w = sprite_rect.width / 2.0
    half_h = sprite_rect.height / 2.0

    mn_left = wall_rect.left - half_w
    mn_right = wall_rect.right + half_w
    mn_top = wall_rect.top - half_h
    mn_bottom = wall_rect.bottom + half_h

    INF = float("inf")

    # ── X axis ──
    if velocity.x == 0:
        if pos.x <= mn_left or pos.x >= mn_right:
            return 1.0, None
        tx_near = -INF
        tx_far = INF
    else:
        tx_near = (mn_left - pos.x) / velocity.x
        tx_far = (mn_right - pos.x) / velocity.x
        if tx_near > tx_far:
            tx_near, tx_far = tx_far, tx_near

    if velocity.y == 0:
        if pos.y <= mn_top or pos.y >= mn_bottom:
            return 1.0, None
        ty_near = -INF
        ty_far = INF
    else:
        ty_near = (mn_top - pos.y) / velocity.y
        ty_far = (mn_bottom - pos.y) / velocity.y
        if ty_near > ty_far:
            ty_near, ty_far = ty_far, ty_near

    if tx_near > ty_far or ty_near > tx_far:
        return 1.0, None

    t_near = max(tx_near, ty_near)
    t_far = min(tx_far, ty_far)

    if t_near >= 1.0 or t_far <= 0:
        return 1.0, None

    toi = max(t_near, 0.0)

    if tx_near > ty_near:
        normal = vec(-1, 0) if velocity.x > 0 else vec(1, 0)
    elif ty_near > tx_near:
        normal = vec(0, -1) if velocity.y > 0 else vec(0, 1)
    else:
        if abs(velocity.x) > abs(velocity.y):
            normal = vec(-1, 0) if velocity.x > 0 else vec(1, 0)
        else:
            normal = vec(0, -1) if velocity.y > 0 else vec(0, 1)

    return toi, normal


"""
100% ai made function, was just for testing. not used in the code.
"""


def _resolve_overlaps(sprite, group):
    """
    Discrete overlap check (SAT-lite for AABBs).
    If the sprite is already inside any wall, push it out along the
    shortest penetration axis *before* sweeping.
    """
    half_w = sprite.rect.width / 2.0
    half_h = sprite.rect.height / 2.0

    for wall in group:
        # Build Minkowski-inflated rect (same as in sweep_single)
        mn_left = wall.rect.left - half_w
        mn_right = wall.rect.right + half_w
        mn_top = wall.rect.top - half_h
        mn_bottom = wall.rect.bottom + half_h

        # Is the sprite center inside the inflated box?
        if not (
            mn_left < sprite.pos.x < mn_right and mn_top < sprite.pos.y < mn_bottom
        ):
            continue

        # Compute penetration depths on each side
        pen_left = sprite.pos.x - mn_left
        pen_right = mn_right - sprite.pos.x
        pen_top = sprite.pos.y - mn_top
        pen_bottom = mn_bottom - sprite.pos.y

        min_pen = min(pen_left, pen_right, pen_top, pen_bottom)

        if min_pen == pen_left:
            sprite.pos.x = mn_left - SKIN_WIDTH
            sprite.vel.x = min(sprite.vel.x, 0)
        elif min_pen == pen_right:
            sprite.pos.x = mn_right + SKIN_WIDTH
            sprite.vel.x = max(sprite.vel.x, 0)
        elif min_pen == pen_top:
            sprite.pos.y = mn_top - SKIN_WIDTH
            sprite.vel.y = min(sprite.vel.y, 0)
            # Landing on a floor
            if hasattr(sprite, "state_machine"):
                sprite.state_machine.stateManage("airborne", False)
        elif min_pen == pen_bottom:
            sprite.pos.y = mn_bottom + SKIN_WIDTH
            sprite.vel.y = max(sprite.vel.y, 0)


def swept_aabb_collide(sprite, group):
    """
    Full swept AABB collision: resolves overlaps, then iteratively
    sweeps the sprite through the world with smooth sliding

    """

    if sprite.vel.x == 0 and sprite.vel.y == 0:
        return

    # _resolve_overlaps(sprite, group)

    time_remaining = 1.0
    velocity = vec(sprite.vel)  # working copy for this frame

    for i in range(MAX_SWEEP_ITERATIONS):
        if time_remaining <= 0:
            break

        # Scale velocity to the remaining fraction of the frame
        step_vel = velocity * time_remaining

        # Skip if effectively zero movement left
        if step_vel.length_squared() < 0.0001:
            break

        # Find the closest collision across all walls
        best_toi = 1.0
        best_normal = None

        for wall in group:
            toi, normal = sweep_single(sprite.pos, step_vel, sprite.rect, wall.rect)
            if toi < best_toi:
                best_toi = toi
                best_normal = normal

        if best_normal is None or best_toi >= 1.0:
            sprite.pos += step_vel
            break
        else:
            # Move to impact point minus skin width
            move_t = max(best_toi - SKIN_WIDTH, 0.0)
            sprite.pos += step_vel * move_t

            time_remaining -= best_toi * time_remaining

            dot = velocity.dot(best_normal)
            if dot < 0:
                velocity = velocity - (best_normal * dot)

            if best_normal.x != 0:
                sprite.vel.x = 0
            if best_normal.y != 0:
                sprite.vel.y = 0

            # reset jump
            if best_normal.y == -1 and hasattr(sprite, "state_machine"):
                sprite.state_machine.stateManage("airborne", False)

            # If the sliding velocity is negligible, stop early
            if velocity.length_squared() < 0.0001:
                break


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
        self.health = HEALTH
        self.healthbar = HealthBar(self)
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.load_images()
        self.camera = Camera(self, self.game)
        self.state_machine = StateMachine()
        self.state_machine.start_machine(Player_STATES(self))
        self.hitbox = pg.mask.from_surface(self.image)
        self.all_attacks = []
        self.basic_attack = self.BasicAttack(self)
        self.all_attacks.append(self.basic_attack)
        self.dash = self.Dash(self)
        self.animate()
        self.keys = {
            "left": None,
            "right": None,
            "jump": None,
            "attack": None,
            "dash": None,
        }

    def update(self):
        # get keys and check if character is even moving

        is_moving = self.get_keys()
        self.dash.update()
        # applying acceleration to velocity and velocity to accel
        # eration
        try:

            self.vel += self.accel

        except:
            pass

        self.vel.y += GRAVITY

        # checking if its hitting anything else
        # swept_aabb_collide moves sprite.pos internally, do NOT add vel again
        swept_aabb_collide(self, self.game.all_walls)
        self.rect.center = self.pos

        if not is_moving:

            self.vel.x *= FRICTION
            if abs(self.vel.x) <= 0.05:

                self.vel.x = 0

        self.state_machine.update()
        self.accel *= 0
        self.animate()
        self.basic_attack.update()
        self.get_collisions()
        self.healthbar.update()

    def get_collisions(self):
        for attack in self.game.all_attacks:

            if (
                attack.sprite != self
                and attack.active
                and (
                    self.hitbox.overlap(
                        attack.hitbox,
                        (
                            int(attack.rect.left - self.rect.left),
                            int(attack.rect.top - self.rect.top),
                        ),
                    )
                )
            ):
                print("got hit")
                self.damage(attack)

    def damage(self, attack):
        if not self.state_machine.states["invincible"].active:
            self.health -= attack.damage
            if self.health <= 0:
                self.die()
            attack.affect(self)
            self.state_machine.stateManage("invincible", True)

    def load_images(self):
        # loads images for the sprite
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
        if not self.state_machine.states["stunned"].active:
            if (
                keys[self.keys["jump"]]
                and not self.state_machine.states["airborne"].active
            ):
                print("jumped")
                self.state_machine.stateManage("airborne", True)

                self.vel.y = -JUMP_SPEED
            if keys[self.keys["dash"]]:
                print("dashed")
                self.dash.activate()
            if keys[self.keys["attack"]]:
                print("attacked")
                self.basic_attack.activate()
            if abs(self.vel.x) < PLAYER_SPEED:
                if abs(self.vel.x) + ACCELERATION >= PLAYER_SPEED:
                    if keys[self.keys["left"]]:
                        self.vel.x = -PLAYER_SPEED
                        value = True
                    if keys[self.keys["right"]]:
                        self.vel.x = PLAYER_SPEED
                        value = True
                else:
                    if keys[self.keys["left"]]:
                        self.vel.x -= ACCELERATION

                        value = True
                    if keys[self.keys["right"]]:
                        self.vel.x += ACCELERATION
                        value = True
        return value
    def die(self):
            
            for sprite in self.game.all_sprites:
                if hasattr(sprite, "sprite"):
                    if sprite.sprite == self:
                        sprite.kill()
            self.kill()
    class BasicAttack(Sprite):
        def __init__(self, sprite):
            self.sprite = sprite
            Sprite.__init__(self, self.sprite.game.all_sprites)
            self.sprite.game.all_attacks.add(self)
            self.pos = self.sprite.pos
            self.damage = 10
            self.image = pg.Surface((0, 0))

            self.spritesheet = Spritesheet(
                path.join(self.sprite.game.img_dir, "attack.png")
            )

            self.hitbox = pg.mask.from_surface(self.image)

            self.activetimer = Cooldown(ATTACK_TIME)
            self.activecooldown = Cooldown(ATTACK_COOLDOWN)
            self.activecooldown.start()
            self.active = False

        def update(self):

            self.active = not self.activetimer.ready()
            if self.active:
                self.image = self.spritesheet.get_image(0, 0, 64, 64)

            else:
                self.image = pg.Surface((0, 0))

            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()

            self.hitbox = pg.mask.from_surface(self.image)

            self.pos = self.sprite.pos
            self.rect.center = self.pos

        def activate(self):
            if self.activecooldown.ready():
                print("active big dawg")

                self.activetimer.start()
                self.activecooldown.start()
                self.active = True

        def affect(self, sprite):
            # this is where you can add knockback and stuff
            sprite.vel.x += 20
            sprite.vel.y -= 10
            sprite.state_machine.states["stunned"].enter(STUN_TIME)

    class Dash(Sprite):
        def __init__(self, sprite):
            self.sprite = sprite

            self.pos = self.sprite.pos

            """  self.image = pg.Surface((0, 0))

            self.spritesheet = Spritesheet(
                path.join(self.sprite.game.img_dir, "attack.png")
            ) """

            """ self.hitbox = pg.mask.from_surface(self.image) """

            self.activetimer = Cooldown(DASH_TIME)
            self.activecooldown = Cooldown(DASH_COOLDOWN)
            self.activecooldown.start()
            self.active = False
        
        def update(self):

            self.active = not self.activetimer.ready()
            if self.active and self.sprite.vel.x != 0:
                print("dashing big dawg")

                self.sprite.vel.x += (
                    self.sprite.vel.x / abs(self.sprite.vel.x) * DASH_SPEED
                )

            """ else:
                self.image = pg.Surface((0, 0)) """

            """ self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()

            self.hitbox = pg.mask.from_surface(self.image) """

            """ self.pos = self.sprite.pos
            self.rect.center = self.pos """

        def activate(self):
            if self.activecooldown.ready():

                self.activetimer.start()
                self.activecooldown.start()
                self.active = True


class Dino(Player):

    def __init__(self, game, x, y):
        Player.__init__(self, game, x, y)
        self.keys = {
            "left": pg.K_a,
            "right": pg.K_d,
            "jump": pg.K_w,
            "attack": pg.K_LSHIFT,
            "dash": pg.K_s,
        }


class Alien(Player):

    def __init__(self, game, x, y):
        Player.__init__(self, game, x, y)
        self.keys = {
            "left": pg.K_LEFT,
            "right": pg.K_RIGHT,
            "jump": pg.K_UP,
            "attack": pg.K_RSHIFT,
            "dash": pg.K_DOWN,
        }


class Mob(Sprite):
    # initialize the instance
    def __init__(self, game, x, y,target):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.hitbox = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.accel = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.state_machine = StateMachine()
        self.state_machine.start_machine(Mob_STATES(self))
        self.health = MOB_HEALTH
        self.healthbar = HealthBar(self)
        self.target = target
        # self.pos = vec(x,y) * TILESIZE[1]

    def damage(self, attack):
        if not self.state_machine.states["invincible"].active:
            self.health -= attack.damage
            if self.health <= 0:
                self.die()
            attack.affect(self)
            self.state_machine.stateManage("invincible", True)
    def die(self):
        
        for sprite in self.game.all_sprites:
            if hasattr(sprite, "sprite"):
                if sprite.sprite == self:
                    sprite.kill()
        self.kill()
    def update(self):
        # calls movement toward sprite
        self.move()
        # same as sprite   
        self.vel.x *= 0.75
       
        self.vel.y += GRAVITY
        
        swept_aabb_collide(self, self.game.all_walls)
        self.rect.center = self.pos
        self.get_collisions()
        self.state_machine.update()
    def get_collisions(self):
        for attack in self.game.all_attacks:

            if (
                attack.sprite != self
                and attack.active
                and (
                    self.hitbox.overlap(
                        attack.hitbox,
                        (
                            int(attack.rect.left - self.rect.left),
                            int(attack.rect.top - self.rect.top),
                        ),
                    )
                )
            ):
                print("got hit")
                self.damage(attack)

    # gets teh neccesrary accleration to get to the sprite
    def move(self):
        #x calculations
        if abs(self.vel.x) <= MOB_SPEED:
            if self.target.pos.x > self.pos.x + MOB_ACCELERATION:
                self.vel.x += MOB_ACCELERATION  
            elif self.target.pos.x > self.pos.x:
                self.vel.x += self.target.pos.x - self.pos.x
            if self.target.pos.x < self.pos.x - MOB_ACCELERATION:
                self.vel.x -= MOB_ACCELERATION 
            elif self.target.pos.x < self.pos.x:
                self.vel.x -= self.target.pos.x - self.pos.x
            if abs(self.vel.x) + abs(MOB_ACCELERATION) >= MOB_SPEED:
                if self.target.pos.x > self.pos.x:
                    self.vel.x = MOB_SPEED
                elif self.target.pos.x < self.pos.x:
                    self.vel.x = -MOB_SPEED
        #y calculations
        if self.state_machine.states["airborne"].active == False:
            if self.target.pos.y<self.pos.y - MOB_JUMP:
                self.vel.y -= MOB_JUMP
            elif self.target.pos.y<self.pos.y:
                self.vel.y += self.target.pos.y - self.pos.y
       
            
        

class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.blit(game.wall_img, (0, 0), (0, 0, TILESIZE, TILESIZE))

        self.rect = self.image.get_rect()

        self.vel = vec(0, 0)

        self.pos = vec(x + TILESIZE / 2, y + TILESIZE / 2)
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
        self.pos = vec(x + TILESIZE / 2, y + TILESIZE / 2)
        # self.pos = vec(x,y) * TILESIZE[1]

    def update(self):
        self.rect.center = self.pos
