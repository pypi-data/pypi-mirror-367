# Robin Logistics - Contestant Examples

This directory contains example solver implementations to help you get started with the Robin Logistics Environment.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Basic Example

```bash
python my_solver.py
```

This will launch the interactive dashboard where you can:
- Configure problem parameters in the "Problem Definition" tab
- Click "🚀 Run Simulation" to test your solver
- Analyze results in the performance metrics

### 3. Run Advanced Example

```bash
python advanced_solver.py
```

## 📁 File Overview

### `my_solver.py`
Basic greedy solver implementation that demonstrates:
- Loading the logistics environment
- Accessing problem data (warehouses, orders, vehicles)
- Building a simple solution
- Launching the interactive dashboard

### `advanced_solver.py`
More sophisticated solver with:
- Distance-based optimization
- Capacity constraint handling
- Multi-vehicle coordination
- Performance optimization techniques

### `requirements.txt`
All necessary dependencies for running the examples locally.

## 🎯 Understanding the Problem

### Problem Components

1. **Warehouses**: Distribution centers with inventory and vehicle fleets
2. **Orders**: Customer delivery requests with specific items and locations
3. **Vehicles**: Fleet with capacity and cost constraints
4. **Network**: Road network connecting all locations

### Solution Format

Your solver must return a dictionary with vehicle routes:

```python
{
    "routes": {
        "LightVan_1_1": [warehouse_node, customer_node_1, customer_node_2, warehouse_node],
        "LightVan_1_2": [warehouse_node, customer_node_3, warehouse_node],
        # ... more routes
    }
}
```

### Key Constraints

- **Vehicle Capacity**: Weight and volume limits
- **Route Structure**: Must start and end at vehicle's home warehouse
- **Order Fulfillment**: Each order must be completely satisfied
- **Inventory Limits**: Limited stock at warehouses

## 🔧 Environment API

### Essential Methods

```python
# Problem information
env.num_warehouses          # Number of distribution centers
env.num_orders             # Number of customer orders
env.warehouse_locations    # [(warehouse_id, lat, lon), ...]
env.order_requirements     # Detailed order specifications

# Distance and routing
env.get_distance(node1, node2)              # Shortest distance
env.get_shortest_path(node1, node2)         # Complete path
env.calculate_route_statistics(route)       # Route analysis

# Vehicle management
env.get_available_vehicles()                # List of vehicle IDs
env.can_vehicle_serve_orders(vehicle_id, orders)  # Capacity check
env.get_vehicle_home_warehouse(vehicle_id)  # Home base location

# Solution validation
env.validate_route(vehicle_id, route)       # Check if route is valid
env.estimate_route_cost(vehicle_id, route)  # Calculate route cost
```

### Helper Functions

```python
# Inventory and warehouse management
env.get_warehouse_inventory()               # Stock levels
env.get_sku_info()                         # Product specifications

# Geographic analysis
env.get_nodes_within_distance(center, max_dist)  # Nearby locations
env.get_order_location(order_id)           # Order destination

# Solution analysis
env.get_unassigned_orders(solution)        # Orders not in solution
```

## 💡 Algorithm Development Tips

### 1. Start Simple
```python
def simple_greedy_solver(env):
    """Assign each order to the nearest available vehicle"""
    routes = {}
    orders = env.order_requirements.copy()
    
    for vehicle_id in env.get_available_vehicles():
        if not orders:
            break
            
        warehouse_node = env.get_vehicle_home_warehouse(vehicle_id)
        route = [warehouse_node]
        
        # Pick the first order that fits
        for i, order in enumerate(orders):
            if env.can_vehicle_serve_orders(vehicle_id, [order['order_id']]):
                route.append(order['destination_node'])
                orders.pop(i)
                break
        
        route.append(warehouse_node)
        routes[vehicle_id] = route
    
    return {"routes": routes}
```

