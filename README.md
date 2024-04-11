# STEROCEN

Simulation and Training Environment for Resource Orchestration in Cloud-Edge Networks.

## Description

This code provides a simulation tool for Edge-Cloud networks for training and testing different orchestration policies.

### Network

The simulator defines a hierarchical network based on four layers: (1) Cloud, (2) far Edge, (3) close Edge, and (4) end-devices.
Each layer is provided one or more nodes with pre-defined:
- Number of CPU cores (can process a single task at a time)
- Clock speed (applied to all CPU cores on the node)
- Queue size (determines how many task can be queued for a single CPU core)

The Cloud layer is exceptional in that it emulates a virtually infinite computational cluster, meaning that it always is assumed to have infinite CPU cores, making queue sizes irrelevant. For this reason it is defined a single node.

The end-devices also have a special characteristic in that each end-device node is actually a group of end-devices (e.g., 10 independent devices).

The network is interconnected through bidirectional communication links with pre-defined transmission and propagation delays.
Note that direct links between nodes that are not in neighbouring layers is not permitted, and that end-device to end-device communicatons are not consired in this simulator.
Each individual device from an end-device node is assumed to have its communication link as defined by the end-device node to close Edge node.

### Traffic

Traffic in the network takes the form of computational tasks generated from independent instances of pre-defined applications with certain parameter and latency requirements.
Based on a set of applications, each independent end-device (in each end-device node) run a single instance of all defined applications.
The applications are defined with the following parameters:
- Processing cost (CPU cycles per bit of input package)
- Input package size
- Output package size
- Max latency (tolerable latency to receive the output package at the source of the input package)
- Avg. inter-package time (mean of the Poisson distribution that determines when the next package will be generated)
- Priority (Weight of the application relative to others)

This is an event simulator which expects an offloading decision (which node should compute a certain computational task) fo each request generated by each application instance.
Every computational task that is generated at random time intervals (following a Poisson distribution) is akin to a request.
These requests define the events of the simulations, i.e., the time steps.
Thus, at each time step, the tool provides an observation of the current situation in the environment and expects an offloading decision to be provided.

### Orchastrator-network interface

The offloading decision is simply an integer (ID of node) that selects which node should handle the task.
Note that other end-devices are excluded from being selectable for offloading.
The observation provides the following information:
- Availability of all CPU cores of all nodes that can compute the task (ratio of free space in the queue)
- Normalized application parameters (relative to the highest value in the set)
- Estimated delay of offloading to all nodes that can compute the task (not acounting for queue times and processing uncertainty)
- Location of the source end-device (which close Edge it is connected to)

Additionally, at each time step the simulator provides a reward that may be used as a performance metric for, e.g., training Machine Learning (ML) algorithms.
There are two supported metrics:
- Penalty reward:
  - If unprocessed (discarted in queue of node): -1000
  - If output package did arrive to source in time: -100-(*time over max latency*)
  - If output package did arrive to source within max latency: 0
- Weighted binary reward:
  - If output package did arrive to source within max latency: +*priority*
  - If output package did not arrive to source within max latency: -*priority*

## How to use

### Creating a simulation

To create an instance of the simulation environment use the Python package in the Environments directory defined as a Gym environment:
```
env = gym.make('offloading_net:offloading-planning-v1')
```
There are four environment types you may use:
```
offloading-noplanning-v0
offloading-noplanning-v1
offloading-planning-v0
offloading-planning-v1
```
The "planning" and "noplanning" keyworks refer to whether you wish for the queues of the CPU cores of the nodes to use a best effort void-filling technique when scheduling new tasks or to simply place them at the end of queues.
In both cases, the nodes will attempt to minimize queue time given the specific scheduling rules.
Meanwhile, "v0" and "v1" refer to penalty and weighted binary rewards, respective.
Of course, you may choose to ignore these rewards in your oschatrator, in which case it makes no difference.

### Running a simulation

