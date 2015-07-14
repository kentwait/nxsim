from .agents import BaseAgent
import numpy

class BaseMonitor(object):
    """Monitors agents and the simulation environment"""
    def __init__(self, environment, interval, **kwargs):
        self.env = environment
        self.interval = interval
        self._variables = {k: v for k, v in kwargs.items()}
        self.env.process(self.run())

    def run(self):
        while True:
            # Do omething
            yield self.env.timeout(self.interval)



class StateMonitor(BaseMonitor):
    """Counts the number of states per logging interval
    """
    def __init__(self):
        super().__init__()



class LoggingAgent(BaseAgent)
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