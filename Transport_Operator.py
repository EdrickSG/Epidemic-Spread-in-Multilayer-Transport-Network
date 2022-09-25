from typing import Dict, List, Any, Set
import numpy as np
import Population
import logging
import networkx as nx
import random as rm


def compute_travelers(population: Population, dt: float):
    """
    Computes the number of S/I/R that travel from population to its corresponding neighbors
    :param population: Origin of travelers
    :param dt:
    :return: Dictionary with keys {S,I,R} and dictionaries of the form {neighbor : #people travelling to neighbor} as values.
    E.g., {S:{city1: 10, city2: 5}, I: {city1: 0, city2: 3}, R:{city1: 10, city2: 20}}
    """
    travel_probabilities = np.zeros(
        len(population.connections) + 1)  # The last entry is to set the probability of non-travelers
    listed_connections = list(
        population.connections.items())  # The order of this list will be used to identify the neighbors
    for idx, pair in enumerate(listed_connections):
        _, passenger_number = pair
        travel_probabilities[
            idx] = passenger_number * dt / population.current_population  # For MetroAreas current population should be the population of the airport_city
    logging.debug(f"Travel Probabilities {travel_probabilities}")
    travel_probabilities[-1] = 1 - sum(travel_probabilities)  # Normalization of probabilities

    rng = np.random.default_rng()
    travelers = dict.fromkeys(['S', 'I', 'R'])

    for label, labeled_population in population.current_state.items():  # label \in {S,I,R}
        try:
            labeled_travelers = rng.multinomial(labeled_population, travel_probabilities)
        except ValueError:
            logging.error(f'Population {population} has a population {population.compute_population()}')
        travelers[label] = {listed_connections[idx][0]: labeled_travelers[idx] for idx in
                            range(len(labeled_travelers) - 1)}
    logging.debug(f" The travelers from {population.name} are {travelers}")

    population.travelers = travelers

    return travelers


def move_travelers(travelers: Dict[str, Dict['Population', int]], origin: Population):
    """
    Subtracts and adds the travelers from city origin to its neighbors
    :param travelers: Dictionary like the returned from the function compute_travelers()
    :param origin: city where the traveler are traveling from
    :return: No return value
    """
    logging.debug(f"Total population of {origin} before moving travelers {origin.compute_population()}")
    for label, dict_travelers in travelers.items():
        for destination, passengers in dict_travelers.items():
            logging.debug(
                f"The state of {destination} before moving {label}-travelers is {destination.current_state} with a total population of {destination.compute_population()}")
            destination.current_state[label] += passengers
            origin.current_state[label] -= passengers
            logging.debug(
                f"The state of {destination} after moving {label}-travelers  is {destination.current_state} with a total population of {destination.compute_population()}")
    logging.debug(f"Total population of {origin} after moving travelers {origin.compute_population()}")


def move_travelers_II(network: 'networkx', dict_populations):
    if not nx.is_directed(network):
        edges_list = list(nx.to_directed(network).edges())
    else:
        edges_list = list(network.edges())
    rm.shuffle(edges_list)

    for edge in edges_list:
        logging.debug(f"Total population of {dict_populations[edge[0]]} before moving travelers {dict_populations[edge[0]].compute_population()}")
        for label, dict_travelers in dict_populations[edge[0]].travelers.items():
            logging.debug(
                f"The state of {dict_populations[edge[1]]} before moving {dict_travelers[dict_populations[edge[1]]]} {label}-travelers is {dict_populations[edge[1]].current_state} with a total population of {dict_populations[edge[1]].compute_population()}")
            dict_populations[edge[1]].current_state[label] += dict_travelers[dict_populations[edge[1]]]
            dict_populations[edge[0]].current_state[label] -= dict_travelers[dict_populations[edge[1]]]
            logging.debug(
                f"The state of {dict_populations[edge[1]]} after moving {label}-travelers is {dict_populations[edge[1]].current_state} with a total population of {dict_populations[edge[1]].compute_population()}")
        logging.debug(
            f"Total population of {dict_populations[edge[0]]} after moving travelers {dict_populations[edge[0]].compute_population()}")