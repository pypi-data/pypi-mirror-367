import pytest
import pandas as pd
import numpy as np
from pyedm4hep.utils import (
    get_simulator_status_bits,
    _calculate_R,
    _calculate_theta,
    _calculate_eta,
    load_event_data,
    _build_particle_df,
    _process_single_tracker,
    _process_single_calo,
    _build_calo_df,
    _add_hit_positions_to_contributions,
    all_trackers,
    all_calos
)

def test_get_simulator_status_bits():
    """Test decoding of simulator status bits."""
    # Test cases based on the bit definitions in utils.py
    # static const int BITCreatedInSimulation = 30;
    # static const int BITBackscatter = 29 ;
    # static const int BITVertexIsNotEndpointOfParent = 28 ;
    # static const int BITDecayedInTracker = 27 ;
    # static const int BITDecayedInCalorimeter = 26 ;
    # static const int BITLeftDetector = 25 ;
    # static const int BITStopped = 24 ;
    # static const int BITOverlay = 23 ;

    assert get_simulator_status_bits(0) == {
        'created_in_simulation': False,
        'backscatter': False,
        'vertex_not_endpoint': False,
        'decayed_in_tracker': False,
        'decayed_in_calorimeter': False,
        'has_left_detector': False,
        'stopped': False,
        'overlay': False
    }

    assert get_simulator_status_bits(1 << 30) == {
        'created_in_simulation': True,
        'backscatter': False,
        'vertex_not_endpoint': False,
        'decayed_in_tracker': False,
        'decayed_in_calorimeter': False,
        'has_left_detector': False,
        'stopped': False,
        'overlay': False
    }

    assert get_simulator_status_bits(1 << 29) == {
        'created_in_simulation': False,
        'backscatter': True,
        'vertex_not_endpoint': False,
        'decayed_in_tracker': False,
        'decayed_in_calorimeter': False,
        'has_left_detector': False,
        'stopped': False,
        'overlay': False
    }

    status_all_true = (1 << 30) | (1 << 29) | (1 << 28) | (1 << 27) | \
                      (1 << 26) | (1 << 25) | (1 << 24) | (1 << 23)
    assert get_simulator_status_bits(status_all_true) == {
        'created_in_simulation': True,
        'backscatter': True,
        'vertex_not_endpoint': True,
        'decayed_in_tracker': True,
        'decayed_in_calorimeter': True,
        'has_left_detector': True,
        'stopped': True,
        'overlay': True
    }

    # Test with a non-integer input (should be cast to int by the function)
    assert get_simulator_status_bits(float(1 << 25)) == {
        'created_in_simulation': False,
        'backscatter': False,
        'vertex_not_endpoint': False,
        'decayed_in_tracker': False,
        'decayed_in_calorimeter': False,
        'has_left_detector': True,
        'stopped': False,
        'overlay': False
    }

def test_calculate_R():
    """Test R calculation."""
    assert _calculate_R(3, 4) == 5.0
    assert _calculate_R(3, 4, 0) == 5.0 # With z=0
    assert _calculate_R(0, 0, 5) == 5.0
    assert _calculate_R(1, 1, 1) == pytest.approx(np.sqrt(3))
    assert _calculate_R(0, 0, 0) == 0.0

def test_calculate_theta():
    """Test theta calculation."""
    assert _calculate_theta(0, 1) == pytest.approx(0.0)      # Along +z axis
    assert _calculate_theta(1, 0) == pytest.approx(np.pi/2)  # In x-y plane
    assert _calculate_theta(0, -1) == pytest.approx(np.pi)   # Along -z axis
    assert _calculate_theta(1, 1) == pytest.approx(np.pi/4)
    assert _calculate_theta(1e-16, 1) == pytest.approx(0.0) # Near +z axis
    assert _calculate_theta(1e-16, -1) == pytest.approx(np.pi) # Near -z axis