At the start or to reset the simulation environment (starting state is empty queues) use `env.reset()`.
For each time step use `env.step(action)`, which takes an integer as an input (node ID) and returns a tuple with observation (array), reward (float), final state, and additional information.
Please note that this complies with the definition of environments in the OpenAI Gym library, but in this simulator there is no final state (always equal to *False*), and the additional information field is always empty.

### Collecting data

Data collection is facilited through access to variables in the environment instance, as well as some methods.
The methods you can use to obtain information are:
- `render()`: Returns a string with information from the current observation.
- `get_path(action)`: Returns an array with the link IDs that form the shortest path (in number of hops) from current source of request to node referred to by action (node ID).
- `calc_delays(action, path)`: Returns the delays in milliseconds for transmitting the input and output packets from and to the end-device, and for estimated processing time.

Apart from these methods, you can access all variables in the environment instance, including: network node and link IDs; current request information; node, link and appication parameters; shortest paths through the network; CPU queues; number of end-devices; and future events (computational tasks that will be generated in the future).

### Orchestrator definition

The orchestrators to be used with the simulation environment are user-defined.
Here we provide some example scripts for running simulations using some heuristic algorithms and Deep Reinforcement Learning (DRL) algorithms.
These can be found in the "Offloading" directory and have the following scripts:
- `offloader.py`: Script to train some DRL agents (DDQN, SARSA, PAL, and TRPO algorithms) as orchestrators, and test them against four heuristics algorithms.
- `parametric_sim.py`: Script to run `offloader.py` with varying simulation parameters, e.g., number of end-device nodes.
- `heuristic_algorithms.py`: Script that defines classes for the four heuristic algorithms:
  - Local Processing: Always offloads to source end-device.
  - Cloud Processing: Always offloads to Cloud layer node.
  - Uniform Distribution: Offloads to all layers (assuming only one node in the Edge and Cloud layers) with equal probability.
  - Max Distance: Offloads as high in the network hierarchy (assuming only one node in the Edge and Cloud layers) based on the estimated total delay provided by the observation.
- `agent_creator.py`: Script that defines methods for creating a data array with many DRL agents to be used in the `offloader.py` script.
- `graph_creator.py`: Script that defines methods for making plots used by the `parametric_sim.py` script.
- `create_<algorithm>_set.py`: Script that defines a class and method for instanciating a DRL agent using *<algorithm>*:
  - The options are: DQN, DDQN, CategoricalDQN, CategoricalDDQN, ResidualDQN, IQN, DoubleIQN, DPP, SARSA, AL, PAL, DoublePAL, PCL, REINFORCE, SAC, TD3, TRPO, A3C, PPO, and ACER.
- `agent_set_sim.py`: Script to create a set of agents using `create_<algorithm>_set.py` scripts, and run training and testing using `offloader.py`.

## Dependencies

The network simulation environment was tested using:
- Python 3.8
- gym 0.22.0
- numpy 1.21.5
- networkx 2.7.1
- pandas 1.4.2

Additionally, the example use case using DRL and heuristic algorithms was tested using:
- chainerrl 0.8.0
- matplotlib 3.5.1

## How to cite

M. Ferens et al., "Deep Reinforcement Learning Applied to Computation Offloading of Vehicular Applications: A Comparison," 2022 International Balkan Conference on Communications and Networking (BalkanCom), 2022, pp. 31-35, doi: 10.1109/BalkanCom55633.2022.9900545.

## Other citations

### MS.c. final proyect

This software associated to Mieszko Ferens' TFM on Reinforcement Learning Techniques for Computation Offloading in Connected Vehicle Applications.
An OpenAI Gym custom environment for simulating a MEC (Multi-Access Edge Computing) problem with variables such as network topology and processing noise. Includes scripts for creating, training and testing agents from ChainerRL.

M. Ferens, "Técnicas de Aprendizaje por Refuerzo para la Delegación de Tareas (Computation Offloading) en Aplicaciones de Vehículo Conectado," MS.c. Thesis, 2022, https://uvadoc.uva.es/handle/10324/55582.