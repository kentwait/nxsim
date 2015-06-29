from collections import namedtuple

# Agent constants
SEED = 123456789

# Logging constants
PYTHON_PICKLE_EXTENSION = 'pickled'
TOPO_SUFFIX = 'topology'
STATE_SUFFIX = 'states'
STATE_VECTOR_SUFFIX = 'statevectors'
BASE_FILENAME = 'log_trial'

# NamedTuples
StateTuple = namedtuple('StateTuple', 'time states')
TopologyTuple = namedtuple('TopologyTuple', 'time topology')