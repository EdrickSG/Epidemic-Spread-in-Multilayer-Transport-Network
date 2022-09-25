import logging
from typing import Dict, List, Any, Set
import numpy as np
import random as rm
import networkx as nx
from Population import MetroArea, City


def create_metro_networks(metro_data: 'np.array', graph_generator: 'nx.function', dict_pops: Dict):
    metro_networks = set({})

    # Creation
    for metro in metro_data:
        G = graph_generator(len(dict_pops[int(metro[0])]))
        G.graph['real_index'] = int(metro[0])
        G.graph['name'] = metro[1]
        G.graph['population'] = sum(dict_pops[int(metro[0])])
        metro_networks.add(G)

    # Node Attributes
    for network in metro_networks:
        for city in list(network.nodes()):
            network.nodes[city]['population'] = dict_pops[network.graph['real_index']][city]
            network.nodes[city]['name'] = network.graph['name'] + str(city)

    # Edge Attributes
    for network in metro_networks:
        highest_population = max([int(network.nodes[n]['population']) for n in network.nodes()])
        total_cities = network.number_of_nodes()
        for idx, edge in enumerate(network.edges):
            neighbor_number_I = len(list(network.neighbors(edge[0])))
            neighbor_number_II = len(list(network.neighbors(edge[1])))
            neighbor_number = np.mean([neighbor_number_I,neighbor_number_II])
            edge_value = np.round(network.nodes[edge[0]]['population'] * network.nodes[edge[1]]['population']*.25 / (
                    highest_population))
            if edge_value == 0:
                edge_value = 1  # Minimum edge value: 1
                logging.warning(
                    f'Edge in metro {network.graph["name"]} between cities {edge[0]} and {edge[1]} set to 1')
            network[edge[0]][edge[1]]['passengers'] = edge_value

    return metro_networks


def from_networks_to_populations(metro_networks: Set['networkx']):
    metro_areas_set = set({})

    for metro_net in metro_networks:
        cities_set = set({})
        for city_node_idx in metro_net.nodes():
            cities_set.add(City(metro_net.nodes[city_node_idx]['name'], city_node_idx,
                                [int(metro_net.nodes[city_node_idx]['population']), 0, 0], [.3, .035]))
        metro_areas_set.add(
            MetroArea(metro_net.graph['name'], int(metro_net.graph['real_index']), cities_set, metro_net))

    return metro_areas_set


def create_airport_network(weighted_connections, weight_multiplication_factor=180):
    weighted_connections = weighted_connections.astype(int)
    edges_set = [(triple[0], triple[1], {'passengers': triple[2] * weight_multiplication_factor}) for triple in
                 weighted_connections]
    network = nx.DiGraph()
    network.add_edges_from(edges_set)
    return network
