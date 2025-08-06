import networkx as nx
from .util.helpers import calculate_linestring_distance
from .models import Node, SKU, Order, Vehicle, Warehouse

class Environment:
    """The main simulation environment for the multi-depot problem."""
    def __init__(self, nodes, edges_df, warehouses, orders, skus):
        self.nodes = {n.id: n for n in nodes}
        self.warehouses = {w.id: w for w in warehouses}
        self.orders = {o.id: o for o in orders}
        self.skus = {s.id: s for s in skus}
        self._graph = nx.DiGraph()
        self._path_cache = {}
        self._build_road_network(edges_df)

    def _build_road_network(self, edges_df_raw):
        """Initialize the road network graph from edge data."""
        edges_df = edges_df_raw.copy()
        edges_df.rename(columns={'from_node': 'start_node', 'to_node': 'end_node'}, inplace=True)

        edges_df['distance_km'] = edges_df['geometry'].apply(calculate_linestring_distance)
        for node_id in self.nodes:
            self._graph.add_node(node_id)
        for _, edge in edges_df.iterrows():
            if edge['distance_km'] > 0:
                self._graph.add_edge(edge['start_node'], edge['end_node'], weight=edge['distance_km'])

    def get_path_and_distance(self, node1_id, node2_id):
        """Calculate the shortest path and distance on demand, using a cache."""
        if (node1_id, node2_id) in self._path_cache:
            return self._path_cache[(node1_id, node2_id)]
        try:
            distance = nx.dijkstra_path_length(self._graph, source=node1_id, target=node2_id)
            path = nx.dijkstra_path(self._graph, source=node1_id, target=node2_id)
            result = (path, distance)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            result = ([], float('inf'))
        self._path_cache[(node1_id, node2_id)] = result
        return result

    def get_distance(self, node1_id, node2_id):
        """Returns only the shortest path distance."""
        _, distance = self.get_path_and_distance(node1_id, node2_id)
        return distance

    def get_path(self, node1_id, node2_id):
        """Returns only the shortest path as a sequence of nodes."""
        path, _ = self.get_path_and_distance(node1_id, node2_id)
        return path

    def get_all_vehicles(self):
        """Returns a flat list of all vehicles from all warehouses."""
        return [v for wh in self.warehouses.values() for v in wh.vehicles]

    def validate_solution(self, solution):
        """Validates a solution dictionary against all multi-depot constraints."""
        if not isinstance(solution, dict) or "routes" not in solution:
            return False, "Solution must be a dictionary with a 'routes' key."

        all_vehicles_by_id = {v.id: v for v in self.get_all_vehicles()}
        all_delivered_orders = set()

        for vehicle_id, route in solution.get("routes", {}).items():
            if vehicle_id not in all_vehicles_by_id:
                return False, f"Vehicle '{vehicle_id}' does not exist."

            vehicle = all_vehicles_by_id[vehicle_id]
            home_warehouse = self.warehouses[vehicle.home_warehouse_id]

            if not route or route[0] != home_warehouse.location.id or route[-1] != home_warehouse.location.id:
                return False, f"Route for {vehicle_id} must start and end at its home warehouse {home_warehouse.id}."

            orders_on_route = [o for o in self.orders.values() if o.destination.id in route]
            all_delivered_orders.update([o.id for o in orders_on_route])

            total_weight = sum(sku.weight * qty for o in orders_on_route for sku, qty in o.requested_items.items())
            total_volume = sum(sku.volume * qty for o in orders_on_route for sku, qty in o.requested_items.items())

            if total_weight > vehicle.capacity_weight or total_volume > vehicle.capacity_volume:
                return False, f"Route for {vehicle_id} exceeds capacity."

            route_dist = sum(self.get_distance(route[i], route[i+1]) for i in range(len(route) - 1))
            if route_dist > vehicle.max_distance:
                return False, f"Route for {vehicle_id} exceeds max distance."

        if len(all_delivered_orders) != len(self.orders):
            return False, f"Not all orders delivered. Required: {len(self.orders)}, Delivered: {len(all_delivered_orders)}."

        return True, "Solution is valid."

    def calculate_cost(self, solution):
        """Calculates the total operational cost of a valid solution."""
        total_cost = 0.0
        all_vehicles_by_id = {v.id: v for v in self.get_all_vehicles()}
        for vehicle_id, route in solution.get("routes", {}).items():
            vehicle = all_vehicles_by_id[vehicle_id]
            total_cost += vehicle.fixed_cost
            total_cost += sum(self.get_distance(route[i], route[i+1]) for i in range(len(route)-1)) * vehicle.cost_per_km
        return total_cost

    def get_route_distance(self, route):
        """Calculate total distance for a route (list of node IDs)."""
        if len(route) < 2:
            return 0.0
        return sum(self.get_distance(route[i], route[i+1]) for i in range(len(route) - 1))

    def get_order_requirements(self, order):
        """Get total weight and volume requirements for an order."""
        total_weight = sum(sku.weight * qty for sku, qty in order.requested_items.items())
        total_volume = sum(sku.volume * qty for sku, qty in order.requested_items.items())
        return total_weight, total_volume

    def can_vehicle_serve_order(self, vehicle, order, current_load_weight=0, current_load_volume=0):
        """Check if a vehicle can serve an order given current load."""
        order_weight, order_volume = self.get_order_requirements(order)
        
        # Check capacity constraints
        if (current_load_weight + order_weight > vehicle.capacity_weight or 
            current_load_volume + order_volume > vehicle.capacity_volume):
            return False
        
        # Check inventory availability at home warehouse
        home_wh = self.warehouses[vehicle.home_warehouse_id]
        return all(home_wh.inventory.get(sku, 0) >= qty 
                  for sku, qty in order.requested_items.items())

    def get_insertion_cost(self, vehicle, route, order, insert_position):
        """Calculate cost increase of inserting an order at specific position in route."""
        if not route or len(route) < 2:
            return float('inf')
        
        if insert_position < 1 or insert_position >= len(route):
            return float('inf')
        
        # Cost before insertion
        prev_node = route[insert_position - 1]
        next_node = route[insert_position]
        old_cost = self.get_distance(prev_node, next_node)
        
        # Cost after insertion
        order_node = order.destination.id
        new_cost = (self.get_distance(prev_node, order_node) + 
                   self.get_distance(order_node, next_node))
        
        return (new_cost - old_cost) * vehicle.cost_per_km