def test_calculate_eta():
    """Test eta calculation."""
    assert _calculate_eta(np.pi/2) == pytest.approx(0.0) # Corresponds to theta = 90 degrees
    assert _calculate_eta(np.pi/4) == pytest.approx(-np.log(np.tan(np.pi/8)))
    assert _calculate_eta(3*np.pi/4) == pytest.approx(-np.log(np.tan(3*np.pi/8)))
    
    # Test edge cases for theta leading to large eta
    # A very small theta (close to 0, particle along beam line forward)
    # Expect large positive eta
    small_theta = 1e-9
    assert _calculate_eta(small_theta) > 10 # Large positive value

    # A theta very close to pi (particle along beam line backward)
    # Expect large negative eta
    close_to_pi_theta = np.pi - 1e-9
    assert _calculate_eta(close_to_pi_theta) < -10 # Large negative value

    # Test at theta = 0 and theta = pi (should be handled by the 1e-15 check in function)
    # These would normally result in -log(0) = inf or -log(tan(pi/2)) = -log(inf) = -inf
    # The implementation replaces inf with a large number.
    assert np.isfinite(_calculate_eta(0.0))
    assert _calculate_eta(0.0) == pytest.approx(-np.log(1e-15)) # Approx 34.53
    assert np.isfinite(_calculate_eta(np.pi))
    # When theta = np.pi, tan_theta_half = tan(np.pi/2) which is very large (e.g., ~1.6e16).
    # eta = -log(tan_theta_half) which will be a large negative number.
    assert _calculate_eta(np.pi) == pytest.approx(-37.33185619326892) # Using value from previous test run for precision

# We will add tests for _build_particle_df, _process_single_tracker, 
# _process_single_calo, _build_calo_df, _add_hit_positions_to_contributions, 
# and load_event_data once we have a strategy for test data (sample file or mocks). 

# --- Tests for data loading functions ---

EXPECTED_PARTICLE_COLUMNS = [
    'PDG', 'generatorStatus', 'simulatorStatus', 'charge', 'time', 'mass',
    'vx', 'vy', 'vz', 'px', 'py', 'pz', 'endpoint_x', 'endpoint_y', 'endpoint_z',
    'parents_begin', 'parents_end', 'daughters_begin', 'daughters_end',
    'pt', 'p', 'eta', 'phi'
]

EXPECTED_LINK_COLUMNS = ['particle_id', 'collectionID']

EXPECTED_TRACKER_HIT_COLUMNS = [
    'cellID', 'time', 'pathLength', 'quality', 'x', 'y', 'z', 'px', 'py', 'pz', 'EDep', 'particle_id'
]

EXPECTED_CALO_HIT_COLUMNS = [
    'cellID', 'energy', 'x', 'y', 'z', 'detector', 'r', 'R', 'phi', 'theta', 'eta',
    'contribution_begin', 'contribution_end'
]

EXPECTED_CALO_CONTRIBUTION_COLUMNS = [
    'detector', 'PDG', 'energy', 'time', 'step_x', 'step_y', 'step_z', 'particle_id',
    'cellID', 'x', 'y', 'z'
]

EXPECTED_EVENT_DATA_KEYS = [
    'particles', 'parents', 'daughters', 'tracker_hits',
    'calo_hits', 'calo_contributions', 'event_header'
]


