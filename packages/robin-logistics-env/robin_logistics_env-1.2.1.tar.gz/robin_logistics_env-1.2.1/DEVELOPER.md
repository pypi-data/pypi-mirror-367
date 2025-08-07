# Robin Logistics Environment - Developer Guide

Internal documentation for package development, deployment, and maintenance.

## 📁 Project Structure

```
robin-logistics-env/
├── README.md                     # Main user documentation (PyPI description)
├── DEVELOPER.md                  # This file - development guide  
├── LICENSE                       # MIT License
├── setup.py                      # Package configuration
├── MANIFEST.in                   # Include additional files in package
├── requirements.txt              # Development dependencies
├── redeploy.sh                   # Automated deployment script
├── .gitignore                    # Git exclusions
│
├── robin_logistics/              # Main package
│   ├── __init__.py              # Public API exports
│   ├── environment.py           # Main LogisticsEnvironment class
│   ├── cli.py                   # Command line interface
│   ├── dashboard.py             # Streamlit dashboard generator
│   ├── exceptions.py            # Custom exception classes
│   │
│   ├── data/                    # Map data (included in package)
│   │   ├── nodes.csv           # 7,571 road network nodes
│   │   └── edges.csv           # 16,411 road network edges
│   │
│   └── core/                    # Internal implementation
│       ├── __init__.py
│       ├── config.py           # Problem instance configuration
│       ├── data_generator.py   # Random problem generation
│       ├── environment.py      # Core simulation environment
│       ├── simulation_engine.py # Route execution simulation
│       ├── visualizer.py       # Map visualization
│       └── models/             # Data model classes
│           ├── __init__.py
│           ├── node.py
│           ├── sku.py
│           ├── order.py
│           ├── vehicle.py
│           └── warehouse.py
│
├── contestant_example/           # Example implementations
│   ├── my_solver.py             # Basic nearest neighbor solver
│   ├── advanced_solver.py       # Savings algorithm solver
│   ├── requirements.txt         # Contestant dependencies
│   └── temp_map.html           # Generated visualization
│
├── dist/                        # Built packages (auto-generated)
└── robin_logistics_env.egg-info/ # Package metadata (auto-generated)
```

## 🏗️ Architecture Overview

### Core Components

#### **1. Public API Layer** (`environment.py`)
- **LogisticsEnvironment**: Main contestant interface
- **Read-only properties**: Problem data access
- **Utility methods**: Distance, capacity checking, validation
- **Execution methods**: run_optimization(), launch_dashboard()

#### **2. Internal Engine** (`core/`)
- **Environment**: Core problem representation and validation
- **SimulationEngine**: Stateful route execution with inventory tracking
- **DataGenerator**: Random problem instance creation
- **Models**: Simple data classes for domain objects

#### **3. Interface Layer**
- **CLI**: Command-line tool with solver loading
- **Dashboard**: Streamlit-based interactive visualization
- **Visualizer**: Folium map generation

#### **4. Data Layer**
- **Static CSV files**: Real road network data (Cairo, Egypt)
- **Configuration**: Problem parameters and constraints

### Design Principles

- **Clean API**: Contestants see only what they need
- **Read-only Access**: No accidental state modification
- **Validation First**: Comprehensive constraint checking
- **Real Data**: Actual road networks and realistic constraints
- **Immediate Feedback**: Visual validation and debugging tools

## 🔧 Development Setup

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Install development dependencies
pip install -r requirements.txt
pip install build twine  # For packaging and publishing
```

### Local Development

```bash
# Install in development mode
pip install -e .

# Verify installation
python -c "from robin_logistics import LogisticsEnvironment; print('Success')"
robin-logistics --help

# Test with examples
cd contestant_example
python my_solver.py
python advanced_solver.py
```

### Running Tests

```bash
# Basic functionality test
python contestant_example/my_solver.py

# CLI interface test
robin-logistics --solver contestant_example/my_solver.py --dashboard

