import os
import random
from copy import deepcopy
from collections import OrderedDict
from .constants import *
from .environment import NetworkEnvironment
from . import utils


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
        # Initialize agent parameters
        self.uid = uid
        self.name = name
        self.description = description
        self.state = state  # state machine - can only have one state at a time
        self.env = None
        if environment: self.register(environment)

    def run(self):
        """Subclass must specify a generator method!"""
        raise NotImplementedError(self)

    def register(self, environment):
        self.env = environment
        self.env.process(self.run())

    def kill(self):
        pass

class BaseSpatialAgent(BaseAgent):
    def __init__(self, uid, environment=None, **kwargs):
        super().__init__(uid, environment=environment, **kwargs)
        self.position = None

    def adjacent_agents(self, radius_limit=10, state=None):
        pass

    def kill(self):
        pass


class BaseNetworkAgent(BaseAgent):
    def __init__(self, uid, environment=None, **kwargs):
        super().__init__(uid, environment=environment, **kwargs)
        self.node = None

    def adjacent_agents(self, state=None):
        pass

    def register(self, environment, node):
        super().register(environment)
        self.env.add_agent(self, node)

    def kill(self):
        # TODO : remove self, remove from graph
        pass

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


class State(object):
    """
    A state is an encapsulation of a behavior to be associated with an agent.
    """
    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    def run(self):
        """
        Behavior when the agent is in the active state during one time unit.
        """
        # Add custom behavior here.
        # For example, while infected, do intrahost evo
        return NotImplementedError()