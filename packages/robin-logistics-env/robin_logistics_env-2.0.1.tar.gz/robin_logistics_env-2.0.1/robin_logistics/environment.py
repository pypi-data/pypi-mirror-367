"""Main API interface for hackathon contestants."""

import os
import json
import tempfile
from typing import Dict, List, Tuple, Callable, Any, Optional
import pandas as pd

from .core.data_generator import generate_problem_instance
from .core.environment import Environment
from .core.simulation_engine import SimulationEngine  
from .core.visualizer import visualize_solution
from .core import config
from .exceptions import InvalidSolutionError, RouteValidationError
from .dashboard import create_dashboard


class LogisticsEnvironment:
    """
    Main interface for hackathon contestants.
    Provides read-only access to problem data and solution validation/visualization.
    """
    
    def __init__(self, problem_config: Optional[Dict] = None):
        """
        Initialize the logistics environment.
        
        Args:
            problem_config: Optional configuration override. If None, uses default config.
        """
        self._config = problem_config or config
        self._load_problem_instance()
        
    def _load_problem_instance(self):
        """Load and initialize the problem instance."""
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))
        
        problem_data = generate_problem_instance(self._config, nodes_df)
        
        self._env = Environment(
            nodes=problem_data['nodes'],
            edges_df=edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus']
        )
        
        self._nodes_df = nodes_df
        self._edges_df = edges_df
        self._last_solution = None
    
    def generate_scenario(self, scenario_key):
        """Generate a new problem instance for a specific scenario."""
        from .core.data_generator import generate_problem_instance
        
        problem_data = generate_problem_instance(self._config, self._nodes_df, scenario_key)
        
        new_env = Environment(
            nodes=problem_data['nodes'],
            edges_df=self._edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus']
        )
        
        return new_env
    
    def generate_scenario_custom(self, heavy_ratio: float, max_distance: int):
        """Generate a new problem instance with custom parameters."""
        from .core.data_generator import generate_custom_scenario
        
        problem_data = generate_custom_scenario(
            self._config, self._nodes_df, heavy_ratio, max_distance
        )
        
        new_env = Environment(
            nodes=problem_data['nodes'],
            edges_df=self._edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus']
        )
        
        return new_env
    
    def generate_scenario_from_config(self, config):
        """Generate a new problem instance from dashboard configuration."""
        from .core.data_generator import generate_scenario_from_config
        
        problem_data = generate_scenario_from_config(
            self._config, self._nodes_df, config
        )
        
        new_env = Environment(
            nodes=problem_data['nodes'],
            edges_df=self._edges_df,
            warehouses=problem_data['warehouses'],
            orders=problem_data['orders'],
            skus=problem_data['skus']
        )
        
        return new_env
    
    @property
    def num_warehouses(self) -> int:
        """Number of warehouses in the problem."""
        return len(self._env.warehouses)
    
    @property  
    def num_vehicles(self) -> int:
        """Total number of vehicles across all warehouses."""
        return len(self._env.get_all_vehicles())
        
    @property
    def num_orders(self) -> int:
        """Number of customer orders to fulfill."""
        return len(self._env.orders)
        
    @property
    def num_nodes(self) -> int:
        """Number of nodes in the road network."""
        return len(self._env.nodes)
    
    @property
    def warehouse_locations(self) -> List[Tuple[str, float, float]]:
        """List of warehouse locations as (warehouse_id, latitude, longitude)."""
        return [
            (wh.id, wh.location.lat, wh.location.lon) 
            for wh in self._env.warehouses.values()
        ]
    
    @property
    def customer_locations(self) -> List[Tuple[str, float, float]]:
        """List of customer locations as (order_id, latitude, longitude)."""
        return [
            (order.id, order.destination.lat, order.destination.lon)
            for order in self._env.orders.values()
        ]
    
    @property  
    def vehicle_specs(self) -> List[Dict]:
        """List of vehicle specifications."""
        specs = []
        for vehicle in self._env.get_all_vehicles():
            specs.append({
                'vehicle_id': vehicle.id,
                'type': vehicle.type,
                'home_warehouse': vehicle.home_warehouse_id,
                'capacity_weight_kg': vehicle.capacity_weight,
                'capacity_volume_m3': vehicle.capacity_volume,
                'max_distance_km': vehicle.max_distance,
                'cost_per_km': vehicle.cost_per_km,
                'fixed_cost': vehicle.fixed_cost
            })
        return specs
    
    @property
    def order_requirements(self) -> List[Dict]:
        """List of order requirements."""
        orders = []
        for order in self._env.orders.values():
            items = []
            total_weight = 0
            total_volume = 0
            
            for sku, qty in order.requested_items.items():
                items.append({
                    'sku_id': sku.id,
                    'quantity': qty,
                    'weight_per_unit': sku.weight,
                    'volume_per_unit': sku.volume
                })
                total_weight += sku.weight * qty
                total_volume += sku.volume * qty
            
            orders.append({
                'order_id': order.id,
                'destination_node': order.destination.id,
                'latitude': order.destination.lat,
                'longitude': order.destination.lon,
                'items': items,
                'total_weight_kg': total_weight,
                'total_volume_m3': total_volume
            })
        return orders

    
    def get_distance(self, node1: int, node2: int) -> float:
        """
        Get shortest path distance between two nodes.
        
        Args:
            node1: Source node ID
            node2: Destination node ID
            
        Returns:
            Distance in kilometers
        """
        return self._env.get_distance(node1, node2)
    
    def get_shortest_path(self, node1: int, node2: int) -> List[int]:
        """
        Get shortest path between two nodes.
        
        Args:
            node1: Source node ID  
            node2: Destination node ID
            
        Returns:
            List of node IDs representing the path
        """
        return self._env.get_path(node1, node2)
    
    def get_vehicle_home_warehouse(self, vehicle_id: str) -> int:
        """
        Get the home warehouse node ID for a vehicle.
        
        Args:
            vehicle_id: Vehicle identifier
            
        Returns:
            Node ID of the vehicle's home warehouse
        """
        for vehicle in self._env.get_all_vehicles():
            if vehicle.id == vehicle_id:
                return self._env.warehouses[vehicle.home_warehouse_id].location.id
        raise ValueError(f"Vehicle {vehicle_id} not found")
    
    def get_order_location(self, order_id: str) -> int:
        """
        Get the delivery location node ID for an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Node ID of the order's delivery location
        """
        if order_id in self._env.orders:
            return self._env.orders[order_id].destination.id
        raise ValueError(f"Order {order_id} not found")
    
    def get_available_vehicles(self) -> List[str]:
        """Get list of all available vehicle IDs."""
        return [v.id for v in self._env.get_all_vehicles()]
    
    def can_vehicle_serve_orders(self, vehicle_id: str, order_ids: List[str], 
                               current_weight: float = 0, current_volume: float = 0) -> bool:
        """
        Check if a vehicle can serve a set of orders given current load.
        
        Args:
            vehicle_id: Vehicle identifier
            order_ids: List of order IDs to check
            current_weight: Current load weight in kg
            current_volume: Current load volume in m³
            
        Returns:
            True if vehicle can serve all orders, False otherwise
        """
        vehicle = None
        for v in self._env.get_all_vehicles():
            if v.id == vehicle_id:
                vehicle = v
                break
        
        if not vehicle:
            return False
            
        total_weight = current_weight
        total_volume = current_volume
        
        for order_id in order_ids:
            if order_id not in self._env.orders:
                return False
            order = self._env.orders[order_id]
            order_weight, order_volume = self._env.get_order_requirements(order)
            total_weight += order_weight
            total_volume += order_volume
            
        return (total_weight <= vehicle.capacity_weight and 
                total_volume <= vehicle.capacity_volume)
    
    def validate_route(self, vehicle_id: str, route: List[int]) -> Tuple[bool, str]:
        """
        Validate a single vehicle route.
        
        Args:
            vehicle_id: Vehicle identifier
            route: List of node IDs representing the route
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
    
            solution = {"routes": {vehicle_id: route}}
            is_valid, message = self._env.validate_solution(solution)
            return is_valid, message
        except Exception as e:
            return False, str(e)
    
    def estimate_route_cost(self, vehicle_id: str, route: List[int]) -> float:
        """
        Estimate the cost of a route.
        
        Args:
            vehicle_id: Vehicle identifier
            route: List of node IDs representing the route
            
        Returns:
            Estimated cost in currency units
        """
        vehicle = None
        for v in self._env.get_all_vehicles():
            if v.id == vehicle_id:
                vehicle = v
                break
                
        if not vehicle or len(route) < 2:
            return 0.0
            
        distance = self._env.get_route_distance(route)
        return vehicle.fixed_cost + (distance * vehicle.cost_per_km)
    
    def get_warehouse_inventory(self, warehouse_id: str = None) -> Dict:
        """
        Get inventory information for warehouses.
        
        Args:
            warehouse_id: Specific warehouse ID, or None for all warehouses
            
        Returns:
            Dictionary of warehouse inventory data
        """
        if warehouse_id:
            if warehouse_id not in self._env.warehouses:
                raise ValueError(f"Warehouse {warehouse_id} not found")
            wh = self._env.warehouses[warehouse_id]
            return {
                'warehouse_id': wh.id,
                'location_node': wh.location.id,
                'inventory': {sku.id: qty for sku, qty in wh.inventory.items()}
            }
        else:
            return {
                wh.id: {
                    'location_node': wh.location.id,
                    'inventory': {sku.id: qty for sku, qty in wh.inventory.items()}
                }
                for wh in self._env.warehouses.values()
            }
    
    def get_sku_info(self) -> Dict:
        """
        Get information about all SKUs (Stock Keeping Units).
        
        Returns:
            Dictionary with SKU specifications
        """
        skus = {}
        for wh in self._env.warehouses.values():
            for sku in wh.inventory.keys():
                if sku.id not in skus:
                    skus[sku.id] = {
                        'id': sku.id,
                        'weight_kg': sku.weight,
                        'volume_m3': sku.volume
                    }
        return skus
    
    def get_nodes_within_distance(self, center_node: int, max_distance: float) -> List[int]:
        """
        Get all nodes within a certain distance from a center node.
        
        Args:
            center_node: Center node ID
            max_distance: Maximum distance in kilometers
            
        Returns:
            List of node IDs within the specified distance
        """
        nearby_nodes = []
        for node in self._env.nodes.values():
            if node.id != center_node:
                distance = self.get_distance(center_node, node.id)
                if distance <= max_distance:
                    nearby_nodes.append(node.id)
        return nearby_nodes
    
    def calculate_route_statistics(self, route: List[int]) -> Dict:
        """
        Calculate comprehensive statistics for a route.
        
        Args:
            route: List of node IDs representing the route
            
        Returns:
            Dictionary with route statistics
        """
        if len(route) < 2:
            return {
                'total_distance': 0,
                'total_stops': len(route),
                'unique_stops': len(set(route)),
                'is_roundtrip': False
            }
        
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.get_distance(route[i], route[i + 1])
        
        return {
            'total_distance': total_distance,
            'total_stops': len(route),
            'unique_stops': len(set(route)),
            'is_roundtrip': route[0] == route[-1] if len(route) > 2 else False,
            'avg_distance_per_segment': total_distance / (len(route) - 1) if len(route) > 1 else 0
        }
    
    def get_unassigned_orders(self, current_solution: Dict) -> List[str]:
        """
        Get list of orders not assigned in the current solution.
        
        Args:
            current_solution: Current solution dictionary with routes
            
        Returns:
            List of unassigned order IDs
        """
        assigned_destinations = set()
        for route in current_solution.get('routes', {}).values():
            assigned_destinations.update(route)
        
        unassigned = []
        for order in self._env.orders.values():
            if order.destination.id not in assigned_destinations:
                unassigned.append(order.id)
        
        return unassigned

    
    def run_optimization(self, solver_function: Callable[['LogisticsEnvironment'], Dict]) -> Dict:
        """
        Run optimization using the provided solver function.
        
        Args:
            solver_function: Function that takes this environment and returns a solution dict
            
        Returns:
            Results dictionary with cost, validity, and other metrics
        """
        try:
            solution = solver_function(self)
            
            if not isinstance(solution, dict) or "routes" not in solution:
                raise InvalidSolutionError("Solution must be a dictionary with 'routes' key")
            
            self._last_solution = solution
            
            is_valid, message = self._env.validate_solution(solution)
            
            if not is_valid:
                return {
                    'is_valid': False,
                    'error_message': message,
                    'cost': 0.0,
                    'vehicles_used': 0,
                    'orders_fulfilled': 0,
                    'solution': solution
                }
            
            sim_engine = SimulationEngine(self._env, solution)
            final_state, logs = sim_engine.run_simulation()
            
            return {
                'is_valid': final_state['is_valid'],
                'cost': final_state['total_cost'],
                'vehicles_used': final_state['vehicles_used'],
                'orders_fulfilled': final_state['orders_delivered'],
                'message': final_state['message'],
                'solution': solution,
                'simulation_logs': logs
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error_message': f"Solver error: {str(e)}",
                'cost': 0.0,
                'vehicles_used': 0,
                'orders_fulfilled': 0,
                'solution': {}
            }
    
    def launch_dashboard(self, solver_function: Callable[['LogisticsEnvironment'], Dict] = None):
        """Launch the interactive dashboard."""
        create_dashboard(self._env, solver_function)

    
    def save_solution(self, solution: Dict, filepath: str):
        """Save solution to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(solution, f, indent=2)
    
    def load_solution(self, filepath: str) -> Dict:
        """Load solution from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def export_problem_data(self, filepath: str):
        """Export problem instance data for external analysis."""
        data = {
            'warehouses': [
                {
                    'id': wh.id,
                    'location': {'node_id': wh.location.id, 'lat': wh.location.lat, 'lon': wh.location.lon},
                    'inventory': {sku.id: qty for sku, qty in wh.inventory.items()},
                    'vehicles': [
                        {
                            'id': v.id,
                            'type': v.type,
                            'capacity_weight': v.capacity_weight,
                            'capacity_volume': v.capacity_volume,
                            'max_distance': v.max_distance,
                            'cost_per_km': v.cost_per_km,
                            'fixed_cost': v.fixed_cost
                        } for v in wh.vehicles
                    ]
                } for wh in self._env.warehouses.values()
            ],
            'orders': [
                {
                    'id': order.id,
                    'destination': {'node_id': order.destination.id, 'lat': order.destination.lat, 'lon': order.destination.lon},
                    'items': {sku.id: qty for sku, qty in order.requested_items.items()}
                } for order in self._env.orders.values()
            ],
            'skus': [
                {
                    'id': sku.id,
                    'weight': sku.weight,
                    'volume': sku.volume
                } for sku in self._env.skus.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)