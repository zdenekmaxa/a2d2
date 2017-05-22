# Prototype of A2D2 (An ATLAS Dataflow Display) 

Implementation of monitoring of ROS (Read-Out System) based on values 
retrieved from the IS (TDAQ CORBA Information System) and a
set of criteria according to the specification document.

ATLAS TDAQ (Trigger Data Acquisition) systems monitor and expert knowledge
base tool.

## Howto

Running at ATLAS P1:

- need to set up TDAQ release (e.g. by sourcing `/sw/atlas/tdaq/tdaq-02-00-02/installed/setup.sh`
  so that `tdaq_python` is available on the command line

- `tdaq_python a2d2.py --help`

- edit config file `Config.py`

- edit ROS criteria configuration: `ros/RosCriteriaConfig.py`


## Development

```
python a2d2.py --help
python a2d2.py --mode devel
cd test ; py.test test_RosTree.py
```

Input data are randomly simulated in the development mode rather than read
from the TDAQ IS database.


## General notes

2009-06-03 concluded on expoloring DQM (DQMF/DQMD) tools to serve requirements
for future `A2D2` application. Requirements specified for the ROS part are
easily achievable in DQMF/DQMD (just matter of creating corresponding
appropriate configuration) according to DQM experts.

2009-07-01 this prototype application is complete and functional for ROS part.

## TODO

- `RosCriteriaConfig` class (criteria definition) done in some interoperable
    format (like JSON) (perhaps could still use Python string interpolation)

- criteria file reloaded when modified (test performed before each IS polling),
    criteria (resp. values) could even be modified from within the application

- better, coloured ROB view (now showing all criteria results in simple form)

- once the application is started, it retrieves names of DF objects (keys)
    from IS. During subsequent checks, these keys are checked if still present
    in the IS, but if new appears (systems integrated to the partition), it is
    not propagated into `a2d2` hierarchical (tree) structure of names.
    It could update the tree (names in the tree) in the
    `RosIsRetriever.py` class instance (likely in
    `propagateStatesFromLeavesUp()`).
    Also, when partition is restarted, `a2d2` application currently needs to be
    restarted as well.

Future development depends on availability of Python interface for other
    sources of information: MRS (Message Reporting System - C++/CORBA) -
    exists, OKS database - exists, cabling database - not sure if Python
    connector exists.

