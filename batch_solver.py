import os
import subprocess
import sys

def run_sat_solver_on_folder(folder_path, metoda):
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
        try:
            subprocess.run(["python", "sat_solver.py", metoda, input_path], check=True)
        except subprocess.CalledProcessError:
            print(f"Error running sat_solver.py with file: {file_name}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python batch_runner.py [dp|dpll|res] [folder]")
        sys.exit(1)

    folder = sys.argv[2].lower()
    metoda = sys.argv[1]

    if metoda not in ["dp", "dpll", "res"]:
        print("Methods needs to be one of the following: dp, dpll, res")
        sys.exit(1)

    run_sat_solver_on_folder(folder, metoda)
