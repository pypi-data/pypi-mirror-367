from math import radians, sin, cos, sqrt, atan2

def calculate_linestring_distance(linestring):
    """Calculates the total distance of a WKT LINESTRING in kilometers."""
    try:
        points_str = linestring.replace('LINESTRING (', '').replace(')', '')
        points = [tuple(map(float, p.split())) for p in points_str.split(', ')]
        total_dist = 0.0
        R = 6371.0
        for i in range(len(points) - 1):
            lon1, lat1 = points[i]; lon2, lat2 = points[i+1]
            lat1_rad, lon1_rad = radians(lat1), radians(lon1)
            lat2_rad, lon2_rad = radians(lat2), radians(lon2)
            dlon, dlat = lon2_rad - lon1_rad, lat2_rad - lat1_rad
            a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            total_dist += R * c
        return total_dist
    except (ValueError, IndexError):
        return 0.0