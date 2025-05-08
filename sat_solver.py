import sys
import time
import resource
from copy import deepcopy
from itertools import combinations

TIME_LIMIT = 10  # seconds
PRINT_INTERVAL = 1000000  # Print progress every million ops

ops = 0
last_print = 0
start_time = time.time()
start_cpu = resource.getrusage(resource.RUSAGE_SELF)

def check_time():
    global ops, last_print
    ops += 1
    if ops - last_print >= PRINT_INTERVAL:
        print_progress()
        last_print = ops
    if time.time() - start_time > TIME_LIMIT:
        raise TimeoutError(f"Time limit of {TIME_LIMIT} seconds exceeded at {ops:,} operations.")

def print_progress():
    elapsed = time.time() - start_time
    print(f"[Progress] Ops: {ops:,} | Elapsed: {elapsed:.2f} sec")

def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    variables = []
    clauses = []
    for line in lines:
        if line.startswith('c') or line == '':
            continue
        if line.startswith('p'):
            _, _, var_count, _ = line.split()
            variables = list(range(1, int(var_count) + 1))
        else:
            clause = list(map(int, line.split()))
            clause = clause[:-1] if clause[-1] == 0 else clause
            clauses.append(clause)
    return variables, clauses

def eval_clause(clause, assignment):
    return any((lit > 0 and assignment.get(abs(lit), False)) or
               (lit < 0 and not assignment.get(abs(lit), False)) for lit in clause)

def davis_putnam(clauses, variables):
    def eliminate(clauses, var):
        pos_clauses = [c for c in clauses if var in c]
        neg_clauses = [c for c in clauses if -var in c]
        other_clauses = [c for c in clauses if var not in c and -var not in c]

        resolvents = []
        for pc in pos_clauses:
            for nc in neg_clauses:
                check_time()
                res = list(set(pc + nc) - {var, -var})
                if not res:
                    return None
                resolvents.append(res)

        return other_clauses + resolvents

    for var in variables:
        clauses = eliminate(clauses, var)
        if clauses is None:
            return False
        if not clauses:
            return True
    return True

def dpll(clauses, assignment={}):
    def unit_propagate(clauses, assignment):
        changed = True
        while changed:
            check_time()
            changed = False
            for clause in clauses:
                if len(clause) == 1:
                    lit = clause[0]
                    val = lit > 0
                    var = abs(lit)
                    if var in assignment and assignment[var] != val:
                        return None
                    if var not in assignment:
                        assignment[var] = val
                        clauses = simplify(clauses, var, val)
                        if clauses is None:
                            return None
                        changed = True
        return clauses

    def simplify(clauses, var, val):
        new_clauses = []
        for clause in clauses:
            check_time()
            if (val and var in clause) or (not val and -var in clause):
                continue
            new_clause = [lit for lit in clause if lit != -var and lit != var]
            if not new_clause:
                return None
            new_clauses.append(new_clause)
        return new_clauses

    clauses = unit_propagate(deepcopy(clauses), assignment)
    if clauses is None:
        return False
    if not clauses:
        return True

    vars_left = {abs(lit) for clause in clauses for lit in clause} - assignment.keys()
    if not vars_left:
        return all(eval_clause(clause, assignment) for clause in clauses)

    var = next(iter(vars_left))
    for val in [True, False]:
        check_time()
        new_assignment = assignment.copy()
        new_assignment[var] = val
        new_clauses = simplify(deepcopy(clauses), var, val)
        if new_clauses is not None and dpll(new_clauses, new_assignment):
            return True
    return False

def resolution(clauses, max_iterations=1000, max_clauses=1_000_000):
    
    def resolve(clause1, clause2):
        for literal in clause1:
            if -literal in clause2:
                # Create new clause by combining and removing complementary literals
                new_clause = set(clause1 + clause2)
                new_clause.discard(literal)
                new_clause.discard(-literal)
                return sorted(new_clause)  # Return sorted for consistency
        return None

    
    clause_set = {tuple(sorted(c)) for c in clauses}
    seen_clauses = set(clause_set)  # Track all clauses ever generated
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        check_time() 
        
        if len(clause_set) > max_clauses:
            print(f"Clause limit reached ({max_clauses})")
            return None
            
        new_clauses = set()
        pairs = combinations(clause_set, 2)
        
        for c1, c2 in pairs:
            check_time()  # Check during resolution steps
            resolvent = resolve(list(c1), list(c2))
            
            if resolvent is not None:
                if not resolvent:  # Empty clause found
                    return False
                    
                resolvent_tuple = tuple(resolvent)
                if resolvent_tuple not in seen_clauses:
                    new_clauses.add(resolvent_tuple)
                    seen_clauses.add(resolvent_tuple)
        
        # No new clauses - satisfiable
        if not new_clauses:
            return True
            
        clause_set.update(new_clauses)
        
        # Optional progress reporting
        if iteration % 100 == 0:
            print(f"Iteration {iteration}: {len(clause_set)} clauses")
    
    print(f"Max iterations reached ({max_iterations})")
    return None

def write_benchmark_to_csv(input_filename, method, ops, wall_time, cpu_time, cpu_usage, result):
    import os
    import csv
    
    # Create benchmarks directory if it doesn't exist
    os.makedirs("benchmarks", exist_ok=True)
    
    # Get the base filename without path or extension
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    csv_filename = f"benchmarks/{base_name}_benchmark.csv"
    
    # Prepare the data row
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": input_filename,
        "method": method,
        "operations": ops,
        "wall_time_sec": f"{wall_time:.4f}",
        "cpu_time_sec": f"{cpu_time:.4f}",
        "cpu_usage_percent": f"{cpu_usage:.1f}" if cpu_usage is not None else "N/A",
        "result": str(result)
    }
    
    # Write to CSV (create file with headers if it doesn't exist)
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Then modify your main block to use this function:
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sat_solver.py [dp|dpll|res] <input_file>")
        sys.exit(1)

    method = sys.argv[1].lower()
    input_file = sys.argv[2]
    result = None

    try:
        variables, clauses = read_input(input_file)
        if method == "dp":
            result = davis_putnam(deepcopy(clauses), variables)
            print("SAT with Davis–Putnam:", result)
        elif method == "dpll":
            result = dpll(deepcopy(clauses))
            print("SAT with DPLL:", result)
        elif method == "res":
            result = resolution(deepcopy(clauses))
            print("SAT with Resolution:", result)
        else:
            print("Invalid method. Choose from: dp, dpll, res")
            sys.exit(1)
    except TimeoutError as e:
        print(f"[TIMEOUT] {e}")
        result = "Timeout"
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        result = "Error"

    # Benchmark report
    MIN_TIME_FOR_ACCURATE_MEASUREMENT = 0.01  # 10 milliseconds
    wall_time = time.time() - start_time
    cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime - start_cpu.ru_utime
    cpu_usage = min((cpu_time / wall_time) * 100, 100) if wall_time >= MIN_TIME_FOR_ACCURATE_MEASUREMENT else None
    
    # Print to console
    print(f"\n[Benchmark]")
    print(f"Total operations: {ops:,}")
    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"CPU time: {cpu_time:.4f} seconds")
    if cpu_usage is not None:
        print(f"CPU usage: {cpu_usage:.1f}%")
    else:
        print("CPU usage: [Not shown for very short runs]")
    
    # Write to CSV
    write_benchmark_to_csv(input_file, method, ops, wall_time, cpu_time, cpu_usage, result)