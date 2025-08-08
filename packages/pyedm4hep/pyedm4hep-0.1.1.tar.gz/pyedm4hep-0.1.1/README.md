# PyEDM4hep

[![codecov](https://codecov.io/gh/murnanedaniel/pyEDM4hep/graph/badge.svg?token=JD9R3LYXH0)](https://codecov.io/gh/murnanedaniel/pyEDM4hep)
<!-- Add other badges here, e.g., PyPI version, license, build status -->

**PyEDM4hep** is a Pythonic interface for EDM4hep event data, combining the power of Pandas DataFrames with an intuitive object-oriented API. It enables fast, flexible analysis of HEP event data stored in ROOT files, with seamless navigation between particles, hits, and decay trees.

---

## Features
- **Object-oriented access** to particles, hits, and calorimeter data
- **Bulk operations** via Pandas DataFrames for high performance
- **ROOT file support** using `uproot`
- **Relationship navigation** (parents, daughters, hits, decay trees)
- **Built-in plotting** for event overviews, decay trees, and kinematics
- **Detector geometry awareness** for realistic analysis
- **Easy integration** with Jupyter and scientific Python stack

---

## Installation

PyEDM4hep requires Python 3.8+ and can be installed via pip:

    pip install pyedm4hep

Or from source:

    git clone https://github.com/murnanedaniel/pyEDM4hep.git
    cd pyEDM4hep
    pip install .

---

## Quickstart

```python
from pyedm4hep import EDM4hepEvent

# Define detector parameters (example values)
detector_params = {
    'tracking_radius': 1100.0,
    'tracking_z_max': 2500.0,
    'energy_threshold': 0.05
}

# Load an event from a ROOT file
file_path = 'path/to/events.root'
event = EDM4hepEvent(file_path, event_index=0, detector_params=detector_params)

# Access particles as a DataFrame
particles_df = event.get_particles_df()

# Work with a single particle
particle = event.get_particle(0)
print(particle.pdg, particle.pt, particle.vertex)

# Plot event overview
fig = event.plot.event_overview()
fig.suptitle("Event Overview")
```

---

## Documentation

- [API Reference](https://github.com/murnanedaniel/pyEDM4hep)
- [Examples & Tutorials](https://github.com/murnanedaniel/pyEDM4hep/tree/main/examples)

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
- Run tests with `pytest`.
- Ensure code coverage remains high.
- Document new features and update the changelog.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Built on top of [EDM4hep](https://github.com/key4hep/EDM4hep) and [uproot](https://github.com/scikit-hep/uproot).
- Inspired by the needs of the HEP analysis community. 