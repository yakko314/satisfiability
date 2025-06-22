# Satisfiability
Project that encompasses several tools relating to Satisfiability solving (AKA, the SAT problem), made as a college assignment. 

# Tools
- `sat_solver.py` - solves SAT problems written in the DIMACS standard formula in a text file, exporting the benchmarking results in a a shared `.csv` file;
- `generate_input.py` - generates `.cnf` files holding a single instance of a DIMACS formula, according to various parameters given;
- `batch_solver.py` - applies `sat_solver.py` to all `.cnf` files in a folder;

# Usage

### Solver
The program is executed from the terminal by specifying the solving method and the input file as command-line arguments. The format is as follows:

```bash
python sat_solver.py [method] [input_file]
```

### Parameters:
- `[method]` can be one of:
  - `dp` – for the Davis-Putnam algorithm
  - `dpll` – for the DPLL algorithm
  - `res` – for the resolution method
- `[input_file]` is the name of the text file containing the formula in CNF format, e.g., `example.txt`

---

### Input Generation

The input generation script is used to create random CNF formulas. You need to specify the number of variables, number of clauses, and optionally a mode for clause length generation. It generates a file with a distinct name, either in a default folder named `inputs/` or a custom one specified by the user.

Command format:

```bash
python generate_input.py <num_vars> <num_clauses> [gen_mode] [folder]
```

#### Parameters:
- `<num_vars>` – the total number of variables in the CNF formula.
- `<num_clauses>` – the number of desired clauses.
- `[gen_mode]` – clause length generation mode:
  - `fixed:k` – all clauses will have fixed length `k`
  - `k` (an integer) – clause length will be randomly chosen between `k` and `num_vars`
  - if omitted, clause lengths will be randomly chosen between `1` and `num_vars`
- `[folder]` – the folder where the generated file will be saved (default: `inputs/`)

The script automatically generates a file in **DIMACS CNF format** and includes descriptive metadata in the header as comments.

---

### Batch Solving

The batch solving script can be used to solve multiple input files from a specified folder:

```bash
python batch_solver.py [method] [input_folder]
```

#### Parameters:
- `[method]` – one of the solving methods defined in `sat_solver.py`. If this parameter is omitted, all methods will be executed.
- `[input_folder]` – the name of the folder containing the input files (default: `inputs/`)

