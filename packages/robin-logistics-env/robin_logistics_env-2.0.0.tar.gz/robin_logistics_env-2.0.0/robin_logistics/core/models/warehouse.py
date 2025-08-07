
class Warehouse:
    """Represents a depot with dynamic inventory and a vehicle fleet."""
    def __init__(self, warehouse_id, location_node):
        self.id, self.location = warehouse_id, location_node
        self.inventory = {}
        self.vehicles = []

    def pickup_items(self, sku, quantity):
        """Removes items from inventory if available. Returns True on success."""
        if self.inventory.get(sku, 0) >= quantity:
            self.inventory[sku] -= quantity
            return True
        return False

    def __repr__(self):
        return f"Warehouse({self.id} at {self.location})"