### 2. Add Distance Optimization
```python
def nearest_neighbor_solver(env):
    """Use nearest neighbor heuristic for route construction"""
    routes = {}
    remaining_orders = env.order_requirements.copy()
    
    for vehicle_id in env.get_available_vehicles():
        if not remaining_orders:
            break
            
        warehouse_node = env.get_vehicle_home_warehouse(vehicle_id)
        current_node = warehouse_node
        route = [warehouse_node]
        vehicle_orders = []
        
        while remaining_orders:
            # Find nearest order that fits in vehicle
            best_order = None
            best_distance = float('inf')
            best_index = -1
            
            for i, order in enumerate(remaining_orders):
                if env.can_vehicle_serve_orders(vehicle_id, 
                    vehicle_orders + [order['order_id']]):
                    
                    distance = env.get_distance(current_node, order['destination_node'])
                    if distance < best_distance:
                        best_distance = distance
                        best_order = order
                        best_index = i
            
            if best_order is None:
                break
                
            # Add order to route
            current_node = best_order['destination_node']
            route.append(current_node)
            vehicle_orders.append(best_order['order_id'])
            remaining_orders.pop(best_index)
        
        route.append(warehouse_node)
        routes[vehicle_id] = route
    
    return {"routes": routes}
```

### 3. Advanced Optimization Techniques

- **Local Search**: 2-opt, 3-opt improvements
- **Genetic Algorithms**: Population-based optimization
- **Simulated Annealing**: Probabilistic optimization
- **Clarke-Wright Savings**: Classical VRP heuristic

## 📊 Performance Analysis

### Dashboard Features

1. **Problem Definition**: Configure problem parameters
2. **Performance Metrics**: Timing, costs, efficiency analysis
3. **Interactive Map**: Visual route inspection
4. **Order Details**: Comprehensive order breakdown

### Key Metrics

- **Solver Time**: Algorithm execution speed
- **Solution Quality**: Total cost, delivery efficiency
- **Resource Utilization**: Vehicle usage, inventory consumption
- **Constraint Satisfaction**: Route validity, capacity compliance

## 🎮 Interactive Development

### Dashboard Workflow

1. **Configure Problem**: Adjust parameters in "Problem Definition" tab
2. **Run Solver**: Click "🚀 Run Simulation" 
3. **Analyze Results**: Review performance metrics and visualizations
4. **Iterate**: Modify algorithm based on insights

### Testing Strategies

- **Small Problems**: Debug with 5-10 orders
- **Varied Scenarios**: Test different item ratios and distances
- **Performance Limits**: Push to 30+ orders for scalability
- **Edge Cases**: Empty orders, single vehicle, capacity exceeded

## 🔍 Debugging Tips

### Common Issues

1. **Invalid Routes**: Check start/end at warehouse
2. **Capacity Exceeded**: Use `can_vehicle_serve_orders()`
3. **Unreachable Nodes**: Verify node IDs exist
4. **Empty Solutions**: Ensure at least one route per vehicle

### Debugging Tools

```python
# Validate your solution before returning
def debug_solution(env, solution):
    for vehicle_id, route in solution['routes'].items():
        is_valid, message = env.validate_route(vehicle_id, route)
        if not is_valid:
            print(f"Invalid route for {vehicle_id}: {message}")
        
        cost = env.estimate_route_cost(vehicle_id, route)
        stats = env.calculate_route_statistics(route)
        print(f"Vehicle {vehicle_id}: Cost=${cost:.2f}, Distance={stats['total_distance']:.1f}km")
```

## 🏆 Optimization Goals

### Primary Objectives
1. **Minimize Total Cost**: Reduce distance and fixed costs
2. **Maximize Delivery Rate**: Fulfill as many orders as possible
3. **Optimize Fleet Usage**: Efficient vehicle utilization

### Advanced Objectives
1. **Balance Workload**: Even distribution across vehicles
2. **Minimize Route Overlap**: Reduce redundant coverage
3. **Geographic Clustering**: Group nearby deliveries

## 📚 Additional Resources

- [Vehicle Routing Problem (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [NetworkX Documentation](https://networkx.org/documentation/)
- [Optimization Algorithms Reference](https://en.wikipedia.org/wiki/Category:Optimization_algorithms_and_methods)

## 🤝 Getting Help

- Check the main README.md for comprehensive API documentation
- Use the dashboard's interactive features for visual debugging
- Experiment with different problem configurations
- Focus on correctness first, then optimize for performance

---

**Happy Optimizing!** 🚛📦✨

Remember: The best algorithm is one that works reliably and can be understood and improved over time.