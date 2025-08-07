import random
import pandas as pd
import math
from .models import Node, SKU, Warehouse, Vehicle, Order

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 6371
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_problem_instance(config, nodes_df_raw, scenario_key=None):
    """Generates a multi-depot problem instance with strict location constraints."""
    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

    if config.SEED is not None:
        random.seed(config.SEED)

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

    node_map = {row.Index: Node(row.Index, row.lat, row.lon) for row in nodes_df_indexed.itertuples()}
    
    if scenario_key and hasattr(config, 'SCENARIOS') and scenario_key in config.SCENARIOS:
        orders = _generate_scenario_orders(config, scenario_key, warehouses, skus, available_nodes, node_map)
    else:
        customer_destination_nodes = random.sample(available_nodes, config.NUM_ORDERS)
        orders = []
        for i, dest_node_id in enumerate(customer_destination_nodes):
            dest_node = node_map[dest_node_id]
            order = Order(f"ORD-{i+1}", dest_node)
            num_skus = random.randint(1, config.MAX_SKUS_PER_ORDER)
            for sku in random.sample(skus, num_skus):
                order.requested_items[sku] = random.randint(1, config.MAX_QUANTITY_PER_SKU)
            orders.append(order)

    return {
        "nodes": list(node_map.values()),
        "warehouses": warehouses,
        "orders": orders,
        "skus": skus
    }

def _generate_scenario_orders(config, scenario_key, warehouses, skus, available_nodes, node_map):
    """Generate orders based on scenario parameters."""
    scenario = config.SCENARIOS[scenario_key]
    random.seed(scenario['seed'])
    
    light_skus = [sku for sku in skus if sku.weight <= 10]
    heavy_skus = [sku for sku in skus if sku.weight > 10]
    
    if not light_skus or not heavy_skus:
        light_skus = [skus[0]]
        heavy_skus = [skus[-1]]
    
    filtered_nodes = _filter_nodes_by_distance(warehouses, available_nodes, node_map, scenario['max_distance_from_warehouse'])
    
    if len(filtered_nodes) < config.NUM_ORDERS:
        filtered_nodes = available_nodes
    
    customer_destination_nodes = random.sample(filtered_nodes, min(config.NUM_ORDERS, len(filtered_nodes)))
    
    orders = []
    for i, dest_node_id in enumerate(customer_destination_nodes):
        dest_node = node_map[dest_node_id]
        order = Order(f"ORD-{i+1}", dest_node)
        
        num_skus = random.randint(1, config.MAX_SKUS_PER_ORDER)
        for _ in range(num_skus):
            if random.random() < scenario['heavy_ratio']:
                sku = random.choice(heavy_skus)
            else:
                sku = random.choice(light_skus)
            
            if sku not in order.requested_items:
                order.requested_items[sku] = random.randint(1, config.MAX_QUANTITY_PER_SKU)
        
        orders.append(order)
    
    return orders

def _filter_nodes_by_distance(warehouses, available_nodes, node_map, max_distance):
    """Filter nodes based on distance from warehouses."""
    filtered_nodes = []
    
    for node_id in available_nodes:
        node = node_map[node_id]
        min_distance = float('inf')
        
        for warehouse in warehouses:
            distance = calculate_distance(
                warehouse.location.lat, warehouse.location.lon,
                node.lat, node.lon
            )
            min_distance = min(min_distance, distance)
        
        if min_distance <= max_distance:
            filtered_nodes.append(node_id)
    
    return filtered_nodes

def generate_custom_scenario(config, nodes_df_raw, heavy_ratio, max_distance):
    """Generate problem instance with custom heavy ratio and distance parameters."""
    import random
    
    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    
    random.seed(42)
    
    skus = [SKU(**s) for s in config.SKU_DEFINITIONS]
    all_node_ids = nodes_df['node_id'].tolist()
    nodes_df_indexed = nodes_df.set_index('node_id')
    
    used_nodes = set()
    available_nodes = all_node_ids.copy()
    
    warehouses = []
    wh_counter = 1
    for wh_def in config.WAREHOUSE_DEFS:
        num_to_generate = wh_def["num_to_generate"]
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
    
    node_map = {row.Index: Node(row.Index, row.lat, row.lon) for row in nodes_df_indexed.itertuples()}
    
    orders = _generate_custom_orders(config, warehouses, skus, available_nodes, node_map, heavy_ratio, max_distance)
    
    return {
        "nodes": list(node_map.values()),
        "warehouses": warehouses,
        "orders": orders,
        "skus": skus
    }

