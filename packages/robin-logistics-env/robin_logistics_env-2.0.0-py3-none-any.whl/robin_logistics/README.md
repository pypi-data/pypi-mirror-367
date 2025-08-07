# Robin Logistics Environment

Multi-depot vehicle routing problem simulation environment for hackathon contestants.

## Package Structure

```
robin_logistics/
├── __init__.py           # Public API (LogisticsEnvironment)
├── environment.py        # Main environment class
├── exceptions.py         # Custom exceptions
├── dashboard.py         # Interactive dashboard
├── cli.py              # Command line interface
├── data/               # Map data (nodes.csv, edges.csv)
└── core/               # Internal implementation
    ├── config.py
    ├── data_generator.py
    ├── environment.py
    ├── simulation_engine.py
    ├── visualizer.py
    ├── models/
    └── util/
```

## Testing Package Locally

```bash
pip install -e .
python -c "from robin_logistics import LogisticsEnvironment; print('Success')"
robin-logistics --help
```

## Deploy to PyPI

```bash
python -m build
twine upload dist/*
```

## API Reference

### LogisticsEnvironment Properties
- `num_warehouses`, `num_vehicles`, `num_orders`, `num_nodes`
- `warehouse_locations`, `customer_locations`  
- `vehicle_specs`, `order_requirements`

### LogisticsEnvironment Methods
- `get_distance(node1, node2)` - Distance in km
- `get_shortest_path(node1, node2)` - Path as node list
- `can_vehicle_serve_orders(vehicle_id, order_ids)` - Capacity check
- `run_optimization(solver_function)` - Run solver and get results
- `launch_dashboard(solver_function)` - Interactive visualization

### Example Usage
```python
from robin_logistics import LogisticsEnvironment

def my_solver(env):
    return {"routes": {"vehicle_1": [warehouse, customer, warehouse]}}

env = LogisticsEnvironment()
results = env.run_optimization(my_solver)
env.launch_dashboard(my_solver)
```