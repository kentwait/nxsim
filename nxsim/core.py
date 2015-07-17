import simpy
import networkx as nx
from copy import deepcopy
from .agents import BaseAgent, State


class BaseEnvironment(simpy.Environment):
    """The environment behaves like a dictionary of agents.

    In BaseEnvironment, there is no positional structure to the arrangement of the agents, so the agents are stored as
    a key-value pair in a dictionary. The key corresponds to an arbitrary label for the agent for easy retrieval.

    Parameters
    ----------
    initial_time : int
        Specifies the time unit to start with, inherited from simpy.Environment
    structure : dictionary like
    """
    def __init__(self, structure=None, initial_time=0):
        self.init_time = initial_time
        super().__init__(initial_time=initial_time)
        self.structure = dict() if structure is None else structure
        self.possible_states = set()
        self.monitors = list()
        self.resources = list()

    @property
    def agents(self):
        return self.structure.values()

    def current(self):
        """
        Return a snapshot of the current state of the entire simulation environment.
        """
        return deepcopy(self)

    def list(self, state:State=None):
        """Returns list of agents based on their state and connectedness

        Parameters
        ----------
        state : State object, optional
            Used to select agents that have the same specified "state". If state is None, returns all agents regardless
            of its current state

        Returns
        -------
        list
        """
        if state is None:
            return self.agents  # return all regardless of state
        else:
            return [agent for agent in self.agents if agent.state == state]

    def populate(self, agent_constructor:BaseAgent, default_state:State=None):
        """Populates slots in the current structure with agents.

        This assumes that `structure` is iterable and has a `len` value. The number of agents constructed are equal
        to the number of units iterable in the structure - a one-to-one correspondence.

        Parameters
        ----------
        agent_constructor : agent's constructor class

        """
        if (len(list(self.agents)) == 0) and (len(self.structure) > 0):
            for i in self.structure.keys():
                self.structure[i] = agent_constructor(i, state=default_state, environment=self)

    def items(self):
        return self.structure.items()

    def __len__(self):
        """Returns number of agents registered in the environment"""
        return len(self.structure)

    def __contains__(self, agent):
        """Returns True if the agent is registered in this environment"""
        return any(a.uid == agent.uid for a in self.agents)

    def __getitem__(self, key):
        """Returns the agent associated with this key"""
        return self.structure[key]

    def __setitem__(self, key, agent):
        """Agent is registered into this environment"""
        self.structure[key] = agent
        self.process(agent.run())

    def __delitem__(self, key):
        """Agent is removed from this environment"""
        del self.structure[key]

    def __repr__(self):
        return repr(self.structure)


class NetworkEnvironment(BaseEnvironment):
    """An environment that uses a graph to control the spatial configuration of agents.

    This is a subclass of BaseEnvironment. Thus it likewise also acts like a dictionary of agents.

    Parameters
    ---------
    graph : Networkx Graph
    initial_time : int

    """
    def __init__(self, structure=None, initial_time=0):
        super().__init__(initial_time=initial_time)
        self.structure = nx.Graph(structure)  # instantiates an empty graph

    @property
    def agents(self):
        agents = []
        for i in self.structure.nodes():
            try:
                agents.append(self.structure.node[i]['agent'])
            except KeyError:
                pass
        return agents

    def populate(self, agent_constructor:BaseAgent, default_state:State=None):
        if (len(list(self.agents)) == 0) and (len(self.structure) > 0):
            for i in self.structure.nodes():
                self.__setitem__(i, agent_constructor(i, state=default_state, environment=self))

    def add_edges(self, agent_1, agent_2):
        pass

    def items(self):
        return {i: self.__getitem__(i) for i in self.structure.nodes()}

    def __len__(self):
        """Returns number of agents registered in the environment"""
        return len(self.agents)

    def __contains__(self, agent):
        """Returns True if the agent is registered in this environment"""
        return any(a.uid == agent.uid for a in self.agents)

    def __getitem__(self, node_id):
        """Returns the agent given its associated node ID"""
        return self.structure.node[node_id]

    def __setitem__(self, node_id, agent):
        # TODO : check if node id is present in the network
        self.structure.node[node_id] = agent
        self.process(agent.run())

    def __delitem__(self, node_id):
        self.structure.remove_node(node_id)


def build_simulation(agent_constructor, env_constructor, structure, state_instance=None, initial_time=0):
    """Creates an environment given a particular structure and populating it with agents and a particular initial state

    Parameter
    ---------
    agent_constructor : BaseAgent class or subclass
    env_constructor : BaseEnvironment class or subclass
    structure : structure object
    initial_state : State object or None, optional (default = None)
    initial_time = int, optional (default = 0)

    Returns
    -------
    Environment object

    """
    # Set-up trial environment
    env = env_constructor(structure=structure, initial_time=initial_time)
    # Populate environment with default agent
    # TODO : pass either a state constructor or an object
    env.populate(agent_constructor, state_instance=state_instance)
    return env