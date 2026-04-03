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

 

    def update(self):
        print("running")

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
        print("airborne", self.sprite)
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
        self.lifetime = Cooldown(500)

    def enter(self,time):
        
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
        
        if value == True:
            self.enter()
        else:
            self.exit()


class StateMachine:
    def __init__(self):

        self.states = {}
        print(self.states)
        self.requestedStates = {}

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

    def stateManage(self, statename, bool):

        if statename in self.states:
            self.requestedStates[statename] = bool

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