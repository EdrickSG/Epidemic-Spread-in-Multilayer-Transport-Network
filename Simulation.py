from typing import Dict, List, Any, Set
from Population import MetroArea
import numpy as np
import copy as cp
import Transport_Operator as TO
import random as rm
import logging


class Simulation:
    """
    This class contains all the information regarding the time and the functions that iterates over cities/metro areas
    """

    def __init__(self, final_time: float, dt: float, metro_areas: Set[MetroArea], airport_network=None):
        self.final_time = final_time
        self.dt = dt
        self.step_number = int(final_time / dt)
        self.metro_areas = metro_areas
        for metro_area in self.metro_areas:
            metro_area.population_cardinality = len(metro_areas)
        self.dict_metro_areas = {metro.index: metro for metro in metro_areas}
        self.airport_network = airport_network

    def euler_step(self):
        """
        Performs an Euler step in every city, by modifying directly their current_state
        """
        for metro in self.metro_areas:
            for city in metro.cities:
                rates = [city.parms['infection_rate'] * city.current_state['S'] * city.current_state[
                    'I'] / city.current_population,
                         city.parms['recovery_rate'] * city.current_state['I']]

                city.current_state['S'] = city.current_state['S'] - rates[0] * self.dt
                city.current_state['I'] = city.current_state['I'] + rates[0] * self.dt - rates[1] * self.dt
                city.current_state['R'] = city.current_state['R'] + rates[1] * self.dt

    def inner_movement(self):
        """
        Computes the travelers for each city and moves them to the corresponding neighbor
        """
        for metro_area in self.metro_areas:
            total_inner_travelers = 0
            for city in metro_area.cities:
                travelers = TO.compute_travelers(city, self.dt)
                total_inner_travelers += np.array([travelers[label][city] for label in travelers.keys() for city in travelers[label]]).sum()  #Everything related with total_inner_travelers is just to supervise ratios and can be commented out during simulations
                #TO.move_travelers(travelers, city)
            logging.debug(f"The total inner travelers at the current time step at metropolitan area {metro_area} were {total_inner_travelers}")
            TO.move_travelers_II(metro_area.network,metro_area.dict_cities)
        self.update_all_populations()  # The population is only needed to compute the travel_probabilities (in TO.compute_travelers()). Therefore, we need to update the population only after all the travelers are moved

    def outer_movement(self):
        """
        Computes the travelers for each metropolitan area and moves them to the corresponding neighbor
        """
        for metro_area in self.metro_areas:
            travelers = TO.compute_travelers(metro_area, self.dt)
            total_outer_travelers = np.array([travelers[label][city] for label in travelers.keys() for city in travelers[label]]).sum()
            logging.debug(
                f"The total outer travelers at the current time step at metropolitan area {metro_area} were {total_outer_travelers}")
            #TO.move_travelers(travelers, metro_area)
            metro_area.airport_city.history_travelers.append(travelers)
        TO.move_travelers_II(self.airport_network, self.dict_metro_areas)
        self.update_airport_populations()

    def update_all_populations(self):
        for metro in self.metro_areas:
            for city in metro.cities:
                city.current_population = city.compute_population()
                city.history_state = np.append(city.history_state, cp.deepcopy(city.current_state))

    def update_airport_populations(self):
        for metro in self.metro_areas:
            metro.airport_city.current_population = metro.airport_city.compute_population()
            metro.airport_city.history_state[-1] = cp.deepcopy(
                metro.airport_city.current_state)  # Instead of adding another state, the last state is replaced by the new one. So all the cities have the same number of states in history_state

    def set_connections_cities(self):
        for metro in self.metro_areas:
            for node_idx in metro.network.nodes():
                city_connections = {}
                for neighbor_idx in metro.network.neighbors(node_idx):
                    city_connections.update(
                        {metro.dict_cities[neighbor_idx]: metro.network[node_idx][neighbor_idx]['passengers']})
                metro.dict_cities[node_idx].set_connections(city_connections)

    def set_initial_conditions(self):
        # metro_index = rm.choice(list(self.dict_metro_areas))
        metro_index = 346
        patient_zero_city = self.dict_metro_areas[metro_index].dict_cities[10] # 1
        patient_zero_city.current_state['S'] -= 1
        patient_zero_city.current_state['I'] += 1
        patient_zero_city.history_state[0] = cp.deepcopy(patient_zero_city.current_state)

        logging.info(f"Patient zero is in {patient_zero_city}!! D:")

    def set_connections_airports(self):
        for node_idx in self.airport_network.nodes():
            airport_connections = {}
            for neighbor_idx in self.airport_network.neighbors(node_idx):
                airport_connections.update(
                    {self.dict_metro_areas[neighbor_idx]: self.airport_network[node_idx][neighbor_idx]['passengers']})
            self.dict_metro_areas[node_idx].set_connections(airport_connections)
