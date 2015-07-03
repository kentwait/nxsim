# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org).

## Unreleased
#### Added
- CHANGES.txt that summarizes changes more succinctly than git log.
- LICENSE.txt now reflects Apache license.
- setup.py for PyPI distribution
- environment.py containing subclass of simpy.Environment
#### Changed
- environment.NetworkEnvironment is now used to start a new SimPy environment instead of simpy.Environment.
- Refactored graph from simulation.NetworkSimulation.G to environment.NetworkEnvironment.G
#### Fixed
- agents.BaseLoggingAgent now records events accurately. Problem was passed states copy was also updating.
- Events from agents.BaseEnvironmentAgent are not duplicated anymore. Removed duplicate .process that registers the
  agent twice.

## [0.1.1] - 2015-07-01
- Working version using a dictionary or any subscriptable type as state
#### Changed
- Renamed agents.LoggingAgent to agents.BaseLoggingAgent to promote subclassing.
#### Fixed
- States are no longer limited to integers. States can be any object as long as it is subscriptable with an "id" key.

## [0.1.0] - 2015-06-30
- Working version using integer states.
#### Added
- Added State namedtuple declaration inside agents.BaseAgent.
- Added assertions to make "required" keyword arguments.
- agent.BaseAgent class for making node agents.
#### Changed
- simulation.NetworkSimulation.addNewNode is not part of agents.BaseEnvironmentAgent.
- Changed attribute, method and function names from CamelCaps to underscore_separated.
- Refactored logging.Logger into agents.LoggingAgent. Deleted logging.py

## Initial commit
#### Added
- README contains short inital description of the project
- Forked from ComplexNetworkSim [https://github.com/jschaul/ComplexNetworkSim]