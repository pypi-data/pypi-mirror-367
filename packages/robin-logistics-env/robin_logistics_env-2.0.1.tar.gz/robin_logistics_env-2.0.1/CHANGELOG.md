# Changelog

All notable changes to the Robin Logistics Environment will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-01-XX

### Added
- **Interactive Problem Definition Tab**: Complete control over problem parameters
  - Configurable number of orders, warehouses, and vehicles
  - Dynamic inventory distribution across warehouses
  - Heavy/light item ratio controls
  - Delivery distance constraints
- **Comprehensive Performance Metrics**: 
  - Solver timing (execution time tracking)
  - Solution quality metrics (cost per order, delivery efficiency)
  - Resource utilization (fleet usage, inventory consumption)
- **Enhanced Helper Functions** for contestants:
  - `get_warehouse_inventory()`: Access stock levels
  - `get_sku_info()`: Product specifications
  - `get_nodes_within_distance()`: Geographic analysis
  - `calculate_route_statistics()`: Route analysis
  - `get_unassigned_orders()`: Solution completeness checking
- **Improved Dashboard Experience**:
  - Run Simulation button moved to Problem Definition tab
  - Full-size map visualization on launch
  - Order detail inspector with complete specifications
  - Real-time configuration validation
- **Advanced Scenario Generation**: Custom problem instances from dashboard parameters
- **Better Documentation**: Comprehensive API reference and examples

### Changed
- **Dashboard Workflow**: Simulation now triggered from Problem Definition tab
- **Function Serialization**: Switched from `pickle` to `dill` for better compatibility
- **Performance Focus**: All metrics now tracked and displayed prominently
- **API Enhancement**: More intuitive method names and comprehensive docstrings
- **Problem Overview**: Moved to top of dashboard for immediate visibility

### Removed
- **Quick Scenario Test**: Replaced with comprehensive Problem Definition editor
- **Preset Scenario Dropdown**: Replaced with dynamic sliders
- **Unnecessary Comments**: Cleaned codebase while preserving docstrings
- **Dead Code**: Removed unused functions and imports

### Fixed
- **Local Development**: Direct import support without package installation
- **Serialization Issues**: Resolver function passing between processes
- **Map Visualization**: Immediate display without button click
- **Configuration Persistence**: Proper session state management

## [1.2.0] - 2024-01-XX

### Added
- Dynamic scenario generation with custom parameters
- Scenario-based order generation (heavy/light item ratios)
- Distance-based customer filtering
- Interactive dashboard with Streamlit
- Solution visualization with Folium maps
- Real-time performance monitoring

### Changed
- Improved data generator with scenario support
- Enhanced environment API with helper methods
- Better separation between public API and core implementation

### Fixed
- Distance calculation accuracy
- Route validation edge cases
- Memory usage in large problem instances

## [1.1.0] - 2024-01-XX

### Added
- Multi-depot vehicle routing support
- Vehicle capacity constraints (weight and volume)
- Inventory management across warehouses
- Solution validation framework
- Cost calculation with fixed and variable components
- CLI interface for quick testing

### Changed
- Refactored core environment architecture
- Improved error handling and validation
- Enhanced documentation and examples

### Fixed
- Route distance calculations
- Vehicle home warehouse assignments
- Order fulfillment validation

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Robin Logistics Environment
- Basic vehicle routing problem framework
- Network graph with real geographical data
- Simple solver examples
- Core simulation engine
- Basic validation and cost calculation

### Features
- Multi-warehouse support
- Vehicle fleet management  
- Order processing and fulfillment
- Distance-based routing
- Solution format specification

---

## Development Guidelines

### Version Number Scheme
- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes and minor improvements

### Release Process
1. Update version in `setup.py`
2. Update this CHANGELOG.md
3. Create release tag: `git tag v2.0.0`
4. Build and upload to PyPI: `python -m build && twine upload dist/*`

### Categories
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Now removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes