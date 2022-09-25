from typing import Dict, List, Any, Set
import numpy as np
import matplotlib.pyplot as plt
import copy as cp
import logging


class Population:
    """
    Parent class of the subclasses City and MetroArea. It mainly contains the data needed for the transport operator.
    """

    def __init__(self, name: str, index: int):
        self.name = name
        self.connections = None
        self.index = index
        self.history_state = np.array([])
        self.current_state = None
        self.current_population = None
        self.travelers = None

    def __repr__(self):  # Needed to see the names of the objects while printing/logging messages
        return self.name

    def set_connections(self, connections: Dict['Population', int]):
        self.connections = connections

    def compute_population(self):  # Function used to update the current_population, which should not be updated in real time
        pass

    def plot_history(self, final_step, step_number, coupling: int):
        pass

    def show_neighbors(self):
        print(f'The travelers from {self.name} are:')
        for neighbor in self.connections:
            print(self.connections[neighbor], '->', neighbor.name)


class MetroArea(Population):

    def __init__(self, name: str, index: int, cities: Set['City'], metro_net=None):
        super().__init__(name, index)
        self.cities = cities
        #self.airport_city = max(cities, key=lambda city: city.current_population)  # Choose the city with more population. In case of equal number it chooses it "radomly" between the cities with the largest population
        self.airport_city = next(city for city in self.cities if city.index ==10) # 2
        self.airport_city.history_travelers = []
        self.current_state = self.airport_city.current_state  # The current_state of the MetroAreas is the current_state of the airport_city
        self.current_population = self.airport_city.current_population
        self.network = metro_net
        self.dict_cities = {city.index: city for city in cities}
        logging.debug(f"Metropolitan area around {self.name} was created!")

    def compute_population(self):
        return self.airport_city.compute_population()

    def plot_history(self, final_time, dt, coupling: int):
        """
        Quick way to see the development within the metropolitan area
        """
        history = [{label: sum(city.history_state[idx][label] for city in self.cities)
                    for label in self.current_state.keys()}
                   for idx in range(len(self.airport_city.history_state))]
        reps = int(np.ceil(dt * coupling))
        step_number = int(final_time / dt)
        time = np.linspace(0, final_time, step_number * reps + 1, endpoint=True)
        plt.plot(time, [[dic['S'], dic['I'], dic['R']] for dic in history])
        plt.xlabel("days")
        plt.ylabel("population")
        plt.legend(["Susceptible", "Infected", "Recovered"])
        plt.show()


class City(Population):

    def __init__(self, name: str, index: int, state: List[int], simulation_parameters: List[float]):
        super().__init__(name, index)
        self.current_state = {'S': state[0], 'I': state[1], 'R': state[2]}
        self.history_state = np.append(self.history_state, cp.deepcopy(self.current_state))
        self.parms = {'infection_rate': simulation_parameters[0],
                      'recovery_rate': simulation_parameters[1]}
        self.current_population = sum(self.current_state.values())
        self.history_travelers = None
        logging.debug(f"City {self.name} was created!")

    def compute_population(self):
        return sum(self.current_state.values())

    def plot_history(self, final_time, dt, coupling: int):
        """
        Quick way to see the development within the city
        """
        reps = int(np.ceil(dt * coupling))
        step_number = int(final_time / dt)
        time = np.linspace(0, final_time, step_number * reps + 1, endpoint=True)
        plt.plot(time, [[dic['S'], dic['I'], dic['R']] for dic in self.history_state])
        plt.xlabel("days")
        plt.ylabel("population")
        plt.legend(["Susceptible", "Infected", "Recovered"])
        plt.title(self.name)
        plt.show()
