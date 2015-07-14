import os
import random
from copy import deepcopy
from collections import OrderedDict
import networkx as nx
from .constants import *
from .environment import Environment, NetworkEnvironment
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
        # Properties
        self._env = None
        self._state = None

        # Initialize agent parameters
        self.uid = uid
        self.name = name
        self.description = description
        self.state = state  # state machine - can only have one state at a time
        self.env = environment

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

    @env.setter
    def env(self, environment):
        assert isinstance(environment, Environment)
        self._env = environment

    def run(self):
        """Subclass must specify a generator method!"""
        raise NotImplementedError(self)

    def register(self, environment):
        """Register agent to the simulation environment.

        Parameters
        ----------
        environment : Environment object
        """
        self.env = environment
        self.env.process(self.run())

    def kill(self):
        pass


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
        assert isinstance(node, nx.Graph.node)
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
            return [neighbor for neighbor in neighbors if neighbors.state is state]
        else:
            return neighbors

    def register(self, environment, node):
        """Register agent to the network simulation environment.

        Parameters
        ----------
        environment : Environment object
        node : networkx.Graph.node
        """
        super().register(environment)
        self.node = node
        self.env.add_agent(self, node)

    def kill(self):
        # TODO : remove self, remove from graph
        self.env.remove_agent(self.uid)


class BaseSpatialAgent(BaseAgent):
    def __init__(self, uid, environment=None, **kwargs):
        super().__init__(uid, environment=environment, **kwargs)
        self.position = None

    def adjacent_agents(self, radius_limit=10, state=None):
        pass

    def kill(self):
        pass


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