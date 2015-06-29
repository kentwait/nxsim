import os
import glob
import networkx as nx
from pickle import Pickler, Unpickler
from .constants import *


class LogOpeningError(Exception):
    """Error when trying to open multiple simulation logs"""
    def __init__(self, value, logs):
        self.value = value
        self.log = logs

    def __str__(self):
        return repr(self.value)


def create_copy_without_data(G):
    """Return a copy of the graph G with all the data removed"""
    H = nx.Graph()
    for i in H.nodes_iter():
        H.node[i] = {}
    return H

def make_filename(path, trial_id, suffix):
    return os.path.join(path, '{basename}_{trial_id}_{suffix}.{pickle_extension}'.format(
        basename=BASE_FILENAME, trial_id=trial_id, suffix=suffix, pickle_extension=PYTHON_PICKLE_EXTENSION,)
    )

def make_state_filename(path, trial_id):
    return make_filename(path, trial_id, STATE_SUFFIX)

def make_state_vector_filename(path, trial_id):
    return make_filename(path, trial_id, STATE_VECTOR_SUFFIX)

def make_topo_filename(path, trial_id):
    return make_filename(path, trial_id, TOPO_SUFFIX)

def retrieve_trial(path, trial_id):
    """Retrieve states, topologies and statevectors stored in a given path"""
    states = retrieve(make_state_filename(path, trial_id))
    topos = retrieve(make_topo_filename(path, trial_id))
    return states, topos

def retrieve_all_trials(path):
    """Retrieves all trials found inside a directory"""
    states = list()
    topos = list()
    for f in glob.glob(os.path.join(path, '*{}'.format(PYTHON_PICKLE_EXTENSION))):
        if STATE_SUFFIX in f:
            states.append(f)
        elif TOPO_SUFFIX in f:
            topos.append(f)
    state_list = [retrieve(f) for f in states]
    topo_list = [retrieve(f) for f in topos]
    return state_list, topo_list

def retrieve(filename):
    """Retrieve a pickled object"""
    filename = os.path.normcase(filename)
    try:
        with open(filename, 'rb') as f:
            u = Unpickler(f)
            return u.load()
    except IOError:
        raise LogOpeningError('No file found for %s' % filename, filename)

def log_to_file(stuff, filename, verbose=True):
    """Store an object to file by pickling"""
    filename = os.path.normcase(filename)
    dir_path = os.path.dirname(filename)
    if not os.path.exists(dir_path): os.makedirs(dir_path)
    with open(filename, 'wb') as f:
        p = Pickler(f, protocol=2)
        p.dump(stuff)
    if verbose:
        print('Written {} items to pickled binary file: {}'.format(len(stuff), filename))
    return filename

def log_all_to_file(states=(), topos=(), dir_path='sim_01', trial_id=0):
    """Stores states, topologies, and state vectors as pickled files"""
    log_to_file(states, make_state_filename(dir_path, trial_id))
    log_to_file(topos, make_topo_filename(dir_path, trial_id))
