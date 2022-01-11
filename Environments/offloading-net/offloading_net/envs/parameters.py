# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 16:44:33 2021

@author: Mieszko Ferens
"""

import pandas as pd
import networkx as netx
from itertools import product

path_to_env = '../Environments/offloading-net/offloading_net/envs/'

### Parameters for computation offloading in a network environment

## Network topology

# Choose network topology
try:
    state_file = open(path_to_env + "net_topology", "rt")
    topology = state_file.read() # Defined from main
    state_file.close()
except:
    topology = 'network_branchless.csv' # Default for single simulation testing

# Links and bitrate/delay of each link (loaded from .csv)
data = pd.read_csv(path_to_env + topology)
links = data[['original', 'connected']].values.tolist()
links_rate = data['bitrate'].values.tolist()
links_delay = data['delay'].values.tolist()

# Get parameters for nodes in the network (loaded from .csv)
data = pd.read_csv(path_to_env + 'network_branchless_nodes.csv') # TODO Falta la definición dinámica del nombre
node_type = data['type'].values.tolist()
node_clock = data['clock'].values.tolist()
node_cores = data['cores'].values.tolist()

# Get definided applications (loaded from .csv)
data = pd.read_csv(path_to_env + 'app_definition.csv')
apps = data['app'].values.tolist()
app_cost = data['cost'].values.tolist()
app_data_in = data['data_in'].values.tolist()
app_data_out = data['data_out'].values.tolist()
app_max_delay = data['max_delay'].values.tolist()
app_rate = data['rate'].values.tolist()
app_info = data['info'].values.tolist()

# Count network nodes (with and without vehicles, marked as type 4)
n_nodes = len(node_type)
net_nodes = sum(map(lambda x : x<4, node_type))

## Precalculated routes

# Definition of network so paths can be calculated
net = netx.Graph()
net.add_edges_from(links)

# Find vehicle nodes and non-vehicle nodes
sources = [node+1 for node, n_type in enumerate(node_type) if n_type == 4]
targets = [node+1 for node, n_type in enumerate(node_type) if n_type != 4]

# Calculate all necessary combinations of nodes (from each vehicle to other)
node_comb = product(sources, targets)
node_comb = list(map(lambda x : list(x), node_comb))
for i in node_comb: i.sort()

# Precalculation of routes
all_paths = []
for pair in node_comb:
    all_paths.append(netx.shortest_path(net, pair[0], pair[1]))

