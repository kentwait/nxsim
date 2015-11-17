"""
Agents
======
Agents are autonomous units that run within a simulation environment.

The overall result of a simulation is a result of the behavior of each agent and interactions between agents. Because
the specification of an agent greatly depends on the simulation goals, nxsim only provides base constructors from which
actual simulation agents can be built on.

"""
from .core import BaseEnvironment
from collections import namedtuple
import weakref

__all__ = ['BaseAgent', 'BaseNetworkAgent', 'BaseState', 'TrueState', 'FalseState']


class BaseState(namedtuple('State', ['uid', 'description'])):
    """
    A state is an encapsulation of a behavior to be associated with an agent.
    """
    __slots__ = ()

    def __repr__(self):
        return str(self.uid)  # think of a better way to represent this

    def __str__(self):
        return str(self.uid)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.uid


TrueState = BaseState(1, '"True" state')
FalseState = BaseState(0, '"False" state')


class BaseAgent(object):
    """Base class for nxsim agents

    The BaseAgent class is the most basic agent type in nxsim. All other agent classes inherit from this class.

    To create an agent, use the BaseAgent constructor supplying a unique ID for the agent. This unique ID plays a
    very important role to identify, retrieve, and check for the existence of agents in an environment. Other parameters
    such as state, environment, name, and description are optional and can be added later.

    Parameters
    ----------
    environment : nxsim.BaseEnvironment
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
    def __init__(self, uid, environment, state=None, name='', description='', **agent_params):
        """Create a BaseAgent instance and registers it to an existing environment

        Parameters
        ----------
        uid : int
            Unique identifier
        environment : BaseEnvironment
            Simulation environment
        state : BaseState, optional
        name : str, optional
            Descriptive name of the agent
        description : str, optional
            Short description
        agent_params : keyword arguments, optional
            Key-value pairs of other state parameters for the agent

        """
        # Initializae Properties
        self._env = None
        self._state = None

        # Execute property setters
        self.env = environment
        if state:
            assert isinstance(state, BaseState)
            self._state = state  # state machine - can only have one state at a time

        # Initialize agent parameters
        self.uid = uid
        self.name = name
        self.description = description
        self.params = agent_params

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
            self._env = weakref.ref(environment)
            self._env[self.uid] = self
            if self.state is not None:
                self._env.possible_states.add(self.state)
        else:
            raise ValueError('Agent <id: {}, name: {}> is already assigned to environment {}'.format(
                self.uid, self.name, self.env))

    def run(self):
        """Subclass must specify a generator method!

        Note that if the agent currently has a "state", this class can access state attributes and methods. Similarly,
        if this agent is registered to an environment, it will have access to the environemnt's attributes and methods.
        """
        raise NotImplementedError(self)

    def __call__(self):
        if self.state is not None:
            # self.state.run()  # TODO : how to run a behavior that is associated to a certain state
            pass
        self.run()

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__mro__[0], self.uid)  # TODO : fix this - <<class '__main__.Person'> 0>

    def __str__(self):
        return '{} {}'.format(self.__class__, self.uid)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.uid == other.uid

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
    def __init__(self, uid, environment, state=None, name='', description='', **agent_params):
        super().__init__(uid, environment, state=state, name=name, description=description,
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
        neighbors = [self.env.structure.node[i] for i in self.env.structure.neighbors(self.uid)]
        if state is None:
            return neighbors
        elif isinstance(state, BaseState):
            return [neighbor for neighbor in neighbors if neighbor.state == state]
        else:
            raise TypeError('state must be an instance of BaseState or None.')


class TestAgent(BaseAgent):
    pass
