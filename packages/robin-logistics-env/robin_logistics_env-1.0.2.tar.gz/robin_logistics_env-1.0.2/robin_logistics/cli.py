"""
Command-line interface for the Robin Logistics Environment.
"""

import argparse
import sys
import importlib.util
from pathlib import Path

from .environment import LogisticsEnvironment


def load_solver_from_file(solver_file: str):
    """
    Load solver function from a Python file.
    
    Args:
        solver_file: Path to Python file containing solve() function
        
    Returns:
        The solve function
    """
    spec = importlib.util.spec_from_file_location("solver_module", solver_file)
    solver_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver_module)
    
    if not hasattr(solver_module, 'solve'):
        raise AttributeError(f"Solver file {solver_file} must contain a 'solve' function")
    
    return solver_module.solve


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Robin Logistics Environment - Hackathon 2025",
        epilog="Example: robin-logistics --solver my_solver.py --dashboard"
    )
    
    parser.add_argument(
        "--solver", "-s",
        type=str,
        help="Path to Python file containing solve(env) function"
    )
    
    parser.add_argument(
        "--dashboard", "-d",
        action="store_true",
        help="Launch interactive dashboard after solving"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for solution (JSON format)"
    )
    
    parser.add_argument(
        "--validate-only",
        action="store_true", 
        help="Only validate solution without running full optimization"
    )
    
    parser.add_argument(
        "--export-problem",
        type=str,
        help="Export problem instance data to JSON file"
    )
    
    args = parser.parse_args()
    
    # Create environment
    print("🚚 Robin Logistics Environment - Hackathon 2025")
    print("Initializing problem instance...")
    
    try:
        env = LogisticsEnvironment()
        print(f"✅ Problem loaded: {env.num_warehouses} warehouses, {env.num_vehicles} vehicles, {env.num_orders} orders")
        
        # Export problem data if requested
        if args.export_problem:
            env.export_problem_data(args.export_problem)
            print(f"📄 Problem data exported to {args.export_problem}")
        
        # Load and run solver if provided
        if args.solver:
            if not Path(args.solver).exists():
                print(f"❌ Solver file not found: {args.solver}")
                sys.exit(1)
            
            print(f"🔧 Loading solver from {args.solver}")
            solve_function = load_solver_from_file(args.solver)
            
            print("🚀 Running optimization...")
            results = env.run_optimization(solve_function)
            
            # Display results
            print("\\n📊 Results:")
            print(f"   Valid solution: {'✅ Yes' if results['is_valid'] else '❌ No'}")
            
            if results['is_valid']:
                print(f"   Total cost: ${results['cost']:.2f}")
                print(f"   Vehicles used: {results['vehicles_used']}")
                print(f"   Orders fulfilled: {results['orders_fulfilled']}")
            else:
                print(f"   Error: {results['error_message']}")
            
            # Save solution if requested
            if args.output:
                env.save_solution(results['solution'], args.output)
                print(f"💾 Solution saved to {args.output}")
            
            # Launch dashboard if requested
            if args.dashboard:
                print("🌐 Launching dashboard...")
                env.launch_dashboard()
        
        elif args.dashboard:
            print("🌐 Launching dashboard with example solver...")
            env.launch_dashboard(create_example_solver())
        
        else:
            print("\\n🎯 Next steps:")
            print("   1. Create a solver function in a Python file")
            print("   2. Run: robin-logistics --solver your_solver.py --dashboard")
            print("   3. View results in the interactive dashboard")
            print("\\n📚 Documentation: help(LogisticsEnvironment)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def create_example_solver():
    """Create a simple example solver for demonstration."""
    def example_solver(env):
        """Simple greedy solver for demonstration."""
        solution_routes = {}
        assigned_orders = set()
        
        for vehicle_id in env.get_available_vehicles():
            if len(assigned_orders) >= env.num_orders:
                break
                
            home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
            route = [home_warehouse]
            
            # Find closest unassigned order
            for order_spec in env.order_requirements:
                order_id = order_spec['order_id']
                if order_id in assigned_orders:
                    continue
                    
                if env.can_vehicle_serve_orders(vehicle_id, [order_id]):
                    route.append(order_spec['destination_node'])
                    assigned_orders.add(order_id)
                    break
            
            route.append(home_warehouse)
            
            if len(route) > 2:  # Has actual deliveries
                solution_routes[vehicle_id] = route
        
        return {"routes": solution_routes}
    
    return example_solver


if __name__ == "__main__":
    main()