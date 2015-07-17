class BaseMonitor(object):
    """Monitors agents and the simulation environment.

    Monitors, unlike agents, exist outside the context of a simulation environment. However, monitors do interact
    with the simulation environment either by passive observation or actively modifying the structure and parameters
    of the simulation environment.

    Parameters
    ----------
    environment : Environment object
    interval : int or None, optional (default = None)

    """
    def __init__(self, environment, name='monitor', description=''):
        self.env = environment
        self.name = name
        self.description = description
        self.register()

    def register(self):
        self.env.monitors.append(self)
        self.env.process(self.run())

    def run(self):
        raise NotImplementedError(self)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class StateMonitor(BaseMonitor):
    """Counts the number of states per logging interval

    Parameters
    ----------
    environment : Environment object
    interval : int, optional (default = 1)
    possible_states : list, optional (default = ())

    """
    def __init__(self, environment, interval=1, name='monitor', description='', possible_states=()):
        super().__init__(environment, name=name, description=description)
        self.interval = interval
        self.states = self.env.possible_states if len(possible_states) == 0 else possible_states
        self.tally = {str(state): list() for state in self.states}

    def run(self):
        while True:
            for state in self.states:
                count = len(self.env.list(state=state))
                self.tally[str(state)].append(count)
            yield self.env.timeout(self.interval)

    # TODO : when simulation finished, write to file
    def save(self, path):
        with open(path, 'w') as f:
            print('time', *self.states, sep='\t')
            for index in range(self.env.init_time, self.tally[str(self.states[0])]):
                time = index * self.interval
                values = [self.tally[state][index] for state in self.states]
                print(time, *values, sep='\t', file=f)


class BaseManager(BaseMonitor):
    def __init__(self, environment, name='manager', description=''):
        super().__init__(environment, name=name, description=description)

    def run(self):
        raise NotImplementedError(self)