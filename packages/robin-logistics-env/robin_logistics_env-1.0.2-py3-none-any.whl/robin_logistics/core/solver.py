"""This is the only file participants should modify."""
def solve(env):
    """
    Produces a delivery plan for the given multi-depot environment.
    This improved baseline allows multiple orders per vehicle.
    """
    solution_routes = {}
    assigned_orders = set()
    available_vehicles = env.get_all_vehicles().copy()

    vehicle_loads = {v.id: {'weight': 0, 'volume': 0, 'orders': []} for v in available_vehicles}

    for order in env.orders.values():
        if order.id in assigned_orders:
            continue

        order_weight = sum(sku.weight * qty for sku, qty in order.requested_items.items())
        order_volume = sum(sku.volume * qty for sku, qty in order.requested_items.items())

        best_vehicle = None
        min_cost_increase = float('inf')

        for vehicle in available_vehicles:
            home_wh = env.warehouses[vehicle.home_warehouse_id]
            
            can_fulfill_from_home = all(
                home_wh.inventory.get(sku, 0) >= qty 
                for sku, qty in order.requested_items.items()
            )
            
            if not can_fulfill_from_home:
                continue

            current_load = vehicle_loads[vehicle.id]
            new_weight = current_load['weight'] + order_weight
            new_volume = current_load['volume'] + order_volume

            if new_weight > vehicle.capacity_weight or new_volume > vehicle.capacity_volume:
                continue

            if vehicle.id not in solution_routes:
                distance = 2 * env.get_distance(home_wh.location.id, order.destination.id)
                cost_increase = vehicle.fixed_cost + distance * vehicle.cost_per_km
            else:
                current_route = solution_routes[vehicle.id]
                last_customer = current_route[-2]
                insertion_distance = (
                    env.get_distance(last_customer, order.destination.id) +
                    env.get_distance(order.destination.id, home_wh.location.id) -
                    env.get_distance(last_customer, home_wh.location.id)
                )
                cost_increase = insertion_distance * vehicle.cost_per_km

            if cost_increase < min_cost_increase:
                min_cost_increase = cost_increase
                best_vehicle = vehicle

        if best_vehicle:
            home_wh = env.warehouses[best_vehicle.home_warehouse_id]
            
            vehicle_loads[best_vehicle.id]['weight'] += order_weight
            vehicle_loads[best_vehicle.id]['volume'] += order_volume
            vehicle_loads[best_vehicle.id]['orders'].append(order.id)

            if best_vehicle.id not in solution_routes:
                route = [home_wh.location.id, order.destination.id, home_wh.location.id]
                solution_routes[best_vehicle.id] = route
            else:
                current_route = solution_routes[best_vehicle.id]
                current_route.insert(-1, order.destination.id)

            assigned_orders.add(order.id)

    return {"routes": solution_routes}