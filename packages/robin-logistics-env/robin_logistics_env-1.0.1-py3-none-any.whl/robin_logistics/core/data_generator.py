import random
import pandas as pd
from .models import Node, SKU, Warehouse, Vehicle, Order

def generate_problem_instance(config, nodes_df_raw):
    """
    Generates a multi-depot problem instance with strict location constraints.
    Warehouses and customer locations are mutually exclusive.
    All customer delivery locations are unique.
    """
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

    if len(available_nodes) < config.NUM_ORDERS:
        raise ValueError("Not enough unique nodes for each order. Reduce NUM_ORDERS or increase the number of nodes in your map data.")

    customer_destination_nodes = random.sample(available_nodes, config.NUM_ORDERS)

    for wh in warehouses:
        for sku in skus:
            min_q, max_q = config.WAREHOUSE_INVENTORY_LEVELS['min'], config.WAREHOUSE_INVENTORY_LEVELS['max']
            wh.inventory[sku] = random.randint(min_q, max_q)

    orders = []
    node_map = {row.Index: Node(row.Index, row.lat, row.lon) for row in nodes_df_indexed.itertuples()}

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