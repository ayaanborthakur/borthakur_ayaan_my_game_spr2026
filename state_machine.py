is_log_enabled: bool = False
import pygame as pg
from utils import *
from settings import *


#state class
class State:
    #function for state initialization
    def __init__(self, active, sprite):
        self.active = active
        self.sprite = sprite

    #function to enter state
    def enter(self):
        self.active = True

    #function to exit state
    def exit(self):
        self.active = False

    #function for state update
    def update(self):
        pass

    #function to get state name
    def get_name(self):
        return ""

    #function to check state
    def check(self):
        pass


#running state class
class Running(State):

    #function for running state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.direction = 1

    #function for running state update
    def update(self):
        if self.sprite.vel.x != 0:
            self.direction = self.sprite.vel.x / abs(self.sprite.vel.x)

    #function to get running state name
    def get_name(self):
        return "running"

    #function to check running state
    def check(self):
        # We use absolute value to check if moving left or right
        if abs(self.sprite.vel.x) > 0.05:
            self.active = True
        else:
            self.active = False


#idle state class
class Idle(State):

    #function for idle state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function for idle state update
    def update(self):
        pass

    #function to get idle state name
    def get_name(self):
        return "idle"


#airborne state class
class Airborne(State):
    #function for airborne state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function for airborne state update
    def update(self):
        self.sprite.state_machine.modifiers["accel"] = 0.2

    #function to get airborne state name
    def get_name(self):
        return "airborne"

    #function to check airborne state
    def check(self):
        if self.sprite.vel.y != 0:

            self.active = True


#dashing state class
class Dashing(State):
    #function for dashing state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function for dashing state update
    def update(self):
        # print("airborne")
        pass

    #function to get dashing state name
    def get_name(self):
        return "dashing"

    #function to check dashing state
    def check(self):
        if self.sprite.dash.active == True:

            self.active = True
        else:
            self.active = False


#attacking state class
class Attacking(State):
    #function for attacking state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function for attacking state update
    def update(self):
        self.sprite.state_machine.stateManage("slowed", True)

    #function to get attacking state name
    def get_name(self):
        return "attacking"

    #function to check attacking state
    def check(self):
        if hasattr(self.sprite, "basic_attack") and self.sprite.basic_attack.attacking:
            self.active = True
        else:
            self.active = False


#mob idle state class
class Mob_Idle(State):
    #function for mob idle state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function to get mob idle state name
    def get_name(self):
        return "mob_idle"


#mob aggro state class
class Mob_Aggro(State):
    #function for mob aggro state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)

    #function to get mob aggro state name
    def get_name(self):
        return "mob_aggro"


#stunned state class
class Stunned(State):
    #function for stunned state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    #function to enter stunned state
    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    #function to exit stunned state
    def exit(self):
        self.lifetime.reset()
        self.active = False

    #function for stunned state update
    def update(self):
        # print("airborne")
        pass

    #function to get stunned state name
    def get_name(self):
        return "stunned"

    #function to check stunned state
    def check(self):
        if self.lifetime.ready() == True:
            self.exit()


#invincible state class
class Invincible(State):
    #function for invincible state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    #function to enter invincible state
    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    #function to exit invincible state
    def exit(self):
        self.lifetime.reset()
        self.active = False

    #function for invincible state update
    def update(self):
        # print("airborne")
        pass

    #function to get invincible state name
    def get_name(self):
        return "invincible"

    #function to check invincible state
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


#slowed state class
class Slowed(State):
    #function for slowed state initialization
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    #function to enter slowed state
    def enter(self, time=1):

        self.lifetime.start(time)
        self.active = True

    #function to exit slowed state
    def exit(self):
        self.active = False

    #function for slowed state update
    def update(self):
        self.sprite.state_machine.modifiers["slow"] = 0.6

        pass

    #function to get slowed state name
    def get_name(self):
        return "slowed"

    #function to check slowed state
    def check(self):
        if (
            "attacking" in self.sprite.state_machine.states
            and self.sprite.state_machine.states["attacking"].active == True
        ):
            self.active = True
        else:
            self.active = False


