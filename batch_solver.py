import os
import subprocess
import sys
import hashlib

def hash_file(path):
    """Compute SHA256 hash of file contents."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def run_sat_solver_on_folder(folder_path, methods):
    if not os.path.isdir(folder_path):
        print(f"Folder '{folder_path}' doesn't exist.")
        return

    input_files = [f for f in os.listdir(folder_path) if f.endswith(".cnf")]
    if not input_files:
        print(f"No .cnf files found in folder '{folder_path}'.")
        return

    seen_hashes = {}

    for file_name in sorted(input_files):
        input_path = os.path.join(folder_path, file_name)
        file_hash = hash_file(input_path)

        if file_hash in seen_hashes:
            print(f"Skipping '{file_name}' (same content as '{seen_hashes[file_hash]}')")
            continue
        else:
            seen_hashes[file_hash] = file_name

        print(f"\n--- Running on file: {file_name} ---")
        for method in methods:
            print(f"\n=== Running method: {method} ===")
            try:
                subprocess.run(["python", "sat_solver.py", method, input_path], check=True)
            except subprocess.CalledProcessError:
                print(f"Error running sat_solver.py with method {method} on file: {file_name}")

if __name__ == '__main__':
    if len(sys.argv) > 3:
        print("Usage: python batch_runner.py [method] [folder]")
        print("Methods: dp, dpll, res (default: run all)")
        print("Folder defaults to 'inputs/' if not specified")
        sys.exit(1)

    all_methods = ["dp", "dpll", "res"]
    folder = 'inputs'

    if len(sys.argv) == 1:
        methods = all_methods
    elif len(sys.argv) == 2:
        if sys.argv[1] in all_methods:
            methods = [sys.argv[1]]
        else:
            methods = all_methods
            folder = sys.argv[1]
    else:
        methods = [sys.argv[1]] if sys.argv[1] in all_methods else all_methods
        folder = sys.argv[2]

    run_sat_solver_on_folder(folder, methods)