def _generate_custom_orders(config, warehouses, skus, available_nodes, node_map, heavy_ratio, max_distance):
    """Generate orders with custom parameters."""
    import random
    
    random.seed(200)
    
    light_skus = [sku for sku in skus if sku.weight <= 10]
    heavy_skus = [sku for sku in skus if sku.weight > 10]
    
    if not light_skus or not heavy_skus:
        light_skus = [skus[0]]
        heavy_skus = [skus[-1]]
    
    filtered_nodes = _filter_nodes_by_distance(warehouses, available_nodes, node_map, max_distance)
    
    if len(filtered_nodes) < config.NUM_ORDERS:
        filtered_nodes = available_nodes
    
    customer_destination_nodes = random.sample(filtered_nodes, min(config.NUM_ORDERS, len(filtered_nodes)))
    
    orders = []
    for i, dest_node_id in enumerate(customer_destination_nodes):
        dest_node = node_map[dest_node_id]
        order = Order(f"ORD-{i+1}", dest_node)
        
        num_skus = random.randint(1, config.MAX_SKUS_PER_ORDER)
        for _ in range(num_skus):
            if random.random() < heavy_ratio:
                sku = random.choice(heavy_skus)
            else:
                sku = random.choice(light_skus)
            
            if sku not in order.requested_items:
                order.requested_items[sku] = random.randint(1, config.MAX_QUANTITY_PER_SKU)
        
        orders.append(order)
    
    return orders

def generate_scenario_from_config(base_config, nodes_df_raw, custom_config):
    """Generate problem instance from dashboard configuration."""
    import random
    
    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    
    random.seed(42)
    
    skus = [SKU(**s) for s in base_config.SKU_DEFINITIONS]
    all_node_ids = nodes_df['node_id'].tolist()
    nodes_df_indexed = nodes_df.set_index('node_id')
    
    used_nodes = set()
    available_nodes = all_node_ids.copy()
    
    warehouses = []
    num_warehouses = custom_config.get('num_warehouses', 2)
    vehicles_per_warehouse = custom_config.get('vehicles_per_warehouse', 30)
    
    if len(available_nodes) < num_warehouses:
        raise ValueError("Not enough nodes for requested number of warehouses")
    
    selected_wh_nodes = random.sample(available_nodes, num_warehouses)
    
    for i, node_id in enumerate(selected_wh_nodes):
        wh_id = f"WH-{i+1}"
        lat, lon = nodes_df_indexed.loc[node_id]['lat'], nodes_df_indexed.loc[node_id]['lon']
        wh = Warehouse(wh_id, Node(node_id, lat, lon))
        
        for j in range(vehicles_per_warehouse):
            v_id = f"LightVan_{i+1}_{j+1}"
            wh.vehicles.append(Vehicle(v_id, "LightVan", wh.id, 
                                     capacity_weight_kg=800, capacity_volume_m3=6.0,
                                     max_distance_km=300, cost_per_km=0.5, fixed_cost=50))
        
        warehouses.append(wh)
        used_nodes.add(node_id)
        available_nodes.remove(node_id)
    
    min_inventory = custom_config.get('min_inventory', 50)
    max_inventory = custom_config.get('max_inventory', 100)
    inventory_split_equal = custom_config.get('inventory_split_equal', True)
    
    for wh_idx, wh in enumerate(warehouses):
        for sku in skus:
            base_amount = random.randint(min_inventory, max_inventory)
            
            if inventory_split_equal:
                wh.inventory[sku] = base_amount
            else:
                ratio_key = f'wh_ratio_{wh_idx}'
                ratio = custom_config.get(ratio_key, 1.0 / len(warehouses))
                wh.inventory[sku] = int(base_amount * ratio * len(warehouses))
    
    node_map = {row.Index: Node(row.Index, row.lat, row.lon) for row in nodes_df_indexed.itertuples()}
    
    orders = _generate_config_orders(custom_config, warehouses, skus, available_nodes, node_map)
    
    return {
        "nodes": list(node_map.values()),
        "warehouses": warehouses,
        "orders": orders,
        "skus": skus
    }

def _generate_config_orders(config, warehouses, skus, available_nodes, node_map):
    """Generate orders based on dashboard configuration."""
    import random
    
    random.seed(300)
    
    light_skus = [sku for sku in skus if sku.weight <= 10]
    heavy_skus = [sku for sku in skus if sku.weight > 10]
    
    if not light_skus or not heavy_skus:
        light_skus = [skus[0]]
        heavy_skus = [skus[-1]]
    
    max_distance = config.get('max_distance', 150)
    filtered_nodes = _filter_nodes_by_distance(warehouses, available_nodes, node_map, max_distance)
    
    num_orders = config.get('num_orders', 15)
    if len(filtered_nodes) < num_orders:
        filtered_nodes = available_nodes
    
    customer_destination_nodes = random.sample(filtered_nodes, min(num_orders, len(filtered_nodes)))
    
    orders = []
    heavy_ratio = config.get('heavy_ratio', 0.5)
    max_skus_per_order = config.get('max_skus_per_order', 2)
    max_quantity_per_sku = config.get('max_quantity_per_sku', 4)
    
    for i, dest_node_id in enumerate(customer_destination_nodes):
        dest_node = node_map[dest_node_id]
        order = Order(f"ORD-{i+1}", dest_node)
        
        num_skus = random.randint(1, max_skus_per_order)
        for _ in range(num_skus):
            if random.random() < heavy_ratio:
                sku = random.choice(heavy_skus)
            else:
                sku = random.choice(light_skus)
            
            if sku not in order.requested_items:
                order.requested_items[sku] = random.randint(1, max_quantity_per_sku)
        
        orders.append(order)
    
    return orders