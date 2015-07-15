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
        if isinstance(state, State):
            self._state = deepcopy(state)  # make a copy of the original state
            self._state._agent = self  # register agent to state

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

    def register(self, environment, env_id=None):
        """Register agent to the simulation environment.

        Parameters
        ----------
        environment : Environment object
        env_id : Unique identifier in the environment
        """
        uid = env_id if env_id else self.uid
        self._env = environment
        self._env[uid] = self

    def deregister(self):
        """Opposite of the register method. Calling this will remove the agent from its current environment.

        """
        pass

    def kill(self):
        self.env.__delitem__(self.uid)
        # del self

    def __call__(self):
        if self.state is not None:
            self.state.run()
        self.run()


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
        self._node = node  # TODO : check if node is a networkx node

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
    def __init__(self, name, description=None, **state_variables):
        self._agent = None
        self.name = name
        self.description = description
        self.variables = state_variables

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent):
        if isinstance(agent, BaseAgent):
            self._agent = agent
            self._agent._state = self

    @agent.deleter
    def agent(self):
        if self.agent is not None:
            self._agent._state = None
            self._agent = None

    def run(self):
        """Empty method for static states (default)

        To make custom behaviors, sublclass this and override the `run` method. Note that when associated to an agent,
        this class has access to agent methods and attributes. To pass other data, use the `self.variables` attribute
        dictionary.

        """
        pass

    def __call__(self):
        self.run()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name