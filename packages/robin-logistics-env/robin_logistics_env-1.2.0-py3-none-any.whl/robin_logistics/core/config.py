"""Operational parameters for the multi-depot problem instance."""
SEED = None
WAREHOUSE_DEFS = [
    {
        "num_to_generate": 2,
        "vehicle_fleet": [
            {
                "vehicle_type": "LightVan", "count": 30,
                "capacity_weight_kg": 800, "capacity_volume_m3": 6.0,
                "max_distance_km": 300, "cost_per_km": 0.5, "fixed_cost": 50
            }
        ]
    }
]
SKU_DEFINITIONS = [
    {'sku_id': 'SKU_A', 'weight_kg': 10.0, 'volume_m3': 0.05},
    {'sku_id': 'SKU_B', 'weight_kg': 25.0, 'volume_m3': 0.1},
]
WAREHOUSE_INVENTORY_LEVELS = {'min': 50, 'max': 100}
NUM_CUSTOMER_LOCATIONS = 20
NUM_ORDERS = 15
MAX_SKUS_PER_ORDER = 2
MAX_QUANTITY_PER_SKU = 4