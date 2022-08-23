# Eamod spec problem
import os
import configparser
import numpy as np
import ast
from typing import List, Union, Dict, Any


class EAMoDspec:
    """Class that prepares the execution of the EAMoDspec class."""

    def __init__(self, conf: configparser.ConfigParser) -> None:
        """Create an EAMoDspec instance

        Args:
            conf (dict): configuration dictionary with the initial variables.
        """
        self.config = conf
        self._n_vehicle = None  # Calculated
        self._initial_state_full_vehicles = None  # Assigned
        self._initial_state_empty_vehicles = None  # Assigned
        self._road_capacity_matrix: List[List[int]] = []  # Assigned
        self._road_adjacency_list: List[int] = []  # Assigned
        self._road_adjacency_matrix: List[List[int]] = []  # Assigned
        self._road_reverse_adjacency_list: List[int] = []  # Calculated
        self._road_node_outdegree = []  # Calculated
        self._edge_number_matrix = []  # Calculated
        self._road_travel_time_matrix = []  # Assigned
        self._road_travel_distance_matrix_m = []  # Assigned
        self._road_charge_to_traverse_matrix = []  # Assigned
        self._n_road_edge: Union[int, None] = None  # Calculated
        self._n_road_node: Union[int, None] = None  # Calculated
        self._n_charger = None  # Calculated
        self._n_charge_steps = None  # Assigned
        # Charger variables
        self._charger_list = []  # Assigned
        self._charger_speed = []  # Assigned
        self._charger_time = []  # Assigned
        self._charger_capacity = []  # Assigned
        # Passenger flow
        self._n_passanger_flow = None  # Assigned only for testing purposes.

    @classmethod
    def initialize_parameters(cls, conf: configparser.ConfigParser) -> None:
        """Function that will initialize the variables of the Spec Class.

        Args:
            conf (dict): configuration dictionary containing the variables.
        """
        instance = cls(conf)

        # Only the parameters included in functions are initialized for testing purposes.
        instance.road_adjacency_list = instance.config["road_adjacency_list"]
        instance.n_road_node = len(instance.road_adjacency_list)
        instance.validate_road_graph()

        instance.n_road_node = int(instance.config["initialization"]["n_road_node"])
        instance.n_charge_steps = int(
            instance.config["initialization"]["n_charge_steps"]
        )
        instance.n_passanger_flow = int(
            instance.config["initialization"]["n_passanger_flow"]
        )

        # Vehicle state

        # Only as an initialization example
        # In case on customer flows a value is assigned accordingly, to ensure enough vehicle availability
        instance.initial_state_empty_vehicles = np.zeros(
            shape=(instance.n_road_node, instance.n_charge_steps)
        )
        instance.initial_state_full_vehicles = np.zeros(
            shape=(
                instance.n_passanger_flow,
                instance.n_road_node,
                instance.n_charge_steps,
            )
        )
        instance.set_n_vehicle()

        instance.set_road_capacity_matrix()

        # Charger variables
        instance.update_properties_dependent_on_road_graph()

        return instance

    @property
    def road_capacity_matrix(self) -> None:
        return self._road_capacity_matrix

    def set_road_capacity_matrix(self) -> None:
        road_capacity_matrix = ast.literal_eval(
            self.config["road_capacity_matrix"]["capacity_matrix"]
        )
        self._road_capacity_matrix = np.array(road_capacity_matrix)

    @property
    def initial_state_full_vehicles(self):
        return self._initial_state_full_vehicles

    @initial_state_full_vehicles.setter
    def initial_state_full_vehicles(self, value):
        self._initial_state_full_vehicles = value

    @property
    def n_passanger_flow(self):
        return self._n_passanger_flow

    @n_passanger_flow.setter
    def n_passanger_flow(self, value):
        self._n_passanger_flow = value

    @property
    def n_road_node(self):
        return self._n_road_node

    @n_road_node.setter
    def n_road_node(self, value):
        self._n_road_node = value

    @property
    def n_charge_steps(self):
        return self._n_charge_steps

    @n_charge_steps.setter
    def n_charge_steps(self, value):
        self._n_charge_steps = value

    @property
    def initial_state_empty_vehicles(self):
        return self._initial_state_empty_vehicles

    @initial_state_empty_vehicles.setter
    def initial_state_empty_vehicles(self, value):
        self._initial_state_empty_vehicles = value

    @property
    def road_node_outdegree(self):
        return self._road_node_outdegree

    @road_node_outdegree.setter
    def road_node_outdegree(self, value):
        self._road_node_outdegree = value

    @property
    def road_adjacency_matrix(self):
        return self._road_adjacency_matrix

    @road_adjacency_matrix.setter
    def road_adjacency_matrix(self, value):
        self._road_adjacency_matrix = value

    @property
    def road_adjacency_list(self):
        return self._road_adjacency_list

    @road_adjacency_list.setter
    def road_adjacency_list(self, value):
        """Setter assigning road_adjacency_list values.

        Args:
            value (str): string representing a list of nodes.
        """
        for (_, val) in value.items():
            val = ast.literal_eval(val)  # Convert list string to list
            self._road_adjacency_list.append(sorted(list(set(val))))

    def is_valid_road_node(self, i):
        """Function to check if a road node i is valid or not

        Args:
            i (int): integer corresponding to a node.

        Returns:
            bool: True if is a valid road node and false otherwise.
        """
        return isinstance(i, int) and 1 <= i and i <= self.n_road_node

    def validate_road_graph(self):
        """Function to validate the road_adjacency_list."""
        for i in range(len(self.road_adjacency_list)):
            assert all(
                self.is_valid_road_node(j) for j in self.road_adjacency_list[i]
            ), f"Not all neighbors of node {i} are valid road nodes"

    def update_properties_dependent_on_road_graph(self):
        """Property calculation for the road network construction."""
        reverse_adjacency_list = [[] for _ in range(len(self.road_adjacency_list))]
        road_adjacency_matrix = np.zeros(shape=(self.n_road_node, self.n_road_node))
        # Fill reverse adjacency list
        for i in range(len(self.road_adjacency_list)):
            for val in self.road_adjacency_list[i]:
                reverse_adjacency_list[val - 1].append(i)

        self.road_reverse_adjacency_list = [
            sorted(list(set(val))) for val in reverse_adjacency_list
        ]

        # Fill adjacency matrix
        for i in range(self.n_road_node):
            for j in self.road_adjacency_list[i]:
                road_adjacency_matrix[i, j - 1] = 1

        self.road_adjacency_matrix = road_adjacency_matrix

        # Fill node outdegree and calculate n road edge
        road_node_outdegree = [
            len(self.road_adjacency_list[i]) for i in range(self.n_road_node)
        ]
        self._n_road_edge = sum(road_node_outdegree)
        self.road_node_outdegree = road_node_outdegree
        self._edge_number_matrix = np.full([self.n_road_node, self.n_road_node], np.nan)

        edge_c = 0
        for i in range(self.n_road_node):
            for j in range(len(self.road_adjacency_list[i])):
                edge_c += 1
                self._edge_number_matrix[i, j] = edge_c

    def set_n_vehicle(self):
        """Function that specifies the number of vehicles."""
        n_vehicle_full_init = sum(self.initial_state_full_vehicles)
        n_vehicle_empty_init = sum(self.initial_state_empty_vehicles)

        self._n_vehicle = n_vehicle_full_init + n_vehicle_empty_init


# Call EAmodSpec class
if __name__ == "__main__":
    path_to_eamod_config = os.path.join("tests", "data", "config.ini")
    config = configparser.ConfigParser()
    config.read(path_to_eamod_config)
    # Class instance
    EAMoDspec.initialize_parameters(config)
