import os
import pytest
import configparser
import itertools

# Load eamodspec class from eamod_spec package (it contains an init file).
from eamod_spec.EAmodSpec import EAMoDspec


@pytest.fixture(scope="function")
def eamod_conf():
    config = configparser.ConfigParser()
    config.read(os.path.join("tests", "data", "config.ini"))
    return config


@pytest.fixture(scope="function")
def eamod(eamod_conf):
    return EAMoDspec.initialize_parameters(eamod_conf)


def test_eamod_initialization(eamod):
    """Tests the parameters initialized with the configuration file."""
    # Check the types declared in the matlab code.
    # Adjacency list verification (like validation function but using a test)
    # Redundant check if keep or not
    assert all(
        isinstance(item, int)
        for item in list(itertools.chain.from_iterable(eamod.road_adjacency_list))
    )
    assert all(
        item > 0
        for item in list(itertools.chain.from_iterable(eamod.road_adjacency_list))
    )

    assert all(
        item >= 0
        for item in list(itertools.chain.from_iterable(eamod.road_capacity_matrix))
    )
