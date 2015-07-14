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
    def __init__(self, uid, state=None, environment=None, name='', description=''):
        # Properties
        self._env = None
        self._state = None

        # Initialize agent parameters
        self.uid = uid
        self.name = name
        self.description = description
        self.state = state  # state machine - can only have one state at a time
        self._env = environment

    @property  # TODO : Make a descriptor class for this
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        assert isinstance(state, State)
        self._state = state

    @property
    def env(self):
        return self._env

    # @env.setter
    # def env(self, environment):
    #     assert isinstance(environment, Environment)
    #     self._env = environment

    def run(self):
        """Subclass must specify a generator method!"""
        raise NotImplementedError(self)

    def register(self, environment, id=None):
        """Register agent to the simulation environment.

        Parameters
        ----------
        environment : Environment object
        """
        uid = id if id else self.uid
        self._env = environment
        self._env[uid] = self

    def kill(self):
        self.env.__delitem__(self.uid)
        # del self


class BaseNetworkAgent(BaseAgent):
    """Base class for network agents

    Parameters
    ----------
    uid : int
    environment : Environment object
    node : networkx.Graph.node
    """
    def __init__(self, uid, state=None, environment=None, **kwargs):
        super().__init__(uid, state=state, environment=environment, **kwargs)
        # Properties
        self._node = None

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node):
         # TODO : check if node is a networkx node
         self._node = node

    def adjacent_agents(self, state=None):
        """Lists agents directly connected to this agent.

        Parameters
        ----------
        state : State object

        Returns
        -------
        list
        """
        neighbors = [self.env.structure.node[i]['agent'] for i in self.env.structure.neighbors(self.node)
                     if self.env.structure.node[i]['agent'].state is state]
        if state:
            return [neighbor for neighbor in neighbors if neighbor.state is state]
        else:
            return neighbors

    def register(self, environment, node=None):
        """Register agent to the network simulation environment.

        Parameters
        ----------
        environment : Environment object
        node : networkx.Graph.node
        """
        node = node if node else environment.structure.node[self.uid]
        self._env = environment
        self._env[node.id] = self


class State(object):
    """
    A state is an encapsulation of a behavior to be associated with an agent.
    """
    def __init__(self, name, description=None, behavior=None):
        self._behavior = self.static()
        self.name = name
        self.description = description
        self.active = behavior

    @property
    def behavior(self):
        return self._behavior()

    @behavior.setter
    def behavior(self, func):
        if func is None:
            self._behavior = self.static()
        elif callable(func):
            self._behavior = func
        else:
            raise TypeError('Passed object <func> must be callable.')

    def static(self):
        """Empty method for static states"""
        return True

    def __call__(self, *args, **kwargs):
        return self.behavior()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name