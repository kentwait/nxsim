import os
import random
from copy import deepcopy
from collections import OrderedDict
from .constants import *
from .environment import NetworkEnvironment
from . import utils


class BaseAgent(object):
    #class variables, shared between all instances of this class
    r = random.Random(SEED)
    TIMESTEP_DEFAULT = 1.0

    def __init__(self, environment=None, agent_id=None, state=None,
                 name='network_process', **state_params):
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
        # Check for REQUIRED arguments
        assert environment is not None, TypeError('__init__ missing 1 required keyword argument: \'environment\'. '
                                                  'Cannot be NoneType.')
        # Initialize agent parameters
        self.id = agent_id
        self.state = state
        self.name = name
        self.state_params = state_params

        # Global parameters
        self.global_topology = environment.G
        self.environment_params = environment.environment_params

        # Register agent to environment
        self.env = environment
        self.action = self.env.process(self.run())  # initialize every time an instance of the agent is created

    def run(self):
        """Subclass must specify a generator method!"""
        raise NotImplementedError(self)

    def get_all_nodes(self):
        """Returns list of nodes in the network"""
        return self.global_topology.nodes()

    def get_agents(self, state_id=None, limit_neighbors=False):
        """Returns list of agents based on their state and connectedness

        Parameters
        ----------
        state_id : int, str, or array-like, optional
            Used to select agents that have the same specified "state". If state = None, returns all agents regardless
            of its current state
        limit_neighbors : bool, optional
            Returns agents based on whether they are connected to this agent or not. If limit_neighbors = False,
            returns all agents whether or not it is directly connected to this agent
        """
        if limit_neighbors:
            agents = self.global_topology.neighbors(self.id)
        else:
            agents = self.get_all_nodes()

        if state_id is None:
            return [self.global_topology.node[_]['agent'] for _ in agents]  # return all regardless of state
        else:
            return [self.global_topology.node[_]['agent'] for _ in agents
                    if self.global_topology.node[_]['agent'].state['id'] == state_id]

    def get_all_agents(self, state_id=None):
        """Returns list of agents based only on their state"""
        return self.get_agents(state_id=state_id, limit_neighbors=False)

    def get_neighboring_agents(self, state_id=None):
        """Returns list of neighboring agents based on their state"""
        return self.get_agents(state_id=state_id, limit_neighbors=True)

    def get_neighboring_nodes(self):
        """Returns list of neighboring nodes"""
        return self.global_topology.neighbors(self.id)

    def get_agent(self, agent_id):
        """Returns agent with the specified id"""
        return self.global_topology.node[agent_id]['agent']

    def remove_node(self, agent_id):
        """Remove specified node from the network

        Parameters
        ----------
        agent_id : int

        """
        self.global_topology.remove_node(agent_id)

    def die(self):
        """Remove this node from the network"""
        self.remove_node(self.id)


class BaseNetworkAgent(BaseAgent):
    def __init__(self, environment=None, agent_id=None, state=None,
                 name='network_agent', **state_params):
        assert agent_id is not None, TypeError('__init__ missing 1 required keyword argument: \'agent_id\'. '
                                               'Cannot be NoneType.')
        assert state is not None, TypeError('__init__ missing 1 required keyword argument: \'state\'. '
                                            'Cannot be NoneType.')
        super().__init__(environment=environment, agent_id=agent_id, state=state,
                         name=name, **state_params)


