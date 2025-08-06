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
    return f"""
import streamlit as st
import os
import pickle
from robin_logistics.core.simulation_engine import SimulationEngine
from robin_logistics.core.visualizer import visualize_solution


def load_env_and_solution():
    env_path = "{env_path}"
    sol_path = "{sol_path}"
    
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
        st.dataframe(wh_data, use_container_width=True)


def main():
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
    
    map_tab, details_tab, routes_tab = st.tabs(["🗺️ Map View", "📋 Problem Details", "🚛 Route Details"])
    
    with map_tab:
        st.subheader("Interactive Route Map")
        map_file = "temp_map.html"
        visualize_solution(env, solution, map_file)
        
        if os.path.exists(map_file):
            with open(map_file, 'r', encoding='utf-8') as f:
                st.components.v1.html(f.read(), height=600, scrolling=True)
    
    with details_tab:
        display_problem_details(env)
    
    with routes_tab:
        st.subheader("Route Details")
        for vehicle_id, route in solution.get("routes", {{}}).items():
            with st.expander(f"Vehicle {{vehicle_id}}"):
                st.write(f"Route: {{' → '.join(map(str, route))}}")
                if vehicle_id in logs:
                    for log_entry in logs[vehicle_id]:
                        st.write(log_entry)


if __name__ == "__main__":
    main()
"""