import networkx as nx
import simpy
from .agents import LoggingAgent

class NetworkSimulation(object):
    """NetworkSimulation of agents over any type of networkx graph"""
    def __init__(self, topology=None, agent_type=None, states=(),
                 environment_agent=None, dir_path='sim_01', num_trials=3, max_time=100,
                 **global_params):
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
        global_params : dictionary of globally-shared parameters
        """
        # Check for REQUIRED arguments
        assert topology is not None, TypeError('__init__ missing 1 required keyword argument: \'topology\'')
        assert agent_type is not None, TypeError('__init__ missing 1 required keyword argument: \'agent_type\'')
        assert len(states) != 0, TypeError('__init__ missing 1 required keyword argument: \'states\'')

        self.G = nx.Graph(topology)  # convert to undirected graph
        self.id_counter = len(topology.nodes())
        self.agent_type = agent_type
        self.num_trials = num_trials
        self.until = max_time
        self.dir_path = dir_path
        self.environment_agent_type = environment_agent
        self.global_params = global_params

        # Initial states
        self.initial_topology = self.G.copy()
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
        self.env = simpy.Environment()
        self.G = self.initial_topology.copy()
        self.trial_params = self.global_params.copy()

        # Set up agents on nodes
        print('Setting up agents...')
        self.setup_network_agents()

        # Set up environmental agent
        if self.environment_agent_type:
            env_agent = self.environment_agent_type(simulation=self)
            self.env.process(env_agent.run())

        # Set up logging
        logging_interval = 1
        logger = LoggingAgent(simulation=self, dir_path=self.dir_path, logging_interval=logging_interval)

        # Run trial
        self.env.run(until=self.until)

        # Save output as pickled objects
        logger.log_trial_to_files(trial_id)

    def setup_network_agents(self):
        """Initializes agents on nodes of graph and registers them to the SimPy environment"""
        for i in self.G.nodes():
            agent = self.agent_type(environment=self.env, agent_id=i, state=self.initial_states[i],
                                    global_topology=self.G, global_params=self.global_params)
            self.G.node[i]['agent'] = agent
            self.env.process(agent.run())