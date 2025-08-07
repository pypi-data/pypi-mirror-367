# Contributing to Robin Logistics Environment

Thank you for your interest in contributing to the Robin Logistics Environment! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of logistics optimization or vehicle routing problems

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/robin-logistics-env.git
   cd robin-logistics-env
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. **Verify Installation**
   ```bash
   python -m pytest tests/
   ```

## 🔧 Development Workflow

### Branching Strategy

- `main`: Stable release branch
- `develop`: Integration branch for new features
- `feature/feature-name`: Individual feature branches
- `bugfix/issue-description`: Bug fix branches

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Run full test suite
   python -m pytest tests/
   
   # Run with coverage
   python -m pytest tests/ --cov=robin_logistics --cov-report=html
   
   # Run linting
   flake8 robin_logistics/
   black --check robin_logistics/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new optimization algorithm"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Code Style Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) coding standards
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Maximum line length: 88 characters (Black default)

### Documentation Style

- Use Google-style docstrings
- Include type hints for all function parameters and return values
- Provide examples for complex functions

#### Example Function Documentation

```python
def calculate_route_cost(self, vehicle_id: str, route: List[int]) -> float:
    """
    Calculate the total cost of a vehicle route.
    
    Args:
        vehicle_id: Unique identifier for the vehicle
        route: List of node IDs representing the route path
        
    Returns:
        Total cost including fixed costs and distance-based costs
        
    Raises:
        ValueError: If vehicle_id is not found
        
    Example:
        >>> env = LogisticsEnvironment()
        >>> cost = env.calculate_route_cost("VAN_001", [1, 5, 8, 1])
        >>> print(f"Route cost: ${cost:.2f}")
        Route cost: $125.50
    """
```

### Commit Message Format

Use conventional commits format:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add genetic algorithm solver example
fix: correct distance calculation in shortest path
docs: update API reference for new methods
test: add unit tests for inventory management
```

## 🧪 Testing Guidelines

### Test Structure

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`

### Writing Tests

```python
import pytest
from robin_logistics import LogisticsEnvironment

class TestLogisticsEnvironment:
    def setup_method(self):
        """Setup test environment before each test."""
        self.env = LogisticsEnvironment()
    
    def test_distance_calculation(self):
        """Test distance calculation between nodes."""
        distance = self.env.get_distance(1, 2)
        assert distance > 0
        assert isinstance(distance, float)
    
    def test_route_validation(self):
        """Test route validation functionality."""
        vehicle_id = self.env.get_available_vehicles()[0]
        warehouse_node = self.env.get_vehicle_home_warehouse(vehicle_id)
        route = [warehouse_node, warehouse_node]
        
        is_valid, message = self.env.validate_route(vehicle_id, route)
        assert is_valid
        assert isinstance(message, str)

    @pytest.mark.parametrize("route_length", [2, 5, 10])
    def test_route_statistics_various_lengths(self, route_length):
        """Test route statistics for different route lengths."""
        route = list(range(route_length))
        stats = self.env.calculate_route_statistics(route)
        
        assert "total_distance" in stats
        assert "total_stops" in stats
        assert stats["total_stops"] == route_length
```

### Test Coverage

- Aim for >90% test coverage
- All new features must include tests
- Bug fixes should include regression tests

## 📊 Performance Guidelines

### Optimization Principles

1. **Efficiency**: Algorithms should scale reasonably with problem size
2. **Memory**: Avoid unnecessary data copies or large intermediate structures
3. **Caching**: Cache expensive calculations when possible
4. **Parallel Processing**: Use multiprocessing for CPU-intensive tasks

### Performance Testing

```python
import time
import pytest

class TestPerformance:
    @pytest.mark.performance
    def test_large_problem_solving_time(self):
        """Ensure solver completes large problems in reasonable time."""
        env = LogisticsEnvironment()
        # Generate large problem instance
        
        start_time = time.time()
        solution = my_solver(env)
        execution_time = time.time() - start_time
        
        assert execution_time < 60  # Should complete within 1 minute
        assert solution is not None
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues to avoid duplicates
2. Ensure you're using the latest version
3. Try to reproduce the issue with minimal code

### Bug Report Template

```markdown
**Describe the Bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Create environment with '...'
2. Run solver with '....'
3. See error

**Expected Behavior**
What you expected to happen.

**Code Sample**
```python
from robin_logistics import LogisticsEnvironment

env = LogisticsEnvironment()
# Minimal code that reproduces the issue
```

**Environment**
- OS: [e.g., Windows 10, Ubuntu 20.04]
- Python Version: [e.g., 3.9.2]
- Package Version: [e.g., 1.2.3]

**Additional Context**
Any other context about the problem.
```

## ✨ Feature Requests

### Before Requesting

1. Check if the feature already exists
2. Consider if it fits the project's scope
3. Think about implementation complexity

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Explain why this feature would be useful.

**Proposed Implementation**
If you have ideas about how to implement this.

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## 🏗️ Architecture Guidelines

### Project Structure

```
robin_logistics/
├── __init__.py              # Public API exports
├── environment.py           # Main LogisticsEnvironment class
├── dashboard.py             # Streamlit dashboard
├── cli.py                   # Command-line interface
├── exceptions.py            # Custom exceptions
└── core/                    # Internal implementation
    ├── __init__.py
    ├── environment.py       # Core environment logic
    ├── simulation_engine.py # Simulation execution
    ├── data_generator.py    # Problem generation
    ├── config.py            # Configuration constants
    └── models/              # Data models
        ├── __init__.py
        ├── node.py
        ├── vehicle.py
        ├── warehouse.py
        ├── order.py
        └── sku.py
```

### Design Principles

1. **Separation of Concerns**: Clear separation between API, core logic, and visualization
2. **Single Responsibility**: Each class/function has one clear purpose
3. **Dependency Injection**: Pass dependencies explicitly rather than using globals
4. **Immutability**: Prefer immutable data structures where possible

### Adding New Features

#### New Solver Algorithms

1. Create example in `examples/solvers/`
2. Add documentation to README
3. Include performance benchmarks
4. Add to dashboard comparison tools

#### New Dashboard Features

1. Add to appropriate tab in `dashboard.py`
2. Ensure mobile responsiveness
3. Include help text and tooltips
4. Test with various problem sizes

#### New API Methods

1. Add to `LogisticsEnvironment` class
2. Include comprehensive docstrings
3. Add unit tests
4. Update API documentation

## 📚 Documentation

### Types of Documentation

1. **API Reference**: Docstrings in code
2. **User Guide**: README.md examples
3. **Developer Guide**: This CONTRIBUTING.md
4. **Tutorials**: Step-by-step examples

### Documentation Standards

- Keep examples up-to-date with code changes
- Include both simple and advanced usage examples
- Explain the "why" not just the "how"
- Use clear, concise language

## 🚀 Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Checklist

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Build and upload to PyPI

## 💬 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: For security issues or private matters

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn and contribute
- Follow the [Python Community Code of Conduct](https://www.python.org/psf/conduct/)

## 🎯 Priority Areas

### Current Focus Areas

1. **Performance Optimization**: Improve algorithm execution speed
2. **Algorithm Examples**: More solver implementations
3. **Visualization**: Enhanced dashboard features
4. **Documentation**: More tutorials and examples

### Good First Issues

Look for issues labeled:
- `good first issue`
- `help wanted`
- `documentation`
- `enhancement`

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Robin Logistics Environment! Your efforts help make logistics optimization more accessible to everyone. 🚛📦✨