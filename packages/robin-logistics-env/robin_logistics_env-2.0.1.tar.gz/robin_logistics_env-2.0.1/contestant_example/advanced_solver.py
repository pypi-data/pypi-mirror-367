"""Advanced solver example with multiple optimization strategies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robin_logistics import LogisticsEnvironment


def solve(env):
    """
    Advanced multi-depot vehicle routing solver using savings algorithm approach.
    
    Args:
        env: LogisticsEnvironment instance
        
    Returns:
        dict: Solution with routes
    """
    print(f"Solving problem with {env.num_warehouses} warehouses, {env.num_orders} orders, and {env.num_vehicles} vehicles")
    
    solution_routes = {}
    assigned_orders = set()
    available_vehicles = env.get_available_vehicles()
    
    vehicle_loads = {v_id: {'weight': 0, 'volume': 0, 'orders': []} for v_id in available_vehicles}
    
    for order_spec in env.order_requirements:
        order_id = order_spec['order_id']
        if order_id in assigned_orders:
            continue
            
        order_weight = order_spec['total_weight_kg']
        order_volume = order_spec['total_volume_m3']
        customer_node = order_spec['destination_node']
        
        best_vehicle = None
        min_cost_increase = float('inf')
        
        for vehicle_id in available_vehicles:
            if not env.can_vehicle_serve_orders(
                vehicle_id, [order_id], 
                vehicle_loads[vehicle_id]['weight'], 
                vehicle_loads[vehicle_id]['volume']
            ):
                continue
            
            home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
            
            if vehicle_id not in solution_routes:
                distance = 2 * env.get_distance(home_warehouse, customer_node)
                vehicle_spec = next(v for v in env.vehicle_specs if v['vehicle_id'] == vehicle_id)
                cost_increase = vehicle_spec['fixed_cost'] + distance * vehicle_spec['cost_per_km']
            else:
                current_route = solution_routes[vehicle_id]
                last_customer = current_route[-2]
                
                insertion_distance = (
                    env.get_distance(last_customer, customer_node) +
                    env.get_distance(customer_node, home_warehouse) -
                    env.get_distance(last_customer, home_warehouse)
                )
                
                vehicle_spec = next(v for v in env.vehicle_specs if v['vehicle_id'] == vehicle_id)
                cost_increase = insertion_distance * vehicle_spec['cost_per_km']
            
            if cost_increase < min_cost_increase:
                min_cost_increase = cost_increase
                best_vehicle = vehicle_id
        
        if best_vehicle:
            home_warehouse = env.get_vehicle_home_warehouse(best_vehicle)
            
            vehicle_loads[best_vehicle]['weight'] += order_weight
            vehicle_loads[best_vehicle]['volume'] += order_volume
            vehicle_loads[best_vehicle]['orders'].append(order_id)
            
            if best_vehicle not in solution_routes:
                solution_routes[best_vehicle] = [home_warehouse, customer_node, home_warehouse]
            else:
                current_route = solution_routes[best_vehicle]
                current_route.insert(-1, customer_node)
            
            assigned_orders.add(order_id)
    
    print(f"Solution complete: {len(solution_routes)} vehicles used, {len(assigned_orders)} orders assigned")
    return {"routes": solution_routes}


def test_solver():
    """Test the solver locally."""
    env = LogisticsEnvironment()
    
    print("Launching dashboard...")
    
    env.launch_dashboard(solve)


if __name__ == "__main__":
    test_solver()