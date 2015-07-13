import simpy
import networkx as nx

class Environment(simpy.Environment):
    def current(self):
        """
        Return a snapshot of the current state of the entire simulation environment.
        """
        pass

    def list_agents(self):
        pass

    def list_all_agents(self):
        pass

    def add_agent(self, agent):
        pass

    def remove_agent(self, agent):
        pass

    def __contains__(self, agent):
        pass


class SpatialEnvironment(Environment):
    def __init__(self, dimensions, initial_time=0, **environment_params):
        super().__init__(initial_time=initial_time)
        self.structure = dimensions  # sparse matrix?


class NetworkEnvironment(Environment):
    """Subclass of simpy.Environment that uses a graph to control the spatial configuration of agent processes.

    Parameters
    ---------
    topology : Networkx Graph
    initial_time : int
    """
    def __init__(self, graph, initial_time=0, **environment_params):
        super().__init__(initial_time=initial_time)
        assert isinstance(graph, nx.Graph)
        self.structure = nx.Graph(graph)  # converts to undirected graph
        self.agents = []

    def list_agents(self):
        pass

    def list_all_agents(self):
        pass

    def add_agent(self, agent, node):
        pass

    def remove_agent(self, agent):
        pass

    def __contains__(self, agent):
        return any(agent.uid == a.uid for a in self.agents)