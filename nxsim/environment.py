import simpy
import networkx as nx

class NetworkEnvironment(simpy.Environment):
    """Subclass of simpy.Environment that uses a graph to control the spatial configuration of agent processes.

    Parameters
    ---------
    topology : Networkx Graph
    initial_time : int
    """
    def __init__(self, topology, initial_time=0, **environment_params):
        super().__init__(initial_time=initial_time)
        assert isinstance(topology, nx.Graph)
        self.G = nx.Graph(topology)  # converts to undirected graph

        self.environment_params = environment_params  # aka "global_params"
