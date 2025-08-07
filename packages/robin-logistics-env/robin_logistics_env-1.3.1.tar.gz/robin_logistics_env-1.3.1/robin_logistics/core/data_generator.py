import random
import pandas as pd
import math
from .models import Node, SKU, Warehouse, Vehicle, Order

def generate_problem_instance(config, nodes_df_raw, scenario_key="intermediate"):
    """Generates a multi-depot problem instance based on selected scenario."""
    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    
    scenario = config.SCENARIOS[scenario_key]
    random.seed(scenario['seed'])

    skus = [SKU(**s) for s in config.SKU_DEFINITIONS]
    all_node_ids = nodes_df['node_id'].tolist()
    nodes_df_indexed = nodes_df.set_index('node_id')

    used_nodes = set()
    available_nodes = all_node_ids.copy()

    warehouses = []
    wh_counter = 1
    for wh_def in config.WAREHOUSE_DEFS:
        num_to_generate = wh_def["num_to_generate"]
        if len(available_nodes) < num_to_generate:
            raise ValueError("Not enough available nodes to create all warehouses.")

        selected_wh_nodes = random.sample(available_nodes, num_to_generate)

        for node_id in selected_wh_nodes:
            wh_id = f"WH-{wh_counter}"
            lat, lon = nodes_df_indexed.loc[node_id]['lat'], nodes_df_indexed.loc[node_id]['lon']
            wh = Warehouse(wh_id, Node(node_id, lat, lon))

            for v_config in wh_def["vehicle_fleet"]:
                for i in range(v_config['count']):
                    v_id = f"{v_config['vehicle_type']}_{wh_counter}_{i+1}"
                    wh.vehicles.append(Vehicle(v_id, v_config['vehicle_type'], wh.id, **v_config))

            warehouses.append(wh)
            used_nodes.add(node_id)
            available_nodes.remove(node_id)
            wh_counter += 1

    for wh in warehouses:
        for sku in skus:
            min_q, max_q = config.WAREHOUSE_INVENTORY_LEVELS['min'], config.WAREHOUSE_INVENTORY_LEVELS['max']
            wh.inventory[sku] = random.randint(min_q, max_q)

    customer_nodes = _select_nodes_by_distance(
        available_nodes, warehouses, nodes_df_indexed, 
        scenario['num_orders'], scenario['distance_ratio'], config.DISTANCE_THRESHOLDS
    )

    orders = _generate_orders_by_weight_ratio(
        customer_nodes, nodes_df_indexed, scenario, skus
    )

    node_map = {row.Index: Node(row.Index, row.lat, row.lon) for row in nodes_df_indexed.itertuples()}

    return {
        "nodes": list(node_map.values()),
        "warehouses": warehouses,
        "orders": orders,
        "skus": skus,
        "scenario": scenario_key
    }

def _select_nodes_by_distance(available_nodes, warehouses, nodes_df_indexed, num_orders, distance_ratio, distance_thresholds):
    """Select customer nodes based on distance distribution."""
    warehouse_coords = [(wh.location.lat, wh.location.lon) for wh in warehouses]
    
    nodes_by_distance = {"close": [], "medium": [], "far": []}
    
    for node_id in available_nodes:
        if node_id not in nodes_df_indexed.index:
            continue
            
        node_lat = nodes_df_indexed.loc[node_id]['lat']
        node_lon = nodes_df_indexed.loc[node_id]['lon']
        
        min_distance = min(
            _haversine_distance(node_lat, node_lon, wh_lat, wh_lon)
            for wh_lat, wh_lon in warehouse_coords
        )
        
        if min_distance <= distance_thresholds["close"][1]:
            nodes_by_distance["close"].append(node_id)
        elif min_distance <= distance_thresholds["medium"][1]:
            nodes_by_distance["medium"].append(node_id)
        else:
            nodes_by_distance["far"].append(node_id)
    
    selected_nodes = []
    for distance_type, ratio in distance_ratio.items():
        count = int(num_orders * ratio)
        available = nodes_by_distance[distance_type]
        if len(available) >= count:
            selected_nodes.extend(random.sample(available, count))
        else:
            selected_nodes.extend(available)
    
    remaining_needed = num_orders - len(selected_nodes)
    if remaining_needed > 0:
        all_remaining = [n for n in available_nodes if n not in selected_nodes]
        if len(all_remaining) >= remaining_needed:
            selected_nodes.extend(random.sample(all_remaining, remaining_needed))
    
    return selected_nodes[:num_orders]

def _generate_orders_by_weight_ratio(customer_nodes, nodes_df_indexed, scenario, skus):
    """Generate orders with specified weight distribution."""
    orders = []
    sku_a, sku_b = skus[0], skus[1]
    
    weight_ratio = scenario['weight_ratio']
    num_orders = len(customer_nodes)
    num_sku_a_orders = int(num_orders * weight_ratio['SKU_A'])
    
    sku_assignment = ['SKU_A'] * num_sku_a_orders + ['SKU_B'] * (num_orders - num_sku_a_orders)
    random.shuffle(sku_assignment)
    
    for i, node_id in enumerate(customer_nodes):
        if node_id not in nodes_df_indexed.index:
            continue
            
        lat, lon = nodes_df_indexed.loc[node_id]['lat'], nodes_df_indexed.loc[node_id]['lon']
        dest_node = Node(node_id, lat, lon)
        order = Order(f"ORD-{i+1}", dest_node)
        
        primary_sku = sku_a if sku_assignment[i] == 'SKU_A' else sku_b
        order.requested_items[primary_sku] = random.randint(1, scenario['max_quantity_per_sku'])
        
        if random.random() < 0.4 and scenario['max_skus_per_order'] > 1:
            secondary_sku = sku_b if primary_sku == sku_a else sku_a
            order.requested_items[secondary_sku] = random.randint(1, min(2, scenario['max_quantity_per_sku']))
        
        orders.append(order)
    
    return orders

def _haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    R = 6371
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c