import pytest
import matplotlib.figure
from pyedm4hep import EDM4hepEvent, PlottingHandler

# Assume fixtures from conftest.py:
# - sample_event_for_plotting: An EDM4hepEvent loaded with detector_params,
#   suitable for generating all types of plots.
# - sample_particle_id_for_plotting: A particle ID from the above event for specific plots.

@pytest.fixture
def plotting_handler(sample_event_for_plotting):
    """Fixture to get a PlottingHandler instance."""
    return sample_event_for_plotting.plot # Accesses the handler, initializes if needed

def test_plot_event_overview(plotting_handler, sample_event_for_plotting):
    """Test generating the event overview plot."""
    # Ensure the event has detector_params as it's required by event_overview
    if not sample_event_for_plotting._detector_params:
        pytest.skip("Skipping event_overview test: event is missing detector_params")

    fig = plotting_handler.event_overview()
    assert isinstance(fig, matplotlib.figure.Figure)
    # Optionally, save the figure to a temporary location and compare with a reference if needed,
    # or at least ensure it runs without exceptions.
    matplotlib.pyplot.close(fig) # Close the figure to free memory

def test_plot_visualize_decay_tree(plotting_handler, sample_event_for_plotting, sample_particle_id_for_plotting):
    """Test generating the decay tree visualization."""
    # Ensure the event has its decay graph processed if the plot relies on it implicitly
    # sample_event_for_plotting.get_decay_tree() # Build/process decay tree

    fig = plotting_handler.visualize_decay_tree(particle_id=None) # Plot full tree
    assert isinstance(fig, matplotlib.figure.Figure)
    matplotlib.pyplot.close(fig)

    fig_particle = plotting_handler.visualize_decay_tree(particle_id=sample_particle_id_for_plotting)
    assert isinstance(fig_particle, matplotlib.figure.Figure)
    matplotlib.pyplot.close(fig_particle)

    # Test with highlight_collapsed and show_tracking_cylinder if possible/relevant
    # Need a known collapsed_id from the sample event if testing highlight_collapsed
    # if sample_event_for_plotting._detector_params: # For show_tracking_cylinder
    #     fig_cylinder = plotting_handler.visualize_decay_tree(show_tracking_cylinder=True)
    #     assert isinstance(fig_cylinder, matplotlib.figure.Figure)
    #     matplotlib.pyplot.close(fig_cylinder)

def test_plot_highlight_ancestors_descendants(plotting_handler, sample_particle_id_for_plotting):
    """Test plotting ancestors and descendants."""
    fig = plotting_handler.highlight_ancestors_descendants(particle_id=sample_particle_id_for_plotting)
    assert isinstance(fig, matplotlib.figure.Figure)
    matplotlib.pyplot.close(fig)

def test_plot_particle_kinematics(plotting_handler):
    """Test plotting particle kinematics histograms."""
    fig_all = plotting_handler.plot_particle_kinematics(particle_selection='all')
    assert isinstance(fig_all, matplotlib.figure.Figure)
    matplotlib.pyplot.close(fig_all)

    # Test with a list of particle IDs if sample data allows
    # particles_df = plotting_handler._event.get_particles_df()
    # if not particles_df.empty:
    #     sample_ids = particles_df.index[:min(3, len(particles_df))].tolist()
    #     if sample_ids:
    #         fig_selection = plotting_handler.plot_particle_kinematics(particle_selection=sample_ids)
    #         assert isinstance(fig_selection, matplotlib.figure.Figure)
    #         matplotlib.pyplot.close(fig_selection)

# Fixtures needed in conftest.py:
# @pytest.fixture(scope="session")
# def sample_event_for_plotting(sample_event_file_path, sample_detector_params):
#     # Load an event, ensuring it has detector_params as many plots require them.
#     # This event should have enough particles/hits/decays to make plotting meaningful.
#     event = EDM4hepEvent(file_path=sample_event_file_path, event_index=EVENT_IDX_FOR_PLOTTING, detector_params=sample_detector_params)
#     # Optionally, process its decay tree if plots depend on it
#     # event.decay.process_decay_tree(energy_threshold=sample_detector_params.get('energy_threshold', 0.01))
#     return event

# @pytest.fixture(scope="session")
# def sample_particle_id_for_plotting(sample_event_for_plotting):
#     # An ID of a particle within sample_event_for_plotting suitable for plots focusing on a single particle.
#     # particles_df = sample_event_for_plotting.get_particles_df()
#     # if not particles_df.empty:
#     #     return particles_df.index[0] # Placeholder
#     return 0 # Placeholder 