import simpy
import networkx as nx

class Environment(simpy.Environment):
    def __init__(self, structure=None, initial_time=0):
        super().__init__(initial_time=initial_time)
        self.structure = structure
        if self.structure: self.build_structure()  # TODO: make a setter method

    def build_structure(self):
        """
        Place agents and resources into the specific structure of the environment
        """
        pass


class NetworkEnvironment(Environment):
    def __init__(self, topology, initial_time=0,):
        super().__init__(structure=topology, initial_time=initial_time)
        assert isinstance(topology, nx.Graph)
        self.G = nx.Graph(topology)  # converts to undirected graph, # TODO: make a setter method


class Structure(object):
    def __init__(self):
        pass