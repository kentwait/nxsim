"""
Agents
======
Agents are autonomous units that run within a simulation environment.

The overall result of a simulation is a result of the behavior of each agent and interactions between agents. Because
the specification of an agent greatly depends on the simulation goals, nxsim only provides base constructors from which
actual simulation agents can be built on.

"""
from .core import BaseEnvironment

__all__ = ['BaseAgent', 'BaseNetworkAgent', 'BaseState', 'TrueState', 'FalseState']


class BaseAgent(object):
    """Base class for nxsim agents

    Parameters
    ----------
    environment : simpy.Environment() instance
        Simulation environment shared by processes
    agent_id : int, optional
        Unique identifier
    state : dict-like, optional
        BaseState of the Agent. Object must be subscriptable and have an "id" key
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
        self.state = state

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        assert isinstance(self.env, BaseEnvironment)
        assert isinstance(state, BaseState)
        if self.env is not None:
            self._env.possible_states.add(state)  # add current state to possible states
            self._state = state  # assign state to _state
        else:
            raise ValueError('self.env must contain an Environment instance.')

    @state.deleter
    def state(self):
        if self.state is not None:
            self._state = None

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, environment):
        assert isinstance(environment, BaseEnvironment)
        if self._env is None:
            self._env = environment
            self._env[self.id] = self
            if self.state is not None: self._env.possible_states.add(self.state)
        else:
            raise ValueError('Agent <id: {}, name: {}> is already assigned to environment {}'.format(
                self.id, self.name, self.env))

    def run(self):
        """Subclass must specify a generator method!

        Note that if the agent currently has a "state", this class can access state attributes and methods. Similarly,
        if this agent is registered to an environment, it will have access to the environemnt's attributes and methods.
        """
        raise NotImplementedError(self)

    def register(self, environment):
        """Register agent to the simulation environment.

        This method uses the same setter method such that self.register(some_env) will produce the same result as
        self.env = some_env

        Parameters
        ----------
        environment : Environment object
        env_id : Unique identifier in the environment
        """
        self.env = environment

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

    See Also
    --------
    BaseAgent

    """
    def __init__(self, agent_id, state=None, environment=None, name='', description='', **agent_params):
        super().__init__(agent_id, state=state, environment=environment, name=name, description=description,
                         **agent_params)

    def adjacent_agents(self, state=None):
        """Lists agents directly connected to this agent.

        Parameters
        ----------
        state : BaseState object

        Returns
        -------
        list
        """
        neighbors = [self.env.structure.node[i] for i in self.env.structure.neighbors(self.id)]
        if state is None:
            return neighbors
        elif isinstance(state, BaseState):
            return [neighbor for neighbor in neighbors if neighbor.state == state]
        else:
            raise TypeError('state must be an instance of BaseState or None.')


class BaseState(object):
    """
    A state is an encapsulation of a behavior to be associated with an agent.
    """
    def __init__(self, state_id, description, **state_params):
        assert isinstance(state_id, str) or isinstance(state_id, int)
        self.id = state_id
        self.description = description
        self.params = state_params

    def __repr__(self):
        return str(self.id)  # think of a better way to represent this

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.id


TrueState = BaseState(1, '"True" state')
FalseState = BaseState(0, '"False" state')