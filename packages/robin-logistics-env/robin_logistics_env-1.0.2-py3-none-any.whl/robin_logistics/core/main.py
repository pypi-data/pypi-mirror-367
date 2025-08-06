import pandas as pd
import json
import os
from src import config
from src.data_generator import generate_problem_instance
from src.environment import Environment
from src.solver import solve
from src.visualizer import visualize_solution

def main():
    """Executes the main command-line workflow."""
    print("Robin Hackathon 2025: Operations Planning")
    print("\nLoading map data...")
    nodes_df = pd.read_csv('data/nodes.csv')
    edges_df = pd.read_csv('data/edges.csv')
    print(f"Loaded {len(nodes_df)} nodes and {len(edges_df)} road segments")

    print("\nGenerating problem instance...")
    problem_data = generate_problem_instance(config, nodes_df)
    print(f"Generated {len(problem_data['orders'])} orders for {config.NUM_CUSTOMER_LOCATIONS} customers")
    print(f"Created {len(problem_data['warehouses'])} warehouses")

    print("\nInitializing environment...")
    env = Environment(
        nodes=problem_data['nodes'],
        edges_df=edges_df,
        warehouses=problem_data['warehouses'],
        orders=problem_data['orders'],
        skus=problem_data['skus']
    )
    print("Environment ready")

    print("\nRunning solver...")
    solution = solve(env)
    print(f"Solution uses {len(solution.get('routes', {}))} vehicles")

    print("\nValidating solution...")
    is_valid, message = env.validate_solution(solution)
    output_dir = "generated_data"
    os.makedirs(output_dir, exist_ok=True)
    if is_valid:
        print("Solution is valid")
        cost = env.calculate_cost(solution)
        solution['solution_cost'] = round(cost, 2)
        print(f"Total cost: ${cost:.2f}")
        solution_path = os.path.join(output_dir, "solution.json")
        with open(solution_path, 'w') as f:
            json.dump(solution, f, indent=2)
        print(f"Solution saved to {solution_path}")
    else:
        print(f"Solution is invalid: {message}")
        solution['solution_cost'] = None
        solution['validation_error'] = message
        solution_path = os.path.join(output_dir, "invalid_solution.json")
        with open(solution_path, 'w') as f:
            json.dump(solution, f, indent=2)
        print(f"Invalid solution saved to {solution_path}")

    print("\nGenerating visualization...")
    map_path = os.path.join(output_dir, "solution_map.html")
    visualize_solution(env, solution, map_path)
    print(f"Map saved to {map_path}")

if __name__ == "__main__":
    main()