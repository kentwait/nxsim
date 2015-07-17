from copy import deepcopy


class BaseAgent(object):
    """Base class for nxsim agents

    Parameters
    ----------
    environment : simpy.Environment() instance
        Simulation environment shared by processes
    agent_id : int, optional
        Unique identifier
    state : dict-like, optional
        State of the Agent. Object must be subscriptable and have an "id" key
    name : str, optional
        Descriptive name of the agent
    state_params : keyword arguments, optional
        Key-value pairs of other state parameters for the agent

    """
    def __init__(self, agent_id, state=None, environment=None, name='', description='', **agent_params):
        # Properties
        self._env = environment
        self._state = state  # state machine - can only have one state at a time

        # Initialize agent parameters
        self.id = agent_id
        self.name = name
        self.description = description
        self.params = agent_params

    @property  # TODO : Make a descriptor class for this
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if isinstance(state, State):
            self._state = deepcopy(state)  # make a copy of the original state
            self._state._agent = self  # register agent to state
            self._env.possible_states.add(state)

    @state.deleter
    def state(self):
        if self.state is not None:
            self._state._agent = None
            self._state = None

    @property
    def env(self):
        return self._env

    # @env.setter
    # def env(self, environment):
    #     assert isinstance(environment, Environment)
    #     self._env = environment

    def run(self):
        """Subclass must specify a generator method!

        Note that if the agent currently has a "state", this class can access state attributes and methods. Similarly,
        if this agent is registered to an environment, it will have access to the environemnt's attributes and methods.
        """
        raise NotImplementedError(self)

    def register(self, environment):
        """Register agent to the simulation environment.

        Parameters
        ----------
        environment : Environment object
        env_id : Unique identifier in the environment
        """
        self._env = environment
        self._env[self.id] = self

    def deregister(self):
        """Opposite of the register method. Calling this will remove the agent from its current environment.

        """
        raise NotImplementedError(self)

    def kill(self):
        self.env.__delitem__(self.id)
        # del self

    def __call__(self):
        if self.state is not None:
            self.state.run()
        self.run()

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__mro__[0], self.id)  # TODO : fix this - <<class '__main__.Person'> 0>

    def __str__(self):
        return '{} {}'.format(self.__class__, self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


class BaseNetworkAgent(BaseAgent):
    """Base class for network agents

    Parameters
    ----------
    id : int
    environment : Environment object
    node : networkx.Graph.node
    """
    def __init__(self, agent_id, state=None, environment=None, name='', description='', **agent_params):
        super().__init__(agent_id, state=state, environment=environment, name=name, description=description,
                         **agent_params)

    def adjacent_agents(self, state=None):
        """Lists agents directly connected to this agent.

        Parameters
        ----------
        state : State object

        Returns
        -------
        list
        """
        neighbors = [self.env.structure.node[i] for i in self.env.structure.neighbors(self.id)]
        if state is None:
            return neighbors
        elif isinstance(state, State):
            return [neighbor for neighbor in neighbors if neighbor.state == state]
        else:
            raise TypeError('state must be an instance of State or None.')


class State(object):
    """
    A state is an encapsulation of a behavior to be associated with an agent.
    """
    def __init__(self, state_id, description, **state_params):
        self._agent = None
        assert isinstance(state_id, str) or isinstance(state_id, int)
        self.id = state_id
        self.description = description
        self.params = state_params

    @property
    def agent(self):
        return self._agent

    def __repr__(self):
        return str(self.__class__)

    def __str__(self):
        return str(self.__class__)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)


TrueState = State(1, '"True" state')
FalseState = State(0, '"False" state')