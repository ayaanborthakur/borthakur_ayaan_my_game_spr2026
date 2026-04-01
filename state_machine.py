is_log_enabled: bool = False


class State:
    def __init__(self, active, player):
        self.active = active
        self.player = player

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass

    def get_name(self):
        return ""

    def check(self):
        pass


class Running(State):

    def __init__(self, active, player):
        State.__init__(self, active, player)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        print("running")

    def get_name(self):
        return "running"

    def check(self):
        # We use absolute value to check if moving left or right
        if abs(self.player.vel.x) > 0.05:
            self.active = True
        else:
            self.active = False


class Idle(State):

    def __init__(self, active, player):
        State.__init__(self, active, player)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass

    def get_name(self):
        return "idle"


class Airborne(State):
    def __init__(self, active, player):
        State.__init__(self, active, player)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "airborne"

    def check(self):
        if self.player.vel.y != 0:

            self.active = True


class Dashing(State):
    def __init__(self, active, player):
        State.__init__(self, active, player)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "dashing"

    def check(self):
        if self.player.dash.active == True:

            self.active = True


class Attacking(State):
    def __init__(self, active, player):
        State.__init__(self, active, player)

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        # print("airborne")
        pass

    def get_name(self):
        return "attacking"

    def check(self):
        if self.player.basic_attack.active == True:

            self.active = True


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
                self.states[statename].active = self.requestedStates[statename]

            state.check()
            if state.active:
                state.update()
        self.requestedStates = {}

    def stateManage(self, statename, bool):

        if statename in self.states:
            self.requestedStates[statename] = bool
