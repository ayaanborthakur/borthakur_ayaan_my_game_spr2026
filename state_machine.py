is_log_enabled: bool = False
import pygame as pg
from utils import *
from settings import *


class State:
    def __init__(self, active, sprite):
        self.active = active
        self.sprite = sprite

    def enter(self):
        self.active = True

    def exit(self):
        self.active = False

    def update(self):
        pass

    def get_name(self):
        return ""

    def check(self):
        pass


class Running(State):

    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.direction = 1

    def update(self):
        if self.sprite.vel.x != 0:
            self.direction = self.sprite.vel.x / abs(self.sprite.vel.x)

    def get_name(self):
        return "running"

    def check(self):
        # We use absolute value to check if moving left or right
        if abs(self.sprite.vel.x) > 0.05:
            self.active = True
        else:
            self.active = False


class Idle(State):

    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def update(self):
        pass

    def get_name(self):
        return "idle"


class Airborne(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def update(self):
        self.sprite.state_machine.modifiers["accel"] = 0.2

    def get_name(self):
        return "airborne"

    def check(self):
        if self.sprite.vel.y != 0:

            self.active = True


class Dashing(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "dashing"

    def check(self):
        if self.sprite.dash.active == True:

            self.active = True
        else:
            self.active = False


class Attacking(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def update(self):
        self.sprite.state_machine.stateManage("slowed", True)

    def get_name(self):
        return "attacking"

    def check(self):
        if hasattr(self.sprite, "basic_attack") and self.sprite.basic_attack.attacking:
            self.active = True
        else:
            self.active = False


class Mob_Idle(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def get_name(self):
        return "mob_idle"


class Mob_Aggro(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    def get_name(self):
        return "mob_aggro"


class Stunned(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    def exit(self):
        self.lifetime.reset()
        self.active = False

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "stunned"

    def check(self):
        if self.lifetime.ready() == True:
            self.exit()


class Invincible(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    def exit(self):
        self.lifetime.reset()
        self.active = False

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "invincible"

    def check(self):
        value = False
        if self.sprite.state_machine.states["stunned"].active == True:
            value = True

        if "dashing" in self.sprite.state_machine.states:
            if self.sprite.state_machine.states["dashing"].active == True:
                value = True

        if value:
            self.active = True
        elif self.lifetime.ready():
            self.exit()


class Slowed(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    def exit(self):
        self.active = False

    def update(self):
        self.sprite.state_machine.modifiers["slow"] = 0.6

        pass

    def get_name(self):
        return "slowed"

    def check(self):
        if (
            "attacking" in self.sprite.state_machine.states
            and self.sprite.state_machine.states["attacking"].active == True
        ):
            self.active = True
        else:
            self.active = False


class StateMachine:
    def __init__(self, sprite):

        self.states = {}
        print(self.states)
        self.requestedStates = {}
        self.affects = []
        self.modifiers = {"jump": 1, "dash": 1, "attack": 1, "speed": 1, "slow": 1}
        self.abilities = {}
        self.sprite = sprite

    def start_machine(self, init_states=[State]):

        for state in init_states:
            print(state.get_name())
            self.states[state.get_name()] = state

            print(self.states)

        if is_log_enabled:
            print("starting state machine...")

    def update(self):
        self.modifiers = {
            "jump": 1,
            "dash": 1,
            "attack": 1,
            "speed": 1,
            "slow": 1,
            "accel": 1,
        }
        for statename, state in self.states.items():
            if statename in self.requestedStates:
                if self.requestedStates[statename] == True:
                    self.states[statename].enter()
                else:
                    self.states[statename].exit()

            state.check()
            if state.active:
                state.update()
        self.requestedStates = {}

        for affect in self.affects:
            affect.update()
            if affect.active == False:
                self.affects.remove(affect)
        try:
            self.sprite.jump_speed = JUMP_SPEED * self.modifiers["jump"]
            self.sprite.dash_speed = DASH_SPEED * self.modifiers["dash"]
            self.sprite.speed = PLAYER_SPEED * self.modifiers["speed"]
        except Exception as e:
            pass

    def stateManage(self, statename, bool):

        if statename in self.states:
            self.requestedStates[statename] = bool

    def addAffect(self, affect):
        self.affects.append(affect)


def Player_STATES(sprite):
    return [
        Running(False, sprite),
        Idle(True, sprite),
        Airborne(False, sprite),
        Dashing(False, sprite),
        Attacking(False, sprite),
        Stunned(False, sprite),
        Invincible(False, sprite),
        Slowed(False, sprite),
    ]


def Mob_STATES(mob):
    return [
        Running(False, mob),
        Idle(True, mob),
        Airborne(False, mob),
        Attacking(False, mob),
        Stunned(False, mob),
        Invincible(False, mob),
        Mob_Idle(True, mob),
        Mob_Aggro(False, mob),
        Slowed(False, mob),
    ]


# abilities
class MeleeAbility(Sprite):
    def __init__(
        self,
        sprite,
        image,
        cooldown,
        duration,
        damage,
        knockback,
        stun_time,
        invincible_time,
        self_stun,
        affects=[],
        delay=0,
    ):
        self.sprite = sprite
        Sprite.__init__(self, self.sprite.game.all_sprites)
        self.sprite.game.all_attacks.add(self)
        self.pos = self.sprite.pos
        self.damage = damage
        self.knockback = knockback
        self.stun_time = stun_time
        self.invincible_time = invincible_time
        self.affects = affects
        if image != None:
            self.image = pg.Surface((0, 0))
            self.spritesheet = Spritesheet(path.join(self.sprite.game.img_dir, image))
        else:
            self.image = None
        self.hitbox = pg.mask.from_surface(self.image)
        self.direction = 1
        self.delay = Cooldown(delay)
        self.activetimer = Cooldown(duration + delay)
        self.cooldown = Cooldown(cooldown + duration)
        self.active = False
        self.self_stun = self_stun
        self.attacking = False

    def update(self):

        self.attacking = not self.activetimer.ready() 
        self.active = self.attacking and self.delay.ready()

        if self.active:
            self.animate()
            if self.direction == -1:
                self.image = pg.transform.flip(self.image, True, False)

        else:
            self.image = pg.Surface((0, 0))

        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.hitbox = pg.mask.from_surface(self.image)

        self.pos = self.sprite.pos
        self.rect.center = self.pos

    def animate(self):
        max_frames = self.spritesheet.spritesheet.get_width() // 64
        total_elapsed = self.activetimer.current_time - self.activetimer.start_time
        attack_elapsed = total_elapsed - self.delay.time
        attack_duration = self.activetimer.time - self.delay.time
        progress = attack_elapsed / attack_duration
        frame_index = int(progress * max_frames)
        frame_index = min(frame_index, max_frames - 1)
        self.image = self.spritesheet.get_image(frame_index * 64, 0, 64, 64)

    def activate(self, direction):

        if self.cooldown.ready():

            self.direction = direction
            if self.self_stun:
                self.sprite.state_machine.states["slowed"].enter(self.activetimer.time)
            self.delay.start()
            self.activetimer.start()
            self.cooldown.start()
            self.attacking = True

    def affect(self, sprite):
        # this is where you can add knockback and stuff
        sprite.vel.x += self.knockback[0] * self.direction
        sprite.vel.y += self.knockback[1]
        sprite.health -= self.damage
        sprite.state_machine.states["stunned"].enter(self.stun_time)
        sprite.state_machine.states["invincible"].enter(self.invincible_time)
        if self.affects != []:
            for affect in self.affects:
                sprite.state_machine.affects.append(affect(sprite))


class RangedAbility(Sprite):
    def __init__(self, sprite, cooldown, projectile, self_stun, image=None, delay=0):
        self.sprite = sprite
        Sprite.__init__(self, self.sprite.game.all_sprites)
        self.pos = self.sprite.pos
        self.projectiles = []
        self.projectile = projectile
        self.image = pg.Surface((1, 1))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = pg.mask.from_surface(self.image)
        self.self_stun = self_stun

        self.direction = 1
        self.delay = Cooldown(delay)
        self.activetimer = Cooldown(delay)
        self.cooldown = Cooldown(cooldown)
        self.attacking = False
        self.pending = False

    def update(self):

        self.attacking = not self.activetimer.ready()

        if self.pending and self.delay.ready():
            self.projectiles.append(self.projectile(self.sprite, self.direction))
            self.pending = False

        for projectile in self.projectiles:
            projectile.update()
            if projectile.active == False:
                self.projectiles.remove(projectile)
                projectile.kill()

    def activate(self, direction):
        self.direction = direction
        if self.cooldown.ready():
            if self.self_stun:
                self.sprite.state_machine.states["slowed"].enter(self.activetimer.time)
            self.delay.start()
            self.activetimer.start()
            self.cooldown.start()
            self.attacking = True
            self.pending = True


class Projectile(Sprite):
    def __init__(
        self,
        sprite,
        direction,
        image,
        speed,
        damage,
        knockback,
        stun_time,
        invincible_time,
        affects=[],
    ):
        self.sprite = sprite
        Sprite.__init__(self, self.sprite.game.all_sprites)
        self.sprite.game.all_attacks.add(self)
        self.pos = pg.math.Vector2(self.sprite.pos)
        self.direction = direction
        self.speed = speed
        self.active = True
        self.image = pg.Surface((10, 10))
        pg.draw.circle(self.image, (255, 0, 0), (5, 5), 5)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = pg.mask.from_surface(self.image)
        self.rect.center = self.pos
        self.damage = damage
        self.knockback = knockback
        self.stun_time = stun_time
        self.invincible_time = invincible_time
        self.affects = affects

    def update(self):
        self.pos.x += self.speed * self.direction
        self.rect.center = self.pos

        if self.active == False:
            self.die()

    def affect(self, sprite):
        # this is where you can add knockback and stuff
        sprite.vel.x += self.knockback[0]
        sprite.vel.y += self.knockback[1]
        sprite.health -= self.damage
        sprite.state_machine.states["stunned"].enter(self.stun_time)
        sprite.state_machine.states["invincible"].enter(self.invincible_time)
        if self.affects != []:
            for affect in self.affects:

                sprite.state_machine.affects.append(affect(sprite))
        self.die()
        self.active = False

    def die(self):

        self.kill()


class BasicRangedAbility(RangedAbility):
    def __init__(self, sprite):
        RangedAbility.__init__(self, sprite, 500, BasicProjectile, True, None, 50)


class BasicProjectile(Projectile):
    def __init__(self, sprite, direction):
        Projectile.__init__(self, sprite, direction, None, 20, 5, [5, 0], 100, 100, [])


class BasicAttack(MeleeAbility):
    def __init__(self, sprite):

        MeleeAbility.__init__(
            self,
            sprite,
            "sword.png",
            ATTACK_COOLDOWN,
            ATTACK_TIME,
            10,
            [20,-10],
            STUN_TIME,
            STUN_TIME,
            True,
            [],
            100,
        )


class MobBasicAttack(MeleeAbility):
    def __init__(self, sprite):

        MeleeAbility.__init__(
            self,
            sprite,
            "sword.png",
            ATTACK_COOLDOWN,
            ATTACK_TIME,
            4,
            [5, -5],
            STUN_TIME,
            STUN_TIME,
            True,
            [],
            200,
        )


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
        self.cooldown = Cooldown(DASH_COOLDOWN)
        self.cooldown.start()
        self.active = False

    def update(self):

        self.active = not self.activetimer.ready()
        if self.active and self.sprite.vel.x != 0:
            print("dashing big dawg")

            self.sprite.vel.x = (
                self.sprite.vel.x / abs(self.sprite.vel.x) * self.sprite.dash_speed
            )

        """ else:
                self.image = pg.Surface((0, 0)) """

        """ self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()

            self.hitbox = pg.mask.from_surface(self.image) """

        """ self.pos = self.sprite.pos
            self.rect.center = self.pos """

    def activate(self):
        if self.cooldown.ready():

            self.activetimer.start()
            self.cooldown.start()
            self.active = True
