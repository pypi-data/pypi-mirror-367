<div align="center">
    <img src="assets/TinkerBin-no-bg.png" width="220" title="TinkerBin Logo">
</div>

# Tinkerbin
[![tests](https://github.com/pudding-tech/tinkerbin/actions/workflows/tests.yml/badge.svg)](https://github.com/pudding-tech/tinkerbin/actions/workflows/tests.yml)

A collection of utility tools for scientific computing and data analysis, designed to streamline numerical simulations, data processing, and visualization workflows.

## Overview

Tinkerbin provides a comprehensive suite of tools for scientific computing applications, with a focus on:

- **Numpy array manipulation** and collection classes for managing complex datasets
- **Numerical integration** and Fourier transforms
- **I/O operations** and file management with intelligent path handling
- **Logging and printing utilities** for debugging and output formatting
- **Timer functions** for performance monitoring
- **Parameter storage and management** for simulation workflows
- **Function evaluation helpers** with dynamic argument handling
- **IPython integration** for enhanced interactive computing

## Installation

### From Source

```bash
git clone <repository-url>
cd tinkerbin
pip install -e .
```

## Quick Start

```python
import tinkerbin as tb
import tinkerbin.numpy_tools as npt
import tinkerbin.numerics_tools as num

# Set up logging
tb.setup_file_logging(log_folder_path="./logs", log_file_names="simulation.log")

# Start timing your code
tb.start_timer()

# Create mesh collections for parameter studies
class SimulationData(npt.NpMeshCollection):
    # Define your data structure
    pass

# Use numerical tools
discretization = num.Discretization(...)
result = num.discretize_func(your_function, discretization)

# Print timing information
tb.print_timing()
```

## Core Modules

### Numpy Tools (`tinkerbin.numpy_tools`)

Advanced array manipulation and collection classes:

- **`NpArrayCollection`**: Manage multiple related numpy arrays with attribute-style access
- **`NpMeshCollection`**: Handle meshgrid data with independent and dependent variables
- **Plotting utilities**: Integrated visualization tools for data analysis

```python
import tinkerbin.numpy_tools as npt

# Create a mesh collection for parameter studies
class MyData(npt.NpMeshCollection):
    temperature: float
    pressure: float
    result: float
    
    def calculate_results(self):
        # Your calculation logic here
        pass
```

### Numerical Tools (`tinkerbin.numerics_tools`)

Numerical integration, Fourier transforms, and mathematical functions:

- **Discretization classes**: Handle numerical discretization of continuous functions
- **Integration routines**: Numerical integration with various methods
- **Mathematical functions**: Linear ramps, bump functions, and other utilities

```python
import tinkerbin.numerics_tools as num

# Create discretization
t_disc = num.Discretization(start=0, stop=10, num_points=1000)

# Discretize a function
discretized_func = num.discretize_func(lambda t: np.sin(t), t_disc)

# Normalize the result
normalized = num.normalized(discretized_func, t_disc)
```

### I/O and File Management (`tinkerbin.io`)

Intelligent file operations and path handling:

- **`PathDic`**: Nested folder structure management
- **String transliteration**: Convert mathematical expressions to valid filenames
- **File operations**: Enhanced file handling with automatic directory creation

```python
import tinkerbin as tb

# Create organized folder structure
folder_structure = {
    'data': None,
    'figures': ['plots', 'analysis'],
    'logs': None
}

paths = tb.PathDic(folder_structure, root_path="./output")
```

### Logging and Output (`tinkerbin.logging`, `tinkerbin.printing`)

Comprehensive logging and formatted output:

- **File logging**: Automatic log file management
- **Formatted printing**: Enhanced print functions with formatting
- **Progress tracking**: Built-in progress indicators

```python
import tinkerbin as tb

# Set up file logging
tb.setup_file_logging(
    log_folder_path="./logs",
    log_file_names="simulation.log",
    append_to_existing=False
)

# Use enhanced logging
tb.log("Starting simulation...")
```

### Timing and Performance (`tinkerbin.timers`)

Performance monitoring and timing utilities:

```python
import tinkerbin as tb

# Start timing
tb.start_timer()

# Your code here...

# Print elapsed time
tb.print_timing()
```

### Function Evaluation (`tinkerbin.function_evaluation`)

Dynamic function handling and argument inspection:

- **Argument introspection**: Automatically determine function parameters
- **Dynamic evaluation**: Call functions with filtered argument dictionaries

```python
import tinkerbin as tb

# Get function arguments
args = tb.get_func_args(my_function)

# Call function with only relevant arguments from a dictionary
result = tb.pass_only_args(my_function, parameter_dict)
```

## Examples

The `examples/` directory contains complete simulation examples demonstrating:

- **Quantum optics simulations**: Fidelity calculations for single-photon states
- **Parameter studies**: Systematic exploration of parameter spaces
- **Data visualization**: Automated plotting and figure generation
- **Output management**: Organized file structure and logging

### Running Examples

```bash
cd examples
python F_max_1g_plot_vs_tau.py
```

## Development

### Development Dependencies

```bash
pip install -e ".[dev]"
```

### Code Style

The project uses Ruff for code formatting and linting:

```bash
ruff check .
ruff format .
```

### Testing

Run tests using:

```bash
python -m unittest discover tests/
```

## Project Structure

```
tinkerbin/
├── tinkerbin/                 # Main package
│   ├── numpy_tools/          # Array and mesh collection tools
│   ├── numerics_tools.py     # Numerical integration and math
│   ├── io.py                 # File operations and path handling
│   ├── logging.py            # Logging utilities
│   ├── timers.py             # Performance timing
│   ├── function_evaluation.py # Dynamic function handling
│   └── ...                   # Additional utilities
├── examples/                 # Example simulations
├── tests/                    # Test suite
└── output/                   # Generated output files
```

## Authors

- Jan Gulla
- Odd Cappelen

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

*Tinkerbin is designed for researchers and scientists who need reliable, efficient tools for numerical simulations and data analysis workflows.*