class BaseEnvironmentAgent(BaseAgent):
    """Base class for environment agents

    Parameters
    ----------
    simulation : NetworkSimulation class
    name : str, optional
        Descriptive name for the environment agent
    state_params : keyword arguments, optional

    """

    def __init__(self, environment=None, name='environment_process', **state_params):
        assert isinstance(environment, NetworkEnvironment)
        super().__init__(environment=environment, agent_id=None, state=None,
                         name=name, **state_params)

    def add_node(self, agent_type=None, state=None, name='network_process', **state_params):
        """Add a new node to the current network

        Parameters
        ----------
        agent_type : NetworkAgent subclass
            Agent in the new node will be instantiated using this agent class
        state : object
            State of the Agent, this may be an integer or string or any other
        name : str, optional
            Descriptive name of the agent
        state_params : keyword arguments, optional
            Key-value pairs of other state parameters for the agent

        Return
        ------
        int
            Agent ID of the new node
        """
        agent_id = int(len(self.global_topology.nodes()))
        agent = agent_type(self.env, agent_id=agent_id, state=state, name=name, **state_params)
        self.global_topology.add_node(agent_id, {'agent': agent})
        return agent_id


    def add_edge(self, agent_id1, agent_id2, edge_attr_dict=None, *edge_attrs):
        """
        Add an edge between agent_id1 and agent_id2. agent_id1 and agent_id2 correspond to Networkx node IDs.

        This is a wrapper for the Networkx.Graph method `.add_edge`.

        Agents agent_id1 and agent_id2 will be automatically added if they are not already present in the graph.
        Edge attributes can be specified using keywords or passing a dictionary with key-value pairs

        Parameters
        ----------
        agent_id1, agent_id2 : nodes
            Nodes (as defined by Networkx) can be any hashable type except NoneType
        edge_attr_dict : dictionary, optional (default = no attributes)
            Dictionary of edge attributes. Assigns values to specified keyword attributes and overwrites them if already
            present.
        edge_attrs : keyword arguments, optional
            Edge attributes such as labels can be assigned directly using keyowrd arguments
        """
        if agent_id1 in self.global_topology.nodes(data=False):
            if agent_id2 in self.global_topology.nodes(data=False):
                self.global_topology.add_edge(agent_id1, agent_id2, edge_attr_dict=edge_attr_dict, *edge_attrs)
            else:
                raise ValueError('\'agent_id2\'[{}] not in list of existing agents in the network'.format(agent_id2))
        else:
            raise ValueError('\'agent_id1\'[{}] not in list of existing agents in the network'.format(agent_id1))

    def log_topology(self):
        return NotImplementedError()


# CHANGE LOGGING BEHAVIOR BECAUSE IT DOES NOT WORK!
class BaseLoggingAgent(BaseAgent):
    """Log states of agents and graph topology

    Parameters
    ----------
    environment : NetworkEnvironment instance
    dir_path : directory path, str, optional (default = 'sim_01')
    logging_interval : int, optional (default = 1)
    base_filename : str, optional
    pickle_extension : str, optional
    state_history_suffix : str, optional

    """
    def __init__(self, environment=None, dir_path='sim_01', logging_interval=1,
                 base_filename='log', pickle_extension='pickled', state_history_suffix='states'):
        super().__init__(environment=environment, agent_id=None, state=None, name='network_process')
        self.interval = logging_interval
        self.dir_path = dir_path
        self.basename = base_filename
        self.pickle_ext = pickle_extension
        self.state_history_suffix = state_history_suffix

        self.state_history = OrderedDict()
        # self.topology_history = list()  # not implemented

        # Initialize process
        self.env = environment
        self.action = self.env.process(self.run())

        # Global parameters
        self.global_topology = environment.G
        self.environment_params = environment.environment_params

    def run(self):
        while True:
            nodes = self.global_topology.nodes(data=True)
            self.state_history[self.env.now] = {i: deepcopy(node[1]['agent'].state) for i, node in enumerate(nodes)}
            yield self.env.timeout(self.interval)

    def save_trial_state_history(self, trial_id=0):
        assert trial_id is not None, TypeError('missing 1 required keyword argument: \'trial_id\'. '
                                               'Cannot be set to NoneType')
        utils.dump(self.state_history,
                   self.make_state_filename(dir_path=self.dir_path, basename=self.basename, trial_id=trial_id,
                                            pickle_extension=self.pickle_ext)
        )

    @staticmethod
    def open_trial_state_history(dir_path='.', basename='log', trial_id=0, pickle_extension='pickled'):
        return utils.load(BaseLoggingAgent.make_state_filename(dir_path, basename=basename, trial_id=trial_id,
            pickle_extension=pickle_extension))

    @staticmethod
    def make_filename(dir_path='.', basename='log_trial', trial_id=0, suffix='states', pickle_extension='pickled'):
        return os.path.join(dir_path, '{basename}.{trial_id}.{suffix}.{pickle_extension}'.format(
            basename=basename, trial_id=trial_id, suffix=suffix, pickle_extension=pickle_extension,)
        )

    @staticmethod
    def make_state_filename(dir_path='.', basename='log', trial_id=0, pickle_extension='pickled'):
        return os.path.join(dir_path, '{basename}.{trial_id}.{suffix}.{pickle_extension}'.format(
            basename=basename, trial_id=trial_id, suffix='state', pickle_extension=pickle_extension,)
        )