"""Operational parameters for the multi-depot problem instance."""
SEED = None
WAREHOUSE_DEFS = [
    {
        "num_to_generate": 2,
        "vehicle_fleet": [
            {
                "vehicle_type": "Truck", "count": 2,
                "capacity_weight_kg": 4000, "capacity_volume_m3": 12.0,
                "max_distance_km": 600, "cost_per_km": 0.5, "fixed_cost": 2000
            },
            {
                "vehicle_type": "HeavyVan", "count":40,  
                "capacity_weight_kg": 1500, "capacity_volume_m3": 6.0,
                "max_distance_km": 300, "cost_per_km": 0.3, "fixed_cost": 1000
            },
            {
                "vehicle_type": "LightVan", "count": 8,
                "capacity_weight_kg": 500, "capacity_volume_m3": 0.3,
                "max_distance_km": 100, "cost_per_km": 0.1, "fixed_cost": 500
            }
        ]
    }
]
SKU_DEFINITIONS = [
    {'sku_id': 'SKU_A', 'weight_kg': 5.0, 'volume_m3': 0.05},
    {'sku_id': 'SKU_B', 'weight_kg': 10.0, 'volume_m3': 0.1},
    {'sku_id': 'SKU_C', 'weight_kg': 15.0, 'volume_m3': 0.15},
    {'sku_id': 'SKU_D', 'weight_kg': 20.0, 'volume_m3': 0.2},
    {'sku_id': 'SKU_E', 'weight_kg': 25.0, 'volume_m3': 0.25},
    {'sku_id': 'SKU_F', 'weight_kg': 30.0, 'volume_m3': 0.3},
]

WAREHOUSE_INVENTORY_LEVELS = {'min': 100, 'max': 500}
NUM_CUSTOMER_LOCATIONS = 100
NUM_ORDERS = 100
MAX_SKUS_PER_ORDER = 3
MAX_QUANTITY_PER_SKU = 10