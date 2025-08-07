"""Operational parameters for the multi-depot problem instance."""

SEED = 42
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
    {'sku_id': 'Light_Item', 'weight_kg': 5.0, 'volume_m3': 0.02},
    {'sku_id': 'Medium_Item', 'weight_kg': 15.0, 'volume_m3': 0.06},
    {'sku_id': 'Heavy_Item', 'weight_kg': 30.0, 'volume_m3': 0.12},
]

WAREHOUSE_INVENTORY_LEVELS = {'min': 50, 'max': 100}
NUM_ORDERS = 15
MAX_SKUS_PER_ORDER = 2
MAX_QUANTITY_PER_SKU = 4

SCENARIOS = {
    "heavy_close": {
        "name": "Heavy Items, Close Delivery",
        "description": "80% heavy items, deliveries within 50km of warehouses",
        "heavy_ratio": 0.8,
        "light_ratio": 0.2,
        "max_distance_from_warehouse": 50,
        "seed": 100
    },
    "mixed_medium": {
        "name": "Mixed Items, Medium Distance",
        "description": "50% heavy, 50% light items, deliveries within 150km",
        "heavy_ratio": 0.5,
        "light_ratio": 0.5,
        "max_distance_from_warehouse": 150,
        "seed": 200
    },
    "light_far": {
        "name": "Light Items, Far Delivery", 
        "description": "20% heavy, 80% light items, deliveries anywhere",
        "heavy_ratio": 0.2,
        "light_ratio": 0.8,
        "max_distance_from_warehouse": 300,
        "seed": 300
    }
}