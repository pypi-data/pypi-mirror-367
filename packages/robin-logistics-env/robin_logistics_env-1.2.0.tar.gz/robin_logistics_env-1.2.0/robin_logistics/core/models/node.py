class Node:
    def __init__(self, node_id, lat, lon):
        self.id, self.lat, self.lon = int(node_id), float(lat), float(lon)