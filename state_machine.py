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
        if self.sprite.vel.x !=0:
            self.direction = self.sprite.vel.x/abs(self.sprite.vel.x)
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
        pass

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


class Player_Attacking(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)


    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "player_attacking"

    def check(self):
        if self.sprite.basic_attack.active == True:

            self.active = True
        else:
            self.active = False
        


class Mob_Attacking(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)


    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "mob_attacking"

    def check(self):
        pass

class Stunned(State):
    def __init__(self, active, sprite):
        State.__init__(self, active, sprite)
        self.lifetime = Cooldown(1)

    def enter(self,time=1):
        
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
   
    def enter(self,time = 1):
        
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


class StateMachine:
    def __init__(self):

        self.states = {}
        print(self.states)
        self.requestedStates = {}
        self.affects = []
        self.modifiers = {
            "jump" : 1,
            "dash" : 1,
            "attack" : 1,
            
        }
        self.abilities={

        }

    def start_machine(self, init_states=[State]):

        for state in init_states:
            print(state.get_name())
            self.states[state.get_name()] = state
            print(self.states)

        if is_log_enabled:
            print("starting state machine...")

    def update(self):

        for statename, state in self.states.items():
            if statename in self.requestedStates:
                if self.requestedStates[statename] ==True:
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
        Player_Attacking(False, sprite),
        Stunned(False, sprite),
        Invincible(False, sprite),
    ]

def Mob_STATES(mob):
    return [
        Running(False, mob),
        Idle(True, mob),
        Airborne(False, mob),
        Mob_Attacking(False, mob),
        Stunned(False, mob),
        Invincible(False, mob),
    ]   
#abilities
class Ability(Sprite):
        def __init__(self, sprite,image,cooldown,duration,damage,knockback,stun_time,invincible_time,affects=[]):
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
                self.spritesheet = Spritesheet(
                    path.join(self.sprite.game.img_dir, image)
                )
            else:
                self.image = None
            self.hitbox = pg.mask.from_surface(self.image)
            self.direction = 1
            self.activetimer = Cooldown(duration)
            self.activecooldown = Cooldown(cooldown)
            self.activecooldown.start()
            self.active = False

        def update(self):

            self.active = not self.activetimer.ready()
            
            if self.active:
                if self.direction == 1:
                    self.image = self.spritesheet.get_image(0, 0, 64, 64)
                else:
                    self.image = pg.transform.flip(self.spritesheet.get_image(0, 0, 64, 64), True, False)

            else:
                self.image = pg.Surface((0, 0))

            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()

            self.hitbox = pg.mask.from_surface(self.image)

            self.pos = self.sprite.pos
            self.rect.center = self.pos

        def activate(self,direction):
            self.direction = direction
            if self.activecooldown.ready():

                self.activetimer.start()
                self.activecooldown.start()
                self.active = True

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


class BasicAttack(Ability):
        def __init__(self, sprite):
            
            Ability.__init__(self, sprite, "attack.png", ATTACK_COOLDOWN, ATTACK_TIME, 10, [10, -20], STUN_TIME, STUN_TIME, [])

        

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