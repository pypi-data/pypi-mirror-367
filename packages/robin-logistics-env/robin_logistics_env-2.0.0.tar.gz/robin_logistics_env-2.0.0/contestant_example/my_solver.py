"""Simple solver for testing the robin-logistics-env package."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robin_logistics import LogisticsEnvironment


def solve(env):
    """
    Simple nearest neighbor solver implementation.
    
    Args:
        env: LogisticsEnvironment instance
        
    Returns:
        dict: Solution with routes
    """
    print(f"Solving problem with {env.num_warehouses} warehouses and {env.num_orders} orders")
    
    solution_routes = {}
    unassigned_orders = [order['order_id'] for order in env.order_requirements]
    
    for vehicle_spec in env.vehicle_specs:
        if not unassigned_orders:
            break
            
        vehicle_id = vehicle_spec['vehicle_id']
        home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
        route = [home_warehouse]
        current_weight = 0
        current_volume = 0
        
        while unassigned_orders:
            best_order = None
            min_distance = float('inf')
            
            for order_id in unassigned_orders:
                order_spec = next(o for o in env.order_requirements if o['order_id'] == order_id)
                
                if env.can_vehicle_serve_orders(
                    vehicle_id, [order_id], current_weight, current_volume
                ):
                    customer_location = order_spec['destination_node']
                    distance = env.get_distance(route[-1], customer_location)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_order = order_id
            
            if best_order is None:
                break
                
            order_spec = next(o for o in env.order_requirements if o['order_id'] == best_order)
            route.append(order_spec['destination_node'])
            current_weight += order_spec['total_weight_kg']
            current_volume += order_spec['total_volume_m3']
            unassigned_orders.remove(best_order)
        
        route.append(home_warehouse)
        
        if len(route) > 2:
            solution_routes[vehicle_id] = route
    
    return {"routes": solution_routes}


def test_solver():
    """Test the solver locally."""
    env = LogisticsEnvironment()
    
    print("Launching dashboard...")
    
    env.launch_dashboard(solve)


if __name__ == "__main__":
    test_solver()