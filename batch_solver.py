import os
import subprocess
import sys

def run_sat_solver_on_folder(folder_path, methods):
    if not os.path.isdir(folder_path):
        print(f"Folder '{folder_path}' doesn't exist.")
        return

    input_files = [f for f in os.listdir(folder_path) if f.endswith(".cnf")]

    if not input_files:
        print(f"No .cnf files found in folder '{folder_path}'.")
        return

    for file_name in input_files:
        input_path = os.path.join(folder_path, file_name)
        print(f"\n--- Running on file: {file_name} ---")
        for method in methods:
            print(f"\n=== Running method: {method} ===")
            try:
                subprocess.run(["python", "sat_solver.py", method, input_path], check=True)
            except subprocess.CalledProcessError:
                print(f"Error running sat_solver.py with method {method} on file: {file_name}")

if __name__ == '__main__':
    if len(sys.argv) > 3:
        print("Usage: python batch_runner.py [methods] [folder]")
        print("Methods: dp, dpll, res (default: run all)")
        print("Folder defaults to 'inputs/' if not specified")
        sys.exit(1)

    # Set default values
    all_methods = ["dp", "dpll", "res"]
    folder = 'inputs'

    # Parse arguments
    if len(sys.argv) == 1:  # No arguments provided
        methods = all_methods
    elif len(sys.argv) == 2:  # One argument provided
        if sys.argv[1] in all_methods:
            methods = [sys.argv[1]]
        else:
            methods = all_methods
            folder = sys.argv[1]  # Assume the argument is folder name
    else:  # Two arguments provided
        methods = [sys.argv[1]] if sys.argv[1] in all_methods else all_methods
        folder = sys.argv[2]

    run_sat_solver_on_folder(folder, methods)