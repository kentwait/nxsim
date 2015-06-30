import os
import networkx as nx
import pickle

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

# Storing and retrieving objects

def dump(stuff, filename, verbose=True, protocol=3):
        """Store an object to file by pickling

        Parameters
        ----------
        stuff : object to be pickled
        filename : path
        verbose : bool
        protocol : 1,2,3 (default = 3)
            Protocol used by Pickler, higher number means more recent version of Python is needed to read the pickle
            produced. Default is protocol=3, which only works with Python 3+

        Return
        ------
        path
            Path where pickled object was saved.
        """
        filename = os.path.normcase(filename)
        dir_path = os.path.dirname(filename)
        if not os.path.exists(dir_path): os.makedirs(dir_path)
        with open(filename, 'wb') as f:
            p = pickle.Pickler(f, protocol=protocol)
            p.dump(stuff)
        if verbose:
            print('Written {} items to pickled binary file: {}'.format(len(stuff), filename))
        return filename

def load(filename):
    """Retrieve a pickled object

    Parameter
    ---------
    filename : path

    Return
    ------
    object
        Unpickled object
    """
    filename = os.path.normcase(filename)
    try:
        with open(filename, 'rb') as f:
            u = pickle.Unpickler(f)
            return u.load()
    except IOError:
        raise LogOpeningError('No file found for %s' % filename, filename)
