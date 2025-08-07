"""Dashboard interface for the Robin Logistics Environment."""

import os
import tempfile
import subprocess
import webbrowser
from typing import Dict
import streamlit as st

from .core.simulation_engine import SimulationEngine
from .core.visualizer import visualize_solution


def create_dashboard(env, solver_function=None):
    """Create and launch the interactive dashboard."""
    import pickle
    import tempfile
    import dill
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as env_file:
        pickle.dump(env, env_file)
        env_path = env_file.name
    
    with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as solver_file:
        dill.dump(solver_function, solver_file)
        solver_path = solver_file.name
    
    dashboard_code = _generate_dashboard_code(env_path, solver_path)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(dashboard_code)
        temp_file = f.name
    
    try:
        subprocess.run(['streamlit', 'run', temp_file], check=True)
        
    finally:
        for path in [temp_file, env_path, solver_path]:
            if os.path.exists(path):
                os.unlink(path)


def _generate_dashboard_code(env_path: str, solver_path: str) -> str:
    """Generate the Streamlit dashboard code."""
    return """
import streamlit as st
import pandas as pd
import os
import pickle
import dill
from robin_logistics.core.simulation_engine import SimulationEngine
from robin_logistics.core.visualizer import visualize_solution


def load_env_and_solver():
    env_path = "{}"
    solver_path = "{}"
    
    try:
        with open(env_path, 'rb') as f:
            env = pickle.load(f)
        with open(solver_path, 'rb') as f:
            solver_function = dill.load(f)
        return env, solver_function
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
    
    env, solver_function = load_env_and_solver()
    if not env or not solver_function:
        return
    
    # Problem Definition Section - Always at top
    st.header("📝 Problem Definition")
    st.info("Configure problem parameters below, then run simulation to test your solver")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Order Configuration")
        
        num_orders = st.number_input(
            "Number of Orders",
            min_value=5,
            max_value=50,
            value=st.session_state.get('num_orders', 15),
            help="Total number of customer orders to generate"
        )
        
        heavy_ratio_def = st.slider(
            "Heavy Items Ratio",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.get('heavy_ratio_def', 0.5),
            step=0.1,
            help="Proportion of heavy items across all orders"
        )
        
        max_skus_per_order = st.number_input(
            "Max SKUs per Order",
            min_value=1,
            max_value=5,
            value=st.session_state.get('max_skus_per_order', 2),
            help="Maximum different items in a single order"
        )
        
        max_quantity_per_sku = st.number_input(
            "Max Quantity per SKU",
            min_value=1,
            max_value=10,
            value=st.session_state.get('max_quantity_per_sku', 4),
            help="Maximum quantity of each item type"
        )
        
        delivery_distance = st.slider(
            "Max Delivery Distance (km)",
            min_value=10,
            max_value=300,
            value=st.session_state.get('delivery_distance', 150),
            step=10,
            help="Maximum distance from warehouses for deliveries"
        )
    
    with col2:
        st.subheader("Warehouse & Fleet Configuration")
        
        num_warehouses = st.number_input(
            "Number of Warehouses",
            min_value=1,
            max_value=5,
            value=st.session_state.get('num_warehouses', 2),
            help="Number of distribution centers"
        )
        
        vehicles_per_warehouse = st.number_input(
            "Vehicles per Warehouse",
            min_value=5,
            max_value=50,
            value=st.session_state.get('vehicles_per_warehouse', 30),
            help="Fleet size at each warehouse"
        )
        
        st.subheader("Inventory Distribution")
        
        inventory_split_equal = st.checkbox(
            "Equal Inventory Split",
            value=st.session_state.get('inventory_split_equal', True),
            help="Distribute inventory equally across warehouses"
        )
        
        if not inventory_split_equal:
            st.write("Warehouse Inventory Ratios:")
            for i in range(num_warehouses):
                ratio = st.slider(
                    f"Warehouse {{i+1}} Inventory %",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.get(f'wh_ratio_{{i}}', 1.0/num_warehouses),
                    step=0.1,
                    key=f"wh_ratio_{{i}}"
                )
                st.session_state[f'wh_ratio_{{i}}'] = ratio
        
        min_inventory = st.number_input(
            "Min Inventory per SKU",
            min_value=10,
            max_value=200,
            value=st.session_state.get('min_inventory', 50),
            help="Minimum stock level for each item"
        )
        
        max_inventory = st.number_input(
            "Max Inventory per SKU",
            min_value=min_inventory,
            max_value=500,
            value=st.session_state.get('max_inventory', 100),
            help="Maximum stock level for each item"
        )
    
    # Update session state
    st.session_state.update({{
        'num_orders': num_orders,
        'heavy_ratio_def': heavy_ratio_def,
        'max_skus_per_order': max_skus_per_order,
        'max_quantity_per_sku': max_quantity_per_sku,
        'delivery_distance': delivery_distance,
        'num_warehouses': num_warehouses,
        'vehicles_per_warehouse': vehicles_per_warehouse,
        'inventory_split_equal': inventory_split_equal,
        'min_inventory': min_inventory,
        'max_inventory': max_inventory
    }})
    
    # Control buttons with Run Simulation
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Generate New Problem", use_container_width=True):
            st.success("Problem configuration updated! Run simulation to test.")
            st.session_state.problem_updated = True
    
    with col2:
        if st.button("Reset to Defaults", use_container_width=True):
            for key in ['num_orders', 'heavy_ratio_def', 'max_skus_per_order', 
                       'max_quantity_per_sku', 'delivery_distance', 'num_warehouses',
                       'vehicles_per_warehouse', 'inventory_split_equal', 
                       'min_inventory', 'max_inventory']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col3:
        if st.button("Export Configuration", use_container_width=True):
            config_data = {{k: v for k, v in st.session_state.items() 
                          if k.startswith(('num_', 'heavy_', 'max_', 'delivery_', 'vehicles_', 'inventory_', 'min_'))}}
            st.download_button(
                "Download Config JSON",
                data=pd.Series(config_data).to_json(indent=2),
                file_name="problem_config.json",
                mime="application/json"
            )
    
    with col4:
        if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Running solver and simulation..."):
                import time
                start_time = time.time()
                
                try:
                    from robin_logistics import LogisticsEnvironment
                    wrapper_env = LogisticsEnvironment()
                    
                    custom_config = {{
                        'heavy_ratio': st.session_state.get('heavy_ratio_def', 0.5),
                        'max_distance': st.session_state.get('delivery_distance', 150),
                        'num_orders': st.session_state.get('num_orders', 15),
                        'num_warehouses': st.session_state.get('num_warehouses', 2),
                        'vehicles_per_warehouse': st.session_state.get('vehicles_per_warehouse', 30),
                        'max_skus_per_order': st.session_state.get('max_skus_per_order', 2),
                        'max_quantity_per_sku': st.session_state.get('max_quantity_per_sku', 4),
                        'min_inventory': st.session_state.get('min_inventory', 50),
                        'max_inventory': st.session_state.get('max_inventory', 100),
                        'inventory_split_equal': st.session_state.get('inventory_split_equal', True)
                    }}
                    
                    scenario_env = wrapper_env.generate_scenario_from_config(custom_config)
                    wrapper_env._env = scenario_env
                    
                    solver_start = time.time()
                    solution = solver_function(wrapper_env)
                    solver_time = time.time() - solver_start
                    
                    if not solution or "routes" not in solution:
                        st.error("Solver returned invalid solution format")
                        return
                    
                    simulation_start = time.time()
                    sim_engine = SimulationEngine(scenario_env, solution)
                    final_state, logs = sim_engine.run_simulation()
                    simulation_time = time.time() - simulation_start
                    total_time = time.time() - start_time
                    
                    performance_metrics = {{
                        'solver_time': solver_time,
                        'simulation_time': simulation_time,
                        'total_time': total_time,
                        'num_routes': len(solution.get('routes', {{}})),
                        'num_orders': len(scenario_env.orders),
                        'num_warehouses': len(scenario_env.warehouses),
                        'num_vehicles_used': final_state.get('vehicles_used', 0),
                        'total_cost': final_state.get('total_cost', 0),
                        'orders_delivered': final_state.get('orders_delivered', 0),
                        'solution_valid': final_state.get('is_valid', False),
                        'config_used': custom_config
                    }}
                    
                    st.session_state.solution = solution
                    st.session_state.final_state = final_state
                    st.session_state.logs = logs
                    st.session_state.simulation_run = True
                    st.session_state.current_env = scenario_env
                    st.session_state.performance_metrics = performance_metrics
                    
                except Exception as e:
                    st.error(f"Error running simulation: {{e}}")
                    return
    
    if st.session_state.get('simulation_run', False):
        solution = st.session_state.solution
        final_state = st.session_state.final_state
        logs = st.session_state.logs
        current_env = st.session_state.current_env
        performance_metrics = st.session_state.performance_metrics
        
        st.header("Solution Results")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cost", f"${{final_state['total_cost']:.2f}}")
        with col2:
            st.metric("Vehicles Used", final_state['vehicles_used'])
        with col3:
            st.metric("Orders Delivered", f"{{final_state['orders_delivered']}}/{{len(current_env.orders)}}")
        with col4:
            st.metric("Solver Time", f"{{performance_metrics['solver_time']:.3f}}s")
        
        st.subheader("Performance Metrics")
        perf_col1, perf_col2, perf_col3 = st.columns(3)
        
        with perf_col1:
            st.metric("Problem Size", f"{{performance_metrics['num_orders']}} orders")
            st.metric("Warehouses", performance_metrics['num_warehouses'])
            st.metric("Routes Generated", performance_metrics['num_routes'])
            
        with perf_col2:
            st.metric("Solver Time", f"{{performance_metrics['solver_time']:.3f}}s")
            st.metric("Simulation Time", f"{{performance_metrics['simulation_time']:.3f}}s")
            st.metric("Total Time", f"{{performance_metrics['total_time']:.3f}}s")
            
        with perf_col3:
            efficiency = (performance_metrics['orders_delivered'] / performance_metrics['num_orders']) * 100
            cost_per_order = performance_metrics['total_cost'] / max(performance_metrics['orders_delivered'], 1)
            vehicles_efficiency = (performance_metrics['num_vehicles_used'] / len(current_env.get_all_vehicles())) * 100
            
            st.metric("Delivery Efficiency", f"{{efficiency:.1f}}%")
            st.metric("Cost per Order", f"${{cost_per_order:.2f}}")
            st.metric("Fleet Utilization", f"{{vehicles_efficiency:.1f}}%")
    
        if final_state['is_valid']:
            st.success("Solution is valid!")
        else:
            st.error(f"Solution is invalid: {{final_state['message']}}")
        
        # Current Problem Overview
        st.divider()
        st.header("📊 Current Problem Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Warehouses", len(current_env.warehouses))
        with col2:
            st.metric("Vehicles", len(current_env.get_all_vehicles()))
        with col3:
            st.metric("Orders", len(current_env.orders))
        with col4:
            st.metric("Network Nodes", len(current_env.nodes))
        
        # Configuration Summary
        config_used = performance_metrics['config_used']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Heavy Items Ratio", f"{{config_used['heavy_ratio']:.1f}}")
        with col2:
            st.metric("Max Distance", f"{{config_used['max_distance']}}km")
        with col3:
            st.metric("Inventory Split", "Equal" if config_used['inventory_split_equal'] else "Custom")
            
        # Results and Analysis Tabs
        st.divider()
        st.header("📋 Results & Analysis")
        
        map_tab, problem_tab, inventory_tab, vehicles_tab, analysis_tab = st.tabs([
            "Interactive Map", 
            "Problem Details", 
            "Inventory Management",
            "Vehicle Status", 
            "Journey Analysis"
        ])
        
        with map_tab:
            st.header("Route Visualization")
            
            map_path = "temp_solution_map.html"
            visualize_solution(current_env, solution, map_path)
            if os.path.exists(map_path):
                with open(map_path, 'r', encoding='utf-8') as f:
                    map_html = f.read()
                st.components.v1.html(map_html, height=800, scrolling=True)
                os.unlink(map_path)
            
            st.subheader("Order Details")
            selected_order = st.selectbox(
                "Select an order to view details:",
                options=[f"{{order.id}}" for order in current_env.orders.values()],
                help="View detailed information about each order"
            )
            
            if selected_order:
                order = next(o for o in current_env.orders.values() if o.id == selected_order)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Order ID", order.id)
                    st.metric("Destination Node", order.destination.id)
                    
                with col2:
                    st.metric("Latitude", f"{{order.destination.lat:.4f}}")
                    st.metric("Longitude", f"{{order.destination.lon:.4f}}")
                    
                with col3:
                    total_weight = sum(sku.weight * qty for sku, qty in order.requested_items.items())
                    total_volume = sum(sku.volume * qty for sku, qty in order.requested_items.items())
                    st.metric("Total Weight", f"{{total_weight:.1f}} kg")
                    st.metric("Total Volume", f"{{total_volume:.3f}} m³")
                
                st.subheader("Items in Order")
                items_data = []
                for sku, qty in order.requested_items.items():
                    items_data.append({{
                        "SKU": sku.id,
                        "Quantity": qty,
                        "Unit Weight": f"{{sku.weight}} kg",
                        "Unit Volume": f"{{sku.volume}} m³",
                        "Total Weight": f"{{sku.weight * qty}} kg",
                        "Total Volume": f"{{sku.volume * qty}} m³"
                    }})
                
                if items_data:
                    st.dataframe(pd.DataFrame(items_data), use_container_width=True)
    
        with problem_tab:
            display_problem_details(current_env)
        
        with inventory_tab:
            display_inventory_management(current_env, solution)
        
        with vehicles_tab:
            display_vehicle_status(current_env, solution, final_state, logs)
        
        with analysis_tab:
            st.header("Step-by-Step Journey Analysis")
            if not logs:
                st.info("No routes were generated to analyze.")
            else:
                vehicle_choice = st.selectbox("Select a Vehicle to Analyze:", options=list(logs.keys()))
                if vehicle_choice and vehicle_choice in logs:
                    st.subheader(f"Analysis: {{vehicle_choice}}")
                    for i, log_entry in enumerate(logs[vehicle_choice]):
                        with st.expander(f"Step {{i+1}}: {{log_entry[:50]}}...", expanded=False):
                            st.markdown(log_entry)
    else:
        # Show basic problem info when no simulation has been run
        st.header("📊 Current Problem Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Warehouses", len(env.warehouses))
        with col2:
            st.metric("Vehicles", len(env.get_all_vehicles()))
        with col3:
            st.metric("Orders", len(env.orders))
        with col4:
            st.metric("Network Nodes", len(env.nodes))
        
        st.info("Configure the problem parameters above, then click 'Run Simulation' to execute the solver and see results")
        display_problem_details(env)


if __name__ == "__main__":
    main()
""".format(env_path, solver_path)