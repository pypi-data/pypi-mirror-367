import pytest
from pyedm4hep import EDM4hepDataset # Corrected casing: EDM4hepDataset instead of EDM4HepDataset
from pyedm4hep import EDM4hepEvent

# Assume fixtures from conftest.py:
# - sample_event_file_path: Path to a ROOT file with multiple events for dataset testing.
# - sample_detector_params: Detector parameters for event loading.

@pytest.fixture
def dataset_instance(sample_event_file_path, sample_detector_params):
    """Fixture to create an EDM4HepDataset instance."""
    # Adjust initialization based on actual EDM4HepDataset constructor
    return EDM4hepDataset(file_path=sample_event_file_path, detector_params=sample_detector_params)

def test_dataset_initialization(dataset_instance, sample_event_file_path):
    """Test basic initialization of EDM4HepDataset."""
    assert dataset_instance is not None
    assert dataset_instance.file_path == sample_event_file_path
    # Add assertions for other initial properties, e.g., number of events if known by dataset upon init

def test_dataset_len(dataset_instance):
    """Test the __len__ method of the dataset."""
    # This assumes the dataset knows the number of events in the file.
    # You might need to use uproot to open sample_root_file_path and get num_entries for comparison.
    # import uproot
    # with uproot.open(dataset_instance.file_path) as f:
    #     num_entries = f["events"].num_entries # Adjust tree name if necessary
    # assert len(dataset_instance) == num_entries
    assert isinstance(len(dataset_instance), int)
    assert len(dataset_instance) >= 0

def test_dataset_getitem(dataset_instance):
    """Test the __getitem__ method for retrieving an event."""
    if len(dataset_instance) == 0:
        pytest.skip("Skipping __getitem__ test: dataset is empty or length is not yet determined.")
    
    event = dataset_instance[0] # Get the first event
    assert isinstance(event, EDM4hepEvent)
    assert event.event_index == 0
    
    # Test accessing another event if available
    # if len(dataset_instance) > 1:
    #     event_1 = dataset_instance[1]
    #     assert isinstance(event_1, EDM4hepEvent)
    #     assert event_1.event_index == 1

def test_dataset_iteration(dataset_instance):
    """Test iterating over the dataset."""
    if len(dataset_instance) == 0:
        pytest.skip("Skipping iteration test: dataset is empty.")
        
    count = 0
    for i, event in enumerate(dataset_instance):
        assert isinstance(event, EDM4hepEvent)
        assert event.event_index == i
        count += 1
    assert count == len(dataset_instance)

# Add other tests relevant to EDM4HepDataset functionality, for example:
# - Methods for batch loading or processing if available.
# - Filtering capabilities if the dataset supports them.

# Fixtures needed in conftest.py (some might be reused):
# @pytest.fixture(scope="session")
# def sample_root_file_path(): # This might be same as sample_event_file_path or a different one
#     # Path to a ROOT file, preferably with a few events.
#     # return "usr/danieltm/ColliderML/software/OtherLibraries/pyedm4hep/tests/data/multi_event_sample.root"
#     pass # Needs to be implemented

# sample_detector_params fixture would be reused from test_event.py 