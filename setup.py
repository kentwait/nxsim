from distutils.core import setup

setup(
    # nxsim:
    name = 'NxSim',

    # Version number:
    version = '0.1.2',

    # Application author details:
    author = 'Kent Kawashima',
    author_email = 'i@kentwait.com',

    # Package
    packages = ['nxsim'],
    include_package_data = True,
    url = '',
    license = 'LICENSE.txt',
    description = '',

    # Dependent packages
    install_requires = [
        'simpy',
        'networkx',
    ],

)