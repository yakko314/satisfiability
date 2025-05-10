# Satisfiability
Project that encompasses several tools relating to Satisfiability solving (AKA, the SAT problem), made as a college assignment. 

# Tools
- `sat_solver.py` - solves SAT problems written in the DIMACS standard formula in a text file, exporting the benchmarking results in a a shared `.csv` file;
- `generate_input.py` - generates `.cnf` files holding a single instance of a DIMACS formula, according to various parameters given;
- `batch_solver.py` - applies `sat_solver.py` to all `.cnf` files in a folder;
