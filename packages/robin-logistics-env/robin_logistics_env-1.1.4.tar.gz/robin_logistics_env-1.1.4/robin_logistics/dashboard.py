"""Dashboard interface for the Robin Logistics Environment."""

import os
import tempfile
import subprocess
import webbrowser
from typing import Dict
import streamlit as st

from .core.simulation_engine import SimulationEngine
from .core.visualizer import visualize_solution


def create_dashboard(env, solution: Dict):
    """Create and launch the interactive dashboard."""
    import pickle
    import tempfile
    
    # Create temporary files for data
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as env_file:
        pickle.dump(env, env_file)
        env_path = env_file.name
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as sol_file:
        pickle.dump(solution, sol_file)
        sol_path = sol_file.name
    
    # Create dashboard app
    dashboard_code = _generate_dashboard_code(env_path, sol_path)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(dashboard_code)
        temp_file = f.name
    
    try:
        # Launch Streamlit
        subprocess.run(['streamlit', 'run', temp_file], check=True)
        
    finally:
        # Clean up
        for path in [temp_file, env_path, sol_path]:
            if os.path.exists(path):
                os.unlink(path)


def _generate_dashboard_code(env_path: str, sol_path: str) -> str:
    """Generate the Streamlit dashboard code."""
    return """
import streamlit as st
import pandas as pd
import os
import pickle
from robin_logistics.core.simulation_engine import SimulationEngine
from robin_logistics.core.visualizer import visualize_solution


def load_env_and_solution():
    env_path = "{}"
    sol_path = "{}"
    
    try:
        with open(env_path, 'rb') as f:
            env = pickle.load(f)
        with open(sol_path, 'rb') as f:
            solution = pickle.load(f)
        return env, solution
    except Exception as e:
        st.error(f"Error loading data: {{e}}")
        return None, None


def display_problem_details(env):
    \"\"\"Display comprehensive problem instance details\"\"\"
    st.header("📋 Problem Instance Details")
    
    st.subheader("🏬 Warehouses & Fleet")
    wh_data = []
    for wh in env.warehouses.values():
        fleet_info = {{}}
        for vehicle in wh.vehicles:
            vtype = vehicle.type
            if vtype not in fleet_info:
                fleet_info[vtype] = 0
            fleet_info[vtype] += 1
        
        fleet_str = ", ".join([f"{{count}}x {{vtype}}" for vtype, count in fleet_info.items()])
        wh_data.append({{
            'Warehouse ID': wh.id,
            'Location Node': wh.location.id,
            'Coordinates': f"({{wh.location.lat:.4f}}, {{wh.location.lon:.4f}})",
            'Fleet Composition': fleet_str,
            'Total Vehicles': len(wh.vehicles)
        }})
    
    if wh_data:
        st.dataframe(pd.DataFrame(wh_data), use_container_width=True)
    
    st.subheader("📦 SKU Specifications")
    sku_data = []
    for sku in env.skus.values():
        sku_data.append({{
            'SKU ID': sku.id,
            'Weight (kg)': sku.weight,
            'Volume (m³)': sku.volume,
            'Density (kg/m³)': round(sku.weight / sku.volume, 2) if sku.volume > 0 else 'N/A'
        }})
    
    if sku_data:
        st.dataframe(pd.DataFrame(sku_data), use_container_width=True)
    
    st.subheader("📊 Inventory Summary")
    
    total_stock_items = sum(sum(wh.inventory.values()) for wh in env.warehouses.values())
    total_stock_weight = sum(qty * sku.weight for wh in env.warehouses.values() for sku, qty in wh.inventory.items())
    unique_skus = len(set(sku for wh in env.warehouses.values() for sku in wh.inventory.keys()))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items in Stock", f"{{total_stock_items:,}}")
    with col2:
        st.metric("Total Weight", f"{{total_stock_weight:,.1f}} kg")
    with col3:
        st.metric("Unique SKUs", unique_skus)
    
    st.subheader("🛒 Orders Summary")
    
    total_orders = len(env.orders)
    total_items_demanded = sum(sum(order.requested_items.values()) for order in env.orders.values())
    avg_items_per_order = total_items_demanded / total_orders if total_orders > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", total_orders)
    with col2:
        st.metric("Total Items Demanded", f"{{total_items_demanded:,}}")
    with col3:
        st.metric("Avg Items per Order", f"{{avg_items_per_order:.1f}}")


def display_inventory_management(env, solution):
    \"\"\"Comprehensive inventory management dashboard\"\"\"
    st.header("📦 Inventory Management Dashboard")
    
    st.subheader("📉 Inventory Usage & Deductions")
    
    required_items = {{}}
    for order in env.orders.values():
        for sku, qty in order.requested_items.items():
            if sku not in required_items:
                required_items[sku] = 0
            required_items[sku] += qty
    
    used_items = {{}}
    for vehicle_id, route in solution.get("routes", {{}}).items():
        orders_on_route = [o for o in env.orders.values() if o.destination.id in route]
        for order in orders_on_route:
            for sku, qty in order.requested_items.items():
                if sku not in used_items:
                    used_items[sku] = 0
                used_items[sku] += qty
    
    usage_data = []
    for wh in env.warehouses.values():
        for sku, initial_qty in wh.inventory.items():
            required = required_items.get(sku, 0)
            used = used_items.get(sku, 0)
            remaining = initial_qty - used
            
            usage_data.append({{
                'Warehouse': wh.id,
                'SKU': sku.id,
                'Initial Stock': initial_qty,
                'Required Total': required,
                'Used in Solution': used,
                'Remaining Stock': remaining,
                'Utilization %': f"{{(used / initial_qty * 100):.1f}}%" if initial_qty > 0 else "0.0%",
                'Status': '🟢 Sufficient' if remaining >= 0 else '🔴 Shortage'
            }})
    
    if usage_data:
        usage_df = pd.DataFrame(usage_data)
        st.dataframe(usage_df, use_container_width=True)


def display_vehicle_status(env, solution, final_state, logs):
    \"\"\"Display detailed vehicle attributes and status\"\"\"
    st.header("🚛 Vehicle Fleet Status")
    
    all_vehicles = env.get_all_vehicles()
    vehicle_data = []
    
    for vehicle in all_vehicles:
        is_used = vehicle.id in solution.get("routes", {{}})
        route = solution.get("routes", {{}}).get(vehicle.id, [])
        
        route_distance = 0
        route_cost = 0
        orders_served = 0
        orders_on_route = []
        
        if is_used and route:
            for i in range(len(route) - 1):
                route_distance += env.get_distance(route[i], route[i+1])
            
            route_cost = vehicle.fixed_cost + (route_distance * vehicle.cost_per_km)
            orders_on_route = [o for o in env.orders.values() if o.destination.id in route]
            orders_served = len(orders_on_route)
        
        weight_utilization = 0
        volume_utilization = 0
        distance_utilization = 0
        
        if is_used:
            total_weight = 0
            total_volume = 0
            
            for order in orders_on_route:
                for sku, qty in order.requested_items.items():
                    total_weight += sku.weight * qty
                    total_volume += sku.volume * qty
            
            weight_utilization = (total_weight / vehicle.capacity_weight) * 100 if vehicle.capacity_weight > 0 else 0
            volume_utilization = (total_volume / vehicle.capacity_volume) * 100 if vehicle.capacity_volume > 0 else 0
            distance_utilization = (route_distance / vehicle.max_distance) * 100 if vehicle.max_distance > 0 else 0
        
        vehicle_data.append({{
            'Vehicle ID': vehicle.id,
            'Type': vehicle.type,
            'Home Warehouse': vehicle.home_warehouse_id,
            'Status': '🟢 Active' if is_used else '⚪ Idle',
            'Capacity Weight (kg)': vehicle.capacity_weight,
            'Capacity Volume (m³)': vehicle.capacity_volume,
            'Max Distance (km)': vehicle.max_distance,
            'Fixed Cost': f"${{vehicle.fixed_cost}}",
            'Cost/km': f"${{vehicle.cost_per_km}}",
            'Route Distance (km)': f"{{route_distance:.2f}}" if is_used else "0.00",
            'Total Cost': f"${{route_cost:.2f}}" if is_used else "$0.00",
            'Orders Served': orders_served,
            'Weight Util %': f"{{weight_utilization:.1f}}%" if is_used else "0.0%",
            'Volume Util %': f"{{volume_utilization:.1f}}%" if is_used else "0.0%",
            'Distance Util %': f"{{distance_utilization:.1f}}%" if is_used else "0.0%"
        }})
    
    if vehicle_data:
        vehicles_df = pd.DataFrame(vehicle_data)
        st.dataframe(vehicles_df, use_container_width=True)


def main():
    \"\"\"Main dashboard application.\"\"\"
    st.set_page_config(page_title="Robin Logistics Dashboard", page_icon="🚚", layout="wide")
    st.title("🚚 Robin Logistics Optimization Dashboard")
    
    env, solution = load_env_and_solution()
    if not env or not solution:
        return
    
    sim_engine = SimulationEngine(env, solution)
    final_state, logs = sim_engine.run_simulation()
    
    st.header("📈 Solution Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", f"${{final_state['total_cost']:.2f}}")
    with col2:
        st.metric("Vehicles Used", final_state['vehicles_used'])
    with col3:
        st.metric("Orders Delivered", f"{{final_state['orders_delivered']}}/{{len(env.orders)}}")
    
    if final_state['is_valid']:
        st.success("✅ Solution is valid!")
    else:
        st.error(f"❌ Solution is invalid: {{final_state['message']}}")
    
    map_tab, problem_tab, inventory_tab, vehicles_tab, analysis_tab = st.tabs([
        "🗺️ Interactive Map", 
        "📋 Problem Details", 
        "📦 Inventory Management",
        "🚛 Vehicle Status", 
        "📊 Journey Analysis"
    ])
    
    with map_tab:
        st.subheader("Interactive Route Map")
        map_file = "temp_map.html"
        visualize_solution(env, solution, map_file)
        
        if os.path.exists(map_file):
            with open(map_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
    
    with problem_tab:
        display_problem_details(env)
    
    with inventory_tab:
        display_inventory_management(env, solution)
    
    with vehicles_tab:
        display_vehicle_status(env, solution, final_state, logs)
    
    with analysis_tab:
        st.header("📊 Step-by-Step Journey Analysis")
        if not logs:
            st.info("No routes were generated to analyze.")
        else:
            vehicle_choice = st.selectbox("Select a Vehicle to Analyze:", options=list(logs.keys()))
            if vehicle_choice and vehicle_choice in logs:
                st.subheader(f"🔍 Analysis: {{vehicle_choice}}")
                for i, log_entry in enumerate(logs[vehicle_choice]):
                    with st.expander(f"Step {{i+1}}: {{log_entry[:50]}}...", expanded=False):
                        st.markdown(log_entry)


if __name__ == "__main__":
    main()
""".format(env_path, sol_path)