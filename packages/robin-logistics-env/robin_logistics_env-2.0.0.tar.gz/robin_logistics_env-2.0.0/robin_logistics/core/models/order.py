class Order:
    def __init__(self, order_id, destination_node):
        self.id, self.destination, self.requested_items = order_id, destination_node, {}
    
    def __repr__(self):
        return f"Order({self.id} to {self.destination.id})"