@pytest.mark.parametrize("event_idx", [0]) # Test with the first event
def test_load_event_data_structure(sample_event_file_path, event_idx):
    """Test the structure and types of data returned by load_event_data."""
    data = load_event_data(sample_event_file_path, event_idx)

    assert data is not None, "load_event_data returned None"
    assert isinstance(data, dict), "Data is not a dictionary"
    for key in EXPECTED_EVENT_DATA_KEYS:
        assert key in data, f"Missing key: {key} in loaded data"

    assert isinstance(data['particles'], pd.DataFrame), "particles is not a DataFrame"
    assert isinstance(data['parents'], pd.DataFrame), "parents is not a DataFrame"
    assert isinstance(data['daughters'], pd.DataFrame), "daughters is not a DataFrame"
    assert isinstance(data['tracker_hits'], pd.DataFrame), "tracker_hits is not a DataFrame"
    assert isinstance(data['calo_hits'], pd.DataFrame), "calo_hits is not a DataFrame"
    assert isinstance(data['calo_contributions'], pd.DataFrame), "calo_contributions is not a DataFrame"
    assert isinstance(data['event_header'], dict), "event_header is not a dict"

    # Check columns for non-empty DataFrames (if file has data for event 0)
    if not data['particles'].empty:
        assert set(EXPECTED_PARTICLE_COLUMNS).issubset(data['particles'].columns), \
            f"Missing columns in particles_df. Expected subset: {EXPECTED_PARTICLE_COLUMNS}, Got: {list(data['particles'].columns)}"
    
    if not data['parents'].empty:
        assert set(EXPECTED_LINK_COLUMNS).issubset(data['parents'].columns), \
            f"Missing columns in parents_df. Expected subset: {EXPECTED_LINK_COLUMNS}, Got: {list(data['parents'].columns)}"
    if not data['daughters'].empty:
        assert set(EXPECTED_LINK_COLUMNS).issubset(data['daughters'].columns), \
            f"Missing columns in daughters_df. Expected subset: {EXPECTED_LINK_COLUMNS}, Got: {list(data['daughters'].columns)}"

    if not data['tracker_hits'].empty:
        assert set(EXPECTED_TRACKER_HIT_COLUMNS).issubset(data['tracker_hits'].columns), \
            f"Missing columns in tracker_hits_df. Expected subset: {EXPECTED_TRACKER_HIT_COLUMNS}, Got: {list(data['tracker_hits'].columns)}"
    
    if not data['calo_hits'].empty:
        assert set(EXPECTED_CALO_HIT_COLUMNS).issubset(data['calo_hits'].columns), \
            f"Column mismatch in calo_hits_df. Expected subset: {EXPECTED_CALO_HIT_COLUMNS}, Got: {list(data['calo_hits'].columns)}"

    if not data['calo_contributions'].empty:
        assert set(EXPECTED_CALO_CONTRIBUTION_COLUMNS).issubset(data['calo_contributions'].columns), \
            f"Missing columns in calo_contributions_df. Expected subset: {EXPECTED_CALO_CONTRIBUTION_COLUMNS}, Got: {list(data['calo_contributions'].columns)}"
    
    # Check for specific dtypes if necessary, e.g.:
    # if not data['particles'].empty:
    #     assert data['particles']['PDG'].dtype == np.int32

def test_load_event_data_invalid_event(sample_event_file_path):
    """Test loading an event index that is out of bounds."""
    # First, determine a valid number of events in the file
    # Assuming any EDM4HEP file will have fewer than 999999 events
    data = load_event_data(sample_event_file_path, 999999) 
    assert data is None, "load_event_data should return None for a very large event index"

# More specific tests for _build_particle_df, _process_single_tracker, etc.
# might require more knowledge of the sample file's contents or more complex mocking.
# For now, their functionality is implicitly tested via load_event_data.
# We can add dedicated tests if coverage reports show they are not fully covered.

# Example of how one might test _build_particle_df if we had a mock uproot tree:
# def test_build_particle_df_empty(mock_uproot_tree_empty_event):
#     particles_df, parents_df, daughters_df = _build_particle_df(mock_uproot_tree_empty_event, 0)
#     assert particles_df.empty
#     assert parents_df.empty
#     assert daughters_df.empty
#     for col in EXPECTED_PARTICLE_COLUMNS: assert col in particles_df.columns
#     for col in EXPECTED_LINK_COLUMNS: assert col in parents_df.columns
#     for col in EXPECTED_LINK_COLUMNS: assert col in daughters_df.columns

# (End of file additions) 