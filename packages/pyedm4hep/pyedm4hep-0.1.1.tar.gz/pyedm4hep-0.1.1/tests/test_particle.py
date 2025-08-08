import pytest
from pyedm4hep import Particle, EDM4hepEvent

# Assume fixtures `sample_event_with_particles` (an EDM4hepEvent instance)
# and `sample_particle_id` (an ID of a particle in that event) are defined in conftest.py

@pytest.fixture
def particle_instance(sample_event_with_particles, sample_particle_id):
    """Fixture to get a specific Particle instance for testing."""
    return sample_event_with_particles.get_particle(sample_particle_id)

def test_particle_basic_properties(particle_instance):
    """
    Test basic properties of a Particle object.
    """
    assert particle_instance.id is not None # Or specific expected ID
    # Add assertions for pdg, charge, mass, time, generator_status, simulator_status
    # e.g., assert isinstance(particle_instance.pdg, int)

def test_particle_kinematics(particle_instance):
    """
    Test kinematic properties of a Particle object.
    """
    # Add assertions for px, py, pz, momentum, kinetic_energy, pt, p, energy, eta, phi
    # e.g., assert isinstance(particle_instance.pt, float)

def test_particle_vertex_endpoint(particle_instance):
    """
    Test vertex and endpoint properties.
    """
    # Add assertions for vx, vy, vz, vertex, endpoint_x, endpoint_y, endpoint_z, endpoint, vr, endpoint_r
    # e.g., assert len(particle_instance.vertex) == 3

def test_particle_simulation_status_flags(particle_instance):
    """
    Test simulation status flags (decoded from simulatorStatus).
    """
    assert isinstance(particle_instance.status_bits, dict)
    assert isinstance(particle_instance.is_created_in_simulation, bool)
    # Add assertions for other boolean flags like is_backscatter, created_inside_tracker etc.
    # These will depend on the specifics of the sample_event_with_particles and sample_particle_id

def test_particle_relationships_parents_daughters(particle_instance, sample_event_with_particles):
    """
    Test parent and daughter relationships.
    This requires the sample particle to have known parents/daughters in the sample event.
    """
    parents = particle_instance.get_parents()
    daughters = particle_instance.get_daughters()
    assert isinstance(parents, list)
    assert isinstance(daughters, list)
    # Add more specific assertions, e.g., if all elements are Particle instances, expected number of parents/daughters

def test_particle_relationships_hits(particle_instance):
    """
    Test hit relationships (tracker and calo).
    """
    tracker_hits = particle_instance.get_tracker_hits()
    tracker_hits_df = particle_instance.get_tracker_hits_df()
    calo_contribs = particle_instance.get_calo_hits() # These are CaloContributions
    calo_contribs_df = particle_instance.get_calo_hits_df()

    assert isinstance(tracker_hits, list)
    assert tracker_hits_df is not None # Should be a pandas DataFrame
    assert isinstance(calo_contribs, list)
    assert calo_contribs_df is not None # Should be a pandas DataFrame

    # Test num_hits methods
    assert isinstance(particle_instance.get_num_hits(), int)
    assert isinstance(particle_instance.get_num_tracker_hits(), int)
    assert isinstance(particle_instance.get_num_calo_hits(), int)


def test_particle_relationships_ancestors_descendants(particle_instance, sample_event_with_particles):
    """
    Test ancestor and descendant relationships (uses DecayGraphHandler).
    """
    # Ensure decay graph is processed for these to work as expected from planning.md
    # sample_event_with_particles.get_decay_tree() # Call once to build/process if necessary or ensure fixture does it
    
    ancestors = particle_instance.get_ancestors()
    descendants = particle_instance.get_descendants()
    assert isinstance(ancestors, list)
    assert isinstance(descendants, list)

# Add tests for __repr__, __eq__, __hash__ if important for your use cases.

# Fixtures needed in conftest.py:
# @pytest.fixture(scope="session")
# def sample_event_with_particles(sample_event_file_path, sample_detector_params):
#     # Load an event known to have interesting particles and relationships
#     # Potentially process its decay tree if needed for ancestor/descendant tests
#     event = EDM4hepEvent(file_path=sample_event_file_path, event_index=0, detector_params=sample_detector_params)
#     # event.decay.process_decay_tree() # Optional: if tests rely on processed tree
#     return event

# @pytest.fixture(scope="session")
# def sample_particle_id(sample_event_with_particles):
#     # Return the ID of a specific particle from the sample_event_with_particles
#     # that is suitable for testing various properties and relationships.
#     # For example, a particle with parents, daughters, and hits.
#     # particles_df = sample_event_with_particles.get_particles_df()
#     # if not particles_df.empty:
#     #     return particles_df.index[0] # Placeholder, choose a meaningful ID
#     return 0 # Placeholder 