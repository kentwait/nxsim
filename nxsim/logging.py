import networkx as nx
from collections import namedtuple
from . import utils

StateTuple = namedtuple('StateTuple', 'time states')
StateVectorTuple = namedtuple('StateVectorTuple', 'time state_vectors')
TopologyTuple = namedtuple('TopologyTuple', 'time topology')

class Logger(object):
    def __init__(self, env, simulation=None, dir_path='sim_01', logging_interval=1):
        self.sim = simulation
        self.dir_path = dir_path
        self.interval = logging_interval

        self.state_tuples = list()
        self.state_vector_tuples = list()
        # self.topology = nx.Graph()
        self.topology_tuples = list()

        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            self.log_current_state()
            yield self.env.timeout(self.interval)

    def log_current_state(self):
        nodes = self.sim.G.nodes(data=True)
        states = [node[1]['agent'].state for node in nodes]
        state_vectors = [node[1]['agent'].state_vector for node in nodes]

        # log states
        self.state_tuples.append(StateTuple(time=self.env.now, states=states))
        self.state_vector_tuples.append(StateVectorTuple(time=self.env.now, state_vectors=state_vectors))

        # # log new topology if it changed
        # if not nx.fast_could_be_isomorphic(self.topology, nx.Graph(self.G)):
        #     self.topology = utils.create_copy_without_data(self.G)
        #     self.topology_tuples.append(TopologyTuple(time=self.env.now(), topology=self.topology))

    def log_trial_to_files(self, trial_id):
        # if not self.topology_tuples:
        #     self.topology_tuples.append(TopologyTuple(time=0, topology=self.topology))

        # Write states, topologies, and state vectors to file
        # utils.log_all_to_file(self.state_tuples, self.topology_tuples, self.state_vector_tuples,
        #                       self.dir_path, trial_id)
        utils.log_all_to_file(self.state_tuples, self.topology_tuples, self.state_vector_tuples,
                              self.dir_path, trial_id)