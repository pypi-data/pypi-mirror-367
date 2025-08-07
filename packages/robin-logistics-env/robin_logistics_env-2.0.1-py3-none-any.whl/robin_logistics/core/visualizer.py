import folium
import pandas as pd
import streamlit as st

def visualize_solution(environment, solution, output_path):
    """Generates an enhanced interactive HTML map visualizing the multi-depot solution."""
    if not environment.warehouses:
        map_center = [30.0444, 31.2357]
    else:
        first_wh_loc = next(iter(environment.warehouses.values())).location
        map_center = [first_wh_loc.lat, first_wh_loc.lon]

    m = folium.Map(location=map_center, zoom_start=11, tiles="cartodbpositron")

    all_vehicles_by_id = {v.id: v for v in environment.get_all_vehicles()}

    for wh in environment.warehouses.values():
        folium.Marker(location=[wh.location.lat, wh.location.lon],
                      popup=f"<b>Warehouse: {wh.id}</b>",
                      icon=folium.Icon(color="red", icon="warehouse")).add_to(m)
    for order in environment.orders.values():
        folium.Marker(location=[order.destination.lat, order.destination.lon],
                      popup=f"<b>Order: {order.id}</b>",
                      icon=folium.Icon(color="green", icon="home")).add_to(m)

    color_pool = ["purple", "orange", "darkred", "cadetblue", "darkgreen", "gray"]
    for i, (vehicle_id, route_stops) in enumerate(solution.get("routes", {}).items()):
        if not route_stops: continue

        vehicle_group = folium.FeatureGroup(name=f"Route: {vehicle_id}", show=True)
        m.add_child(vehicle_group)
        color = color_pool[i % len(color_pool)]

        full_route_coordinates = []
        total_dist = 0

        for j in range(len(route_stops) - 1):
            path, dist = environment.get_path_and_distance(route_stops[j], route_stops[j+1])
            if not path: continue

            total_dist += dist
            path_coords = [[environment.nodes[nid].lat, environment.nodes[nid].lon] for nid in path]

            if full_route_coordinates and full_route_coordinates[-1] == path_coords[0]:
                full_route_coordinates.extend(path_coords[1:])
            else:
                full_route_coordinates.extend(path_coords)

        if full_route_coordinates:
            cost = all_vehicles_by_id[vehicle_id].fixed_cost + (total_dist * all_vehicles_by_id[vehicle_id].cost_per_km)
            popup_html = f"<b>Route: {vehicle_id}</b><br>Distance: {total_dist:.2f} km<br>Est. Cost: {cost:.2f}"
            folium.PolyLine(locations=full_route_coordinates, popup=folium.Popup(popup_html),
                            color=color, weight=3.5, opacity=0.8).add_to(vehicle_group)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save(output_path)

def display_problem_definition(environment):
    """Creates tables and summaries for the problem definition in the Streamlit app."""
    st.subheader("Warehouse & Fleet Overview")
    wh_data = [{'Warehouse ID': wh.id, 'Location Node': wh.location.id,
                'Vehicle Fleet': ", ".join([v.id for v in wh.vehicles])}
               for wh in environment.warehouses.values()]
    if wh_data:
        st.dataframe(pd.DataFrame(wh_data), use_container_width=True)

    st.subheader("SKU Inventory")
    inventory_data = [{'Warehouse': wh.id, 'SKU': sku.id, 'Quantity': qty}
                      for wh in environment.warehouses.values()
                      for sku, qty in wh.inventory.items()]
    if inventory_data:
        st.dataframe(pd.DataFrame(inventory_data), use_container_width=True)

    st.subheader("Order Manifest")
    order_data = [{'Order ID': order.id, 'Customer Location': order.destination.id,
                   'Items': ", ".join([f"{qty}x {sku.id}" for sku, qty in order.requested_items.items()])}
                  for order in environment.orders.values()]
    if order_data:
        st.dataframe(pd.DataFrame(order_data), use_container_width=True)