#state machine class
class StateMachine:
    #function for state machine initialization
    def __init__(self, sprite):

        self.states = {}
        self.requestedStates = {}
        self.affects = []
        self.modifiers = {"jump": 1, "dash": 1, "attack": 1, "speed": 1, "slow": 1}
        # permanent bonuses accumulated from kills - survive the per-frame modifier reset
        self.base_modifiers = {"jump": 1.0, "dash": 1.0, "attack": 1.0, "speed": 1.0}
        self.abilities = {}
        self.sprite = sprite

    #function to start state machine
    def start_machine(self, init_states=[State]):

        for state in init_states:
            self.states[state.get_name()] = state

        if is_log_enabled:
            print("starting state machine...")

    #function for state machine update: checks active state transitions, applies stat modifiers, and processes active status affects
    def update(self):
        # start each frame from accumulated kill bonuses; states then layer on top
        self.modifiers = {
            "jump": self.base_modifiers.get("jump", 1.0),
            "dash": self.base_modifiers.get("dash", 1.0),
            "attack": self.base_modifiers.get("attack", 1.0),
            "speed": self.base_modifiers.get("speed", 1.0),
            "slow": 1.0,
            "accel": 1.0,
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

    #function to manage state
    def stateManage(self, statename, bool):

        if statename in self.states:
            self.requestedStates[statename] = bool

    #function to add affect
    def addAffect(self, affect):
        self.affects.append(affect)


#function to get player states
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


#function to get mob states
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
#melee ability class
class MeleeAbility(Sprite):
    #function for melee ability initialization
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

    #function for melee ability update: tracks attack duration timers and delay cooldowns to animate hitbox when active
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

    #function to animate melee ability
    def animate(self):
        max_frames = self.spritesheet.spritesheet.get_width() // 64
        total_elapsed = self.activetimer.current_time - self.activetimer.start_time
        attack_elapsed = total_elapsed - self.delay.time
        attack_duration = self.activetimer.time - self.delay.time
        progress = attack_elapsed / attack_duration
        frame_index = int(progress * max_frames)
        frame_index = min(frame_index, max_frames - 1)
        self.image = self.spritesheet.get_image(frame_index * 64, 0, 64, 64)
        if hasattr(self, 'scale_size') and self.scale_size != (64, 64):
            self.image = pg.transform.scale(self.image, self.scale_size)

    #function to activate melee ability
    def activate(self, direction):

        if self.cooldown.ready():

            self.direction = direction
            if self.self_stun:
                self.sprite.state_machine.states["slowed"].enter(self.activetimer.time)
            self.delay.start()
            self.activetimer.start()
            self.cooldown.start()
            self.attacking = True

    #function to apply melee ability affect
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


#ranged ability class
class RangedAbility(Sprite):
    #function for ranged ability initialization
    def __init__(self, sprite, cooldown, projectile, self_stun, image=None, delay=0, activetime=100):
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
        self.activetimer = Cooldown(activetime)
        self.cooldown = Cooldown(cooldown)
        self.attacking = False
        self.pending = False

    #function for ranged ability update: checks active firing timers and spawns projectile instances after initial cast delay
    def update(self):

        self.attacking = not self.activetimer.ready()

        if self.pending and self.delay.ready():
            self.projectiles.append(self.projectile(self.sprite, self.direction))
            self.pending = False

        for projectile in self.projectiles:
            
            if projectile.active == False:
                self.projectiles.remove(projectile)
                projectile.kill()

    #function to activate ranged ability
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


#projectile class
class Projectile(Sprite):
    #function for projectile initialization
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
        if image == None:
            self.image = pg.Surface((10, 10))
            pg.draw.circle(self.image, (255, 0, 0), (5, 5), 5)
        else:
            self.spritesheet = Spritesheet(path.join(self.sprite.game.img_dir, image))
            self.image = self.spritesheet.get_image(0, 0, 64, 64)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.hitbox = pg.mask.from_surface(self.image)
        self.rect.center = self.pos
        self.damage = damage
        self.knockback = knockback
        self.stun_time = stun_time
        self.invincible_time = invincible_time
        self.affects = affects

    #function for projectile update: moves projectile along direction vector at set speed and removes it when inactive
    def update(self):
        self.pos.x += self.speed * self.direction
        self.rect.center = self.pos
        self.animate()
        if self.active == False:
            self.die()

    #function to animate projectile
    def animate(self):
        pass

    #function to apply projectile affect
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

    #function for projectile death
    def die(self):

        self.kill()


#basic ranged ability class
class BasicRangedAbility(RangedAbility):
    #function for basic ranged ability initialization
    def __init__(self, sprite):
        RangedAbility.__init__(self, sprite, 250, BasicProjectile, True, None, 20, 50)


#basic projectile class
class BasicProjectile(Projectile):
    #function for basic projectile initialization
    def __init__(self, sprite, direction):
        Projectile.__init__(self, sprite, direction, None, 35, 25, [-10, 0], 100, 100, [])


#basic attack class
class BasicAttack(MeleeAbility):
    #function for basic attack initialization
    def __init__(self, sprite):

        MeleeAbility.__init__(
            self,
            sprite,
            "sword.png",
            ATTACK_COOLDOWN,
            ATTACK_TIME,
            10,
            [20, -10],
            STUN_TIME,
            STUN_TIME,
            True,
            [],
            100,
        )


#dino basic attack class
class DinoBasicAttack(MeleeAbility):
    #function for dino basic attack initialization
    def __init__(self, sprite):

        MeleeAbility.__init__(
            self,
            sprite,
            "sword.png",
            ATTACK_COOLDOWN,
            ATTACK_TIME,
            25,
            [25, -12],
            STUN_TIME,
            STUN_TIME,
            True,
            [],
            100,
        )
        self.scale_size = (100, 100)


#dinosaur attack class
class RoarAttack(RangedAbility):
    #function for dinosaur attack
    def __init__(self, sprite):
        # Slower attack with bigger cooldown
        RangedAbility.__init__(self, sprite, 6000, RoarProjectile, True, None, 100, 1200)
        # Override activetimer to last for the full roar duration
        
        # Cooldown between spawning each ring of the sound wave
        self.spawn_interval = Cooldown(300)

    #function for roar attack update: spawns expanding sound wave projectiles at set intervals during active roar duration
    def update(self):

        self.attacking = not self.activetimer.ready()
        if not self.attacking:
            self.pending = False

        if self.pending and self.delay.ready() and self.spawn_interval.ready():
            self.projectiles.append(self.projectile(self.sprite, self.direction))
            self.spawn_interval.start()

        for projectile in list(self.projectiles):
            projectile.update()
            if projectile.active == False:
                self.projectiles.remove(projectile)
                projectile.kill()


#roar projectile class
class RoarProjectile(Projectile):
    #function for roar projectile initialization
    def __init__(self, sprite, direction):
        Projectile.__init__(
            self, sprite, direction, "roarProjectile.png", 6, 5, [30, 0], 100, 100, []
        )
        self.birth_time = pg.time.get_ticks()
        self.base_size = 20  # starting size in pixels
        
        self.lifetime = Cooldown(1500)  # projectile dies after 1.5 seconds
        self.lifetime.start()

    #function to animate roar projectile: scales projectile image size dynamically based on elapsed lifetime
    def animate(self):
        # calculate how long this projectile has been alive
        age = pg.time.get_ticks() - self.birth_time
        progress = age / 15
        current_size = int(self.base_size + progress)
        #read from the original spritesheet, then scale to the growing size
        self.image = self.spritesheet.get_image(0, 0, 64, 64)
        self.image = pg.transform.scale(self.image, (current_size, current_size))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self.hitbox = pg.mask.from_surface(self.image)
   


#mob basic attack class
class MobBasicAttack(MeleeAbility):
    #function for mob basic attack initialization
    def __init__(self, sprite):

        MeleeAbility.__init__(
            self,
            sprite,
            "sword.png",
            ATTACK_COOLDOWN,
            ATTACK_TIME,
            getattr(sprite, 'mob_damage', 4),
            [5, -5],
            STUN_TIME,
            STUN_TIME,
            True,
            [],
            200,
        )


#dash class
class Dash(Sprite):
    #function for dash initialization
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

    #function for dash update
    def update(self):

        self.active = not self.activetimer.ready()
        if self.active and self.sprite.vel.x != 0:

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

    #function to activate dash
    def activate(self):
        if self.cooldown.ready():

            self.activetimer.start()
            self.cooldown.start()
            self.active = True
