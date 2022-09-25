from Simulation import *
from Networks import *
import logging
import pickle
import matplotlib.pyplot as plt

# Logger Configurations
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                    level=logging.INFO)  # level = logging.DEBUG for tracking travelers
logging.getLogger('matplotlib.font_manager').disabled = True  # Avoid matplotlib messages in the logger

# Loading Data
with open('./Data/Routes_30/city_name_population.npy', 'rb') as f:  # ['82', 'Toronto', 'Canada', '2930000', '43.86220169067383','-79.37000274658203']
    metro_data = np.load(f, allow_pickle=True)
with open('./Data/Routes_30/populations_dictionary_13.pkl', 'rb') as f:
    dict_pops = pickle.load(f)
weighted_connections_data = np.genfromtxt('./Data/Routes_30/weighted_network.csv', delimiter=',')

simulation_list = np.array([])

metro_networks_set = create_metro_networks(metro_data[::, [0, 1, 3]], lambda x: nx.full_rary_tree(2, x),
                                           dict_pops)  # e.g lambda x: nx.erdos_renyi_graph(x,.6), nx.complete_graph, lambda x: nx.full_rary_tree(2, x)

runs_number = 50
for i in range(runs_number):
    logging.info(f"{i}/{runs_number} simulation! :)")
    # Setting Populations
    metro_areas_set = from_networks_to_populations(metro_networks_set)
    airport_network = create_airport_network(weighted_connections_data)

    # Simulation
    world1 = Simulation(100, .1, metro_areas_set, airport_network)
    world1.set_connections_cities()
    world1.set_connections_airports()
    world1.set_initial_conditions()

    # Main Loop
    for i in range(world1.step_number):
        logging.info(f"Day :{i * world1.dt}")
        world1.euler_step()
        world1.inner_movement()
        world1.outer_movement()
    simulation_list = np.append(simulation_list, world1)

# Saving Data
with open("/Volumes/One Touch/Results/180_rarytree2_13_airportlevel3_runs50_timesteps100_pziac_savtrl.pickle", "wb") as f:
    pickle.dump(simulation_list, f, protocol=pickle.HIGHEST_PROTOCOL)
