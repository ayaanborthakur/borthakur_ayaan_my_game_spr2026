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
        if self.player.accel.magnitude() >= 0:
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

    def stateManage(self, statename, bool):

        if statename() in self.states:
            self.requestedStates[statename()] = bool
