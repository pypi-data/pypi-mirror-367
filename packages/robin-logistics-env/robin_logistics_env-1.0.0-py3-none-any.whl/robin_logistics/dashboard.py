"""
Dashboard interface for the Robin Logistics Environment.
Integrates the Streamlit dashboard with the package.
"""

import os
import tempfile
import subprocess
import webbrowser
from typing import Dict
import streamlit as st

from .core.simulation_engine import SimulationEngine
from .core.visualizer import visualize_solution


def create_dashboard(env, solution: Dict):
    """
    Create and launch the interactive dashboard.
    
    Args:
        env: Internal Environment instance
        solution: Solution dictionary
    """
    # Create a temporary Streamlit app file
    dashboard_code = _generate_dashboard_code()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(dashboard_code)
        temp_file = f.name
    
    try:
        # Set environment variables for the dashboard
        os.environ['ROBIN_ENV_DATA'] = _serialize_env_data(env)
        os.environ['ROBIN_SOLUTION_DATA'] = str(solution)
        
        # Launch Streamlit
        subprocess.run(['streamlit', 'run', temp_file], check=True)
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)


def _serialize_env_data(env) -> str:
    """Serialize environment data for passing to dashboard."""
    import pickle
    import base64
    return base64.b64encode(pickle.dumps(env)).decode()


def _generate_dashboard_code() -> str:
    """Generate the Streamlit dashboard code."""
    return '''
import streamlit as st
import os
import pickle
import base64
import ast
from robin_logistics.core.simulation_engine import SimulationEngine
from robin_logistics.core.visualizer import visualize_solution


def load_env_and_solution():
    """Load environment and solution from environment variables."""
    env_data = os.environ.get('ROBIN_ENV_DATA')
    solution_data = os.environ.get('ROBIN_SOLUTION_DATA')
    
    if not env_data or not solution_data:
        st.error("No environment or solution data found")
        return None, None
        
    env = pickle.loads(base64.b64decode(env_data))
    solution = ast.literal_eval(solution_data)
    
    return env, solution


def display_problem_details(env):
    """Display comprehensive problem instance details"""
    st.header("📋 Problem Instance Details")
    
    st.subheader("🏬 Warehouses & Fleet")
    wh_data = []
    for wh in env.warehouses.values():
        fleet_info = {}
        for vehicle in wh.vehicles:
            vtype = vehicle.type
            if vtype not in fleet_info:
                fleet_info[vtype] = 0
            fleet_info[vtype] += 1
        
        fleet_str = ", ".join([f"{count}x {vtype}" for vtype, count in fleet_info.items()])
        wh_data.append({
            'Warehouse ID': wh.id,
            'Location Node': wh.location.id,
            'Coordinates': f"({wh.location.lat:.4f}, {wh.location.lon:.4f})",
            'Fleet Composition': fleet_str,
            'Total Vehicles': len(wh.vehicles)
        })
    
    if wh_data:
        st.dataframe(wh_data, use_container_width=True)


def main():
    """Main dashboard application."""
    st.set_page_config(page_title="Robin Logistics Dashboard", page_icon="🚚", layout="wide")
    st.title("🚚 Robin Logistics Optimization Dashboard")
    
    env, solution = load_env_and_solution()
    if not env or not solution:
        return
    
    # Run simulation
    sim_engine = SimulationEngine(env, solution)
    final_state, logs = sim_engine.run_simulation()
    
    # Display results
    st.header("📈 Solution Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Cost", f"${final_state['total_cost']:.2f}")
    with col2:
        st.metric("Vehicles Used", final_state['vehicles_used'])
    with col3:
        st.metric("Orders Delivered", f"{final_state['orders_delivered']}/{len(env.orders)}")
    
    if final_state['is_valid']:
        st.success("✅ Solution is valid!")
    else:
        st.error(f"❌ Solution is invalid: {final_state['message']}")
    
    # Tabs for different views
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
        for vehicle_id, route in solution.get("routes", {}).items():
            with st.expander(f"Vehicle {vehicle_id}"):
                st.write(f"Route: {' → '.join(map(str, route))}")
                if vehicle_id in logs:
                    for log_entry in logs[vehicle_id]:
                        st.write(log_entry)


if __name__ == "__main__":
    main()
'''


def launch_dashboard_standalone(env_file: str, solution_file: str):
    """
    Launch dashboard with saved environment and solution files.
    
    Args:
        env_file: Path to pickled environment file
        solution_file: Path to JSON solution file
    """
    # This would be used for standalone dashboard launching
    pass