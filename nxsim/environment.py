import simpy
import networkx as nx
from copy import deepcopy

class BaseEnvironment(simpy.Environment):
    """The environment behaves like a dictionary of agents.

    In BaseEnvironment, there is no positional structure to the arrangement of the agents, so the agents are stored as
    a key-value pair in a dictionary. The key corresponds to an arbitrary label for the agent for easy retrieval.

    Parameters
    ----------
    initial_time : int
        Specifies the time unit to start with, inherited from simpy.Environment
    """
    def __init__(self, initial_time=0):
        # Properties
        self._agents = None

        super().__init__(initial_time=initial_time)
        self.structure = dict()

    @property
    def agents(self):
        return self._agents

    @agents.getter
    def agents(self):
        return self.structure.values()

    def current(self):
        """
        Return a snapshot of the current state of the entire simulation environment.
        """
        return deepcopy(self)

    def __len__(self):
        """Returns number of agents registered in the environment"""
        return len(self.structure)

    def __contains__(self, agent):
        """Returns True if the agent is registered in this environment"""
        return any(a is agent for a in self.agents)

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
    def __init__(self, graph, initial_time=0):
        super().__init__(initial_time=initial_time)
        assert isinstance(graph, nx.Graph)
        self.structure = nx.Graph(graph)  # converts to undirected graph

    @property
    def agents(self):
        return self._agents

    @agents.getter
    def agents(self):
        return [self.structure.node[i]['agent'] for i in self.structure.nodes()]

    def list(self, state=None):
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
            return [agent for agent in self.agents if agent.state is state]

    def __len__(self):
        """Returns number of agents registered in the environment"""
        return len(self.agents)

    def __contains__(self, agent):
        """Returns True if the agent is registered in this environment"""
        return any(a.uid == agent.uid for a in self.agents)

    def __getitem__(self, node_id):
        """Returns the agent given its associated node ID"""
        return self.structure.node[node_id]['agent']

    def __setitem__(self, node_id, agent):
        # TODO : check if node id is present in the network
        self.structure[node_id]['agent'] = agent
        self.process(agent.run())

    def __delitem__(self, node_id):
        self.structure.remove_node(node_id)