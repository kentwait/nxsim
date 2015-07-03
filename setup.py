from distutils.core import setup

setup(
    # nxsim:
    name = 'nxsim',

    # Version number:
    version = '0.1.2',

    # Application author details:
    author = 'Kent Kawashima',
    author_email = 'i@kentwait.com',

    # Package
    packages = ['nxsim'],
    url = 'http://pypi.python.org/pypi/nxsim',
    license = 'LICENSE',
    description = 'Nxsim is a Python package for simulating agents connected by any type of network using SimPy ' \
                  'and Networkx in Python 3.4.',

    # Dependent packages
    requires = [
        'simpy',
        'networkx',
    ],

)