# Package import test
python -c "
from robin_logistics import LogisticsEnvironment
env = LogisticsEnvironment()
print(f'Loaded: {env.num_warehouses} warehouses, {env.num_vehicles} vehicles')
"
```

## 📦 Package Configuration

### setup.py Configuration

Key settings for PyPI publishing:

```python
setup(
    name="robin-logistics-env",
    version="1.2.0",                    # Update for each release
    author="Robin Hackathon Team",
    description="Multi-depot vehicle routing problem simulation environment",
    long_description=long_description,   # Pulled from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/robin/hackathon-2025",
    
    # Package discovery
    packages=find_packages(),
    
    # Include data files
    include_package_data=True,
    package_data={
        "robin_logistics": ["data/*.csv"],
    },
    
    # Dependencies
    install_requires=[
        "pandas>=1.3.0",
        "networkx>=2.6.0", 
        "streamlit>=1.28.0",
        "folium>=0.14.0",
    ],
    
    # Command line tools
    entry_points={
        "console_scripts": [
            "robin-logistics=robin_logistics.cli:main",
        ],
    },
    
    # Python version support
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

### MANIFEST.in

Ensures additional files are included in the package:

```
include README.md
include LICENSE
include MANIFEST.in
recursive-include robin_logistics/data *.csv
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

## 🚀 Deployment Process

### Version Management

1. **Update Version Number** in `setup.py`
2. **Update README.md** if API changes
3. **Test Locally** with example solvers
4. **Build and Deploy** using automated script

### Manual Deployment

```bash
# 1. Clean previous builds
rm -rf dist/ build/ *.egg-info

# 2. Build package
python -m build

# 3. Check package integrity
twine check dist/*

# 4. Upload to PyPI
twine upload dist/*
```

### Automated Deployment

```bash
# Use the deployment script
./redeploy.sh
```

**Script Contents:**
```bash
#!/bin/bash
echo "🏗️ Building robin-logistics-env package..."

# Clean up previous builds
rm -rf dist/ build/ robin_logistics_env.egg-info/

# Build the package
python -m build

# Check package
echo "📋 Checking package integrity..."
twine check dist/*

# Upload to PyPI
echo "🚀 Uploading to PyPI..."
twine upload dist/*

echo "✅ Deployment complete!"
```

### Release Checklist

- [ ] All tests pass locally
- [ ] Version number updated in setup.py
- [ ] README.md reflects current API
- [ ] Example solvers work correctly
- [ ] CLI tool functions properly
- [ ] Dashboard launches without errors
- [ ] Package builds without warnings
- [ ] twine check passes
- [ ] Dependencies are up to date

## 🔍 Testing Strategy

### Unit Testing (Manual)

```bash
# API completeness
python -c "
from robin_logistics import LogisticsEnvironment
env = LogisticsEnvironment()
assert hasattr(env, 'num_warehouses')
assert hasattr(env, 'run_optimization')
assert hasattr(env, 'launch_dashboard')
print('✓ API complete')
"

# Data integrity
python -c "
from robin_logistics import LogisticsEnvironment
env = LogisticsEnvironment()
assert env.num_nodes == 7571
assert env.num_warehouses == 2
assert env.num_vehicles == 60
assert env.num_orders == 15
print('✓ Problem scale correct')
"

# Example solver validation
python -c "
from contestant_example.my_solver import solve
from robin_logistics import LogisticsEnvironment
env = LogisticsEnvironment()
results = env.run_optimization(solve)
assert results['is_valid'] == True
assert results['cost'] > 0
print('✓ Example solver works')
"
```

### Integration Testing

```bash
# CLI functionality
robin-logistics --export-problem test_export.json
robin-logistics --solver contestant_example/my_solver.py --output test_solution.json

# Package installation
pip install dist/robin_logistics_env-*.whl
python -c "from robin_logistics import LogisticsEnvironment; print('✓ Package installs')"
```

## 🛠️ Maintenance Tasks

### Updating Problem Configuration

Edit `robin_logistics/core/config.py`:

```python
# Scale problem size
NUM_CUSTOMER_LOCATIONS = 25  # Increase difficulty
NUM_ORDERS = 20
MAX_SKUS_PER_ORDER = 3

# Adjust fleet composition
WAREHOUSE_DEFS = [
    {
        "num_to_generate": 3,  # More warehouses
        "vehicle_fleet": [
            {"vehicle_type": "LightVan", "count": 20, ...},
            {"vehicle_type": "Truck", "count": 10, ...},  # Add vehicle types
        ]
    }
]
```

### Adding New Map Data

1. **Replace CSV files** in `robin_logistics/data/`
2. **Ensure format compatibility**:
   - `nodes.csv`: node_id, longitude, latitude
   - `edges.csv`: u, v, length, name, highway
3. **Update package version** and rebuild

### Performance Optimization

**Distance Calculation Caching**:
- Already implemented in `core/environment.py`
- Cache hit rate typically >95% for route construction

**Memory Usage**:
- NetworkX graph: ~50MB for 7K nodes
- Problem instance: ~1MB
- Consider node reduction for larger networks

## 🐛 Common Issues

### Development Issues

**Import Errors**:
```bash
# Reinstall in development mode
pip uninstall robin-logistics-env
pip install -e .
```

**Missing Data Files**:
- Check MANIFEST.in includes data directory
- Verify setup.py package_data configuration

**CLI Tool Not Found**:
- Reinstall package: `pip install -e .`
- Check entry_points in setup.py

### Deployment Issues

**PyPI Upload Fails**:
- Check credentials: `twine configure`
- Verify package integrity: `twine check dist/*`
- Ensure unique version number

**Package Size Too Large**:
- Review MANIFEST.in exclusions
- Consider compressing CSV data
- Remove unnecessary files

**Dependency Conflicts**:
- Pin exact versions in setup.py
- Test with fresh virtual environment
- Update compatibility matrix

## 📊 Package Analytics

### Size Breakdown
- **Core Python code**: ~50KB
- **Map data (CSV)**: ~1.2MB  
- **Total package**: ~1.3MB
- **Installed size**: ~2MB

### Performance Metrics
- **Environment initialization**: <1 second
- **Distance calculation**: <1ms (cached)
- **Route validation**: ~10ms for 15 orders
- **Dashboard launch**: ~3-5 seconds

## 🔐 Security Considerations

- **No external API calls** during optimization
- **Read-only file access** from package data
- **Isolated execution** environment for contestant code
- **No persistent state** between runs
- **Safe evaluation** of solver functions

## 📈 Future Enhancements

### Potential Features
- **Multiple map regions** (London, NYC, Tokyo)
- **Dynamic problem generation** with different scales
- **Performance benchmarking** tools
- **Algorithm visualization** for educational purposes
- **Real-time optimization** challenges

### API Stability
- **Current API**: Stable, no breaking changes planned
- **Internal implementation**: May evolve for performance
- **Data format**: CSV structure locked for compatibility

---

**For questions or issues, contact the development team.**