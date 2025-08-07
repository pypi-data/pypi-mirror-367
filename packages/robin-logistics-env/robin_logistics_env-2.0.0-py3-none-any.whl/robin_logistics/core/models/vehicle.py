
class Vehicle:
    """Represents a single delivery vehicle with dynamic state."""
    def __init__(self, vehicle_id, v_type, home_warehouse_id, **kwargs):
        self.id, self.type, self.home_warehouse_id = vehicle_id, v_type, home_warehouse_id
        self.capacity_weight = float(kwargs['capacity_weight_kg'])
        self.capacity_volume = float(kwargs['capacity_volume_m3'])
        self.max_distance = float(kwargs['max_distance_km'])
        self.cost_per_km = float(kwargs['cost_per_km'])
        self.fixed_cost = float(kwargs['fixed_cost'])

        self.current_inventory = {}
        self.current_weight = 0.0
        self.current_volume = 0.0

    def load_item(self, sku, quantity):
        """Loads items onto the vehicle, updating its state."""
        self.current_inventory[sku] = self.current_inventory.get(sku, 0) + quantity
        self.current_weight += sku.weight * quantity
        self.current_volume += sku.volume * quantity

    def unload_order(self, order):
        """Unloads an order's items from the vehicle."""
        for sku, quantity in order.requested_items.items():
            self.current_inventory[sku] -= quantity
            self.current_weight -= sku.weight * quantity
            self.current_volume -= sku.volume * quantity

    def __repr__(self):
        return f"Vehicle({self.id} from {self.home_warehouse_id})"