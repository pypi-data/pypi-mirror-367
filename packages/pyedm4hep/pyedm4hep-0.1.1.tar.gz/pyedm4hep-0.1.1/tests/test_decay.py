import pytest
import networkx as nx
from pyedm4hep import EDM4hepEvent, DecayGraphHandler

# Assume fixtures from conftest.py:
# - sample_event_for_decay_tests: An EDM4hepEvent instance suitable for testing decay logic.
#   This event should have a known decay structure.
# - sample_particle_id_for_decay: A particle ID within sample_event_for_decay_tests to test specific decay paths.

@pytest.fixture
def decay_handler(sample_event_for_decay_tests):
    """Fixture to get a DecayGraphHandler instance."""
    return sample_event_for_decay_tests.decay # Accesses the handler, initializes if needed

@pytest.fixture
def processed_decay_graph(decay_handler, sample_detector_params):
    """Fixture to get a decay graph that has been processed."""
    # Assuming detector_params are needed for process_decay_tree, pass them or a fixture for them
    # The energy_threshold can be a default or part of the fixture setup.
    decay_handler.process_decay_tree(energy_threshold=sample_detector_params.get('energy_threshold', 0.01))
    return decay_handler.get_graph()

def test_decay_graph_build(decay_handler):
    """Test the initial building of the decay graph."""
    graph = decay_handler.get_graph() # Should build if not already built
    assert isinstance(graph, nx.DiGraph)
    # Add assertions based on the number of particles in the event
    # e.g., assert len(graph.nodes) == len(decay_handler._event.get_particles_df())
    # Check for essential node attributes: 'particleID', 'energy', 'pdg', etc.
    # Check for edge creation based on parent-daughter relationships.

def test_decay_graph_process_decay_tree(decay_handler, processed_decay_graph, sample_event_for_decay_tests):
    """Test the process_decay_tree method for collapsedParticleID and incidentParentID."""
    graph = processed_decay_graph # Already processed by the fixture
    # Iterate through nodes and check if 'collapsedParticleID' and 'incidentParentID' are set
    for node_id, data in graph.nodes(data=True):
        assert 'collapsedParticleID' in data
        assert 'incidentParentID' in data
        # More specific assertions based on the known decay structure of sample_event_for_decay_tests
        # e.g., particle X should have collapsedID Y, particle Z should have incidentParentID W

def test_decay_analyze_particles(decay_handler, processed_decay_graph):
    """Test the analyze_particles method."""
    # Ensure process_decay_tree has been called (handled by processed_decay_graph fixture)
    analysis_df = decay_handler.analyze_particles()
    assert analysis_df is not None # Should be a pandas DataFrame
    if not analysis_df.empty:
        assert 'total_energy' in analysis_df.columns
        assert 'num_segments' in analysis_df.columns
    # Check specific values if the sample event has a known structure leading to specific collapsed info

def test_decay_get_particle_descendants(decay_handler, processed_decay_graph, sample_particle_id_for_decay):
    """Test fetching particle descendants."""
    descendants = decay_handler.get_particle_descendants(sample_particle_id_for_decay)
    assert isinstance(descendants, list)
    # Add assertions based on known descendants for sample_particle_id_for_decay

def test_decay_get_particle_ancestors(decay_handler, processed_decay_graph, sample_particle_id_for_decay):
    """Test fetching particle ancestors."""
    ancestors = decay_handler.get_particle_ancestors(sample_particle_id_for_decay)
    assert isinstance(ancestors, list)
    # Add assertions based on known ancestors for sample_particle_id_for_decay

def test_decay_get_particles_by_collapsed_id(decay_handler, processed_decay_graph):
    """Test fetching particles by collapsed ID."""
    # This requires knowing a collapsed_id from your sample_event_for_decay_tests
    # collapsed_ids = {data['collapsedParticleID'] for _, data in processed_decay_graph.nodes(data=True)}
    # if collapsed_ids:
    #     sample_collapsed_id = list(collapsed_ids)[0]
    #     particles = decay_handler.get_particles_by_collapsed_id(sample_collapsed_id)
    #     assert isinstance(particles, list)
    #     # Further checks on the content of `particles`
    pass # Needs a known collapsed_id from test data

def test_decay_get_particle_decay_path(decay_handler, processed_decay_graph):
    """Test fetching a particle decay path."""
    # This requires knowing a start_id and an end_id that form a valid path
    # in your sample_event_for_decay_tests.
    # e.g. path = decay_handler.get_particle_decay_path(start_id=X, end_id=Y)
    # assert isinstance(path, list)
    # assert path[0] == X
    # assert path[-1] == Y
    pass # Needs known start_id and end_id from test data

# Fixtures needed in conftest.py:
# @pytest.fixture(scope="session")
# def sample_event_for_decay_tests(sample_event_file_path, sample_detector_params):
#     # Load an event specifically chosen for its decay chain complexity and known structure
#     event = EDM4hepEvent(file_path=sample_event_file_path, event_index=EVENT_IDX_FOR_DECAY, detector_params=sample_detector_params)
#     return event

# @pytest.fixture(scope="session")
# def sample_particle_id_for_decay(sample_event_for_decay_tests):
#     # An ID of a particle within sample_event_for_decay_tests that is interesting for testing
#     # e.g., a particle in the middle of a decay chain, or one that gets collapsed.
#     # return SOME_PARTICLE_ID
#     return 0 # Placeholder

# Note: The `processed_decay_graph` fixture assumes that `process_decay_tree` might use
# detector parameters. If `process_decay_tree` also takes `energy_threshold` from
# `detector_params`, adjust the fixture or ensure `sample_detector_params` includes it.
# The `planning.md` mentions `energy_threshold` as an argument to `process_decay_tree`. 