"""Scenario-based problem configurations for the logistics environment."""

WAREHOUSE_DEFS = [
    {
        "num_to_generate": 2,
        "vehicle_fleet": [
            {
                "vehicle_type": "LightVan", "count": 30,
                "capacity_weight_kg": 800, "capacity_volume_m3": 6.0,
                "max_distance_km": 500, "cost_per_km": 0.5, "fixed_cost": 50
            }
        ]
    }
]

SKU_DEFINITIONS = [
    {'sku_id': 'SKU_A', 'weight_kg': 10.0, 'volume_m3': 0.05},
    {'sku_id': 'SKU_B', 'weight_kg': 25.0, 'volume_m3': 0.1},
]

WAREHOUSE_INVENTORY_LEVELS = {'min': 100, 'max': 200}

SCENARIOS = {
    "beginner": {
        "name": "Urban Delivery - Easy",
        "description": "Small-scale urban delivery with mostly lightweight items and nearby customers",
        "num_orders": 8,
        "weight_ratio": {"SKU_A": 0.7, "SKU_B": 0.3},
        "distance_ratio": {"close": 0.6, "medium": 0.3, "far": 0.1},
        "max_skus_per_order": 2,
        "max_quantity_per_sku": 3,
        "seed": 12345
    },
    "intermediate": {
        "name": "City-Wide Distribution",
        "description": "Medium-scale distribution with balanced weight and mixed distances",
        "num_orders": 15,
        "weight_ratio": {"SKU_A": 0.5, "SKU_B": 0.5},
        "distance_ratio": {"close": 0.4, "medium": 0.4, "far": 0.2},
        "max_skus_per_order": 2,
        "max_quantity_per_sku": 4,
        "seed": 67890
    },
    "advanced": {
        "name": "Metropolitan Challenge",
        "description": "Large-scale delivery with heavy items and distant customers",
        "num_orders": 25,
        "weight_ratio": {"SKU_A": 0.3, "SKU_B": 0.7},
        "distance_ratio": {"close": 0.2, "medium": 0.3, "far": 0.5},
        "max_skus_per_order": 3,
        "max_quantity_per_sku": 5,
        "seed": 13579
    }
}

DISTANCE_THRESHOLDS = {
    "close": (0, 50),
    "medium": (50, 150), 
    "far": (150, float('inf'))
}