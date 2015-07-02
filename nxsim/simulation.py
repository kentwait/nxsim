import networkx as nx
from copy import deepcopy
from .agents import BaseLoggingAgent
from .agents import NetworkEnvironment

class NetworkSimulation(object):
    """NetworkSimulation of agents over any type of networkx graph"""
    def __init__(self, topology=None, agent_type=None, states=(),
                 environment_agent=None, dir_path='sim_01', num_trials=3, max_time=100, logging_interval=1.0,
                 **environment_params):
        """
        Parameters
        ---------
        topology : networkx.Graph instance
        agent_type : NetworkAgent subclass
            Agents will be instantiated using this agent class for each node on the graph
        states : list
            List of initial states corresponding to the nodes in the topology. Basic form is a list of integers
            whose value indicates the state

        environment_agent: NetworkAgent subclass, optional
            Agent that controls the environment
        dir_path : str, optional
            Directory path where to save pickled objects
        num_trials : int, optional
            Number of independent simulation runs
        max_time : int, optional
            Time how long the simulation should run
        environment_params : dictionary of globally-shared environmental parameters
        """
        # Check for REQUIRED arguments
        assert topology is not None, TypeError('__init__ missing 1 required keyword argument: \'topology\'')
        assert agent_type is not None, TypeError('__init__ missing 1 required keyword argument: \'agent_type\'')
        assert len(states) != 0, TypeError('__init__ missing 1 required keyword argument: \'states\'')

        self.G = nx.Graph(topology)  # convert to undirected graph
        self.agent_type = agent_type
        self.num_trials = num_trials
        self.until = max_time
        self.dir_path = dir_path
        self.environment_agent_type = environment_agent
        self.environment_params = environment_params
        self.logging_interval = logging_interval

        # Initial states
        # self.initial_topology = self.G.copy()
        self.initial_states = states

    def run_simulation(self):
        """Runs the complete simulation"""
        print('Starting simulations...')
        for i in range(self.num_trials):
            print('---Trial {}---'.format(i))
            self.run_trial(i)
        print('Simulation completed.')

    def run_trial(self, trial_id=0):
        """Run a single trial of the simulation

        Parameters
        ----------
        trial_id : int
        """
        # Set-up trial environment and graph
        self.env = NetworkEnvironment(self.G.copy(), initial_time=0, **self.environment_params)
        # self.G = self.initial_topology.copy()
        # self.trial_params = deepcopy(self.global_params)

        # Set up agents on nodes
        print('Setting up agents...')
        self.setup_network_agents()

        # Set up environmental agent
        if self.environment_agent_type:
            env_agent = self.environment_agent_type(environment=self.env)

        # Set up logging
        logging_interval = self.logging_interval
        logger = BaseLoggingAgent(environment=self.env, dir_path=self.dir_path, logging_interval=logging_interval)

        # Run trial
        self.env.run(until=self.until)

        # Save output as pickled objects
        logger.save_trial_state_history(trial_id=trial_id)

    def setup_network_agents(self):
        """Initializes agents on nodes of graph and registers them to the SimPy environment"""
        for i in self.env.G.nodes():
            self.env.G.node[i]['agent'] = self.agent_type(environment=self.env, agent_id=i,
                                                          state=deepcopy(self.initial_states[i]))