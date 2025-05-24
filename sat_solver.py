import sys
import time
import resource
import psutil

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

def get_memory_usage_mb():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)
    
def print_progress():
    elapsed = time.time() - start_time
    mem_mb = get_memory_usage_mb()
    print(f"[Progress] Ops: {ops:,} | Elapsed: {elapsed:.2f} sec | Mem: {mem_mb:.2f} MB")


def read_input(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    variables = []
    clauses = []

    for line in lines:
        if line.startswith('c') or line.startswith('%') or line == '0' or line == '':
            continue
        if line.startswith('p'):
            _, _, var_count, _ = line.split()
            variables = list(range(1, int(var_count) + 1))
        else:
            tokens = line.split()
            # skip if line doesn't contain valid literals
            if all(token in {'0', '%'} for token in tokens):
                continue
            clause = list(map(int, tokens))
            if clause and clause[-1] == 0:
                clause = clause[:-1]
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

        resolvents = set()
        for pc in pos_clauses:
            for nc in neg_clauses:
                check_time()
                res = set(pc + nc) - {var, -var}
                # Skip tautologies (e.g. [x, -x, y])
                if any(-lit in res for lit in res):
                    continue
                if not res:
                    return None
                resolvents.add(tuple(sorted(res)))

        return other_clauses + [list(r) for r in resolvents]

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
            unit_clauses = [c for c in clauses if len(c) == 1]
            for clause in unit_clauses:
                lit = clause[0]
                val = lit > 0
                var = abs(lit)
                if var in assignment:
                    if assignment[var] != val:
                        return None
                else:
                    assignment[var] = val
                    clauses = simplify(clauses, var, val)
                    if clauses is None:
                        return None
                    changed = True
        return clauses

    def pure_literal_assign(clauses, assignment):
        literal_count = {}
        for clause in clauses:
            for lit in clause:
                literal_count[lit] = literal_count.get(lit, 0) + 1

        for lit in list(literal_count):
            if -lit not in literal_count and abs(lit) not in assignment:
                val = lit > 0
                assignment[abs(lit)] = val
                clauses = simplify(clauses, abs(lit), val)
                if clauses is None:
                    return None
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

    clauses = deepcopy(clauses)
    assignment = assignment.copy()

    clauses = unit_propagate(clauses, assignment)
    if clauses is None:
        return False
    clauses = pure_literal_assign(clauses, assignment)
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
                new_clause = set(clause1 + clause2)
                new_clause.discard(literal)
                new_clause.discard(-literal)
                if any(-lit in new_clause for lit in new_clause):
                    return None  # Tautology
                return sorted(new_clause)
        return None

    clause_set = {tuple(sorted(c)) for c in clauses}
    seen_clauses = set(clause_set)
    clause_list = list(clause_set)
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        check_time()

        if len(clause_set) > max_clauses:
            print(f"Clause limit reached ({max_clauses})")
            return None

        new_clauses = set()
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                c1, c2 = clause_list[i], clause_list[j]
                check_time()
                resolvent = resolve(list(c1), list(c2))
                if resolvent is not None:
                    if not resolvent:
                        return False
                    resolvent_tuple = tuple(resolvent)
                    if resolvent_tuple not in seen_clauses:
                        new_clauses.add(resolvent_tuple)
                        seen_clauses.add(resolvent_tuple)

        if not new_clauses:
            return True

        clause_list.extend(new_clauses)
        clause_set.update(new_clauses)

        if iteration % 100 == 0:
            print(f"Iteration {iteration}: {len(clause_set)} clauses")

    print(f"Max iterations reached ({max_iterations})")
    return None


def write_benchmark_to_csv(input_filename, method, ops, wall_time, cpu_time, memory_usage_mb, result):
    import os
    import csv

    os.makedirs("benchmarks", exist_ok=True)
    csv_filename = "benchmarks.csv"

    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": input_filename,
        "method": method,
        "operations": ops,
        "wall_time_sec": f"{wall_time:.4f}",
        "cpu_time_sec": f"{cpu_time:.4f}",
        "memory_usage_mb": f"{memory_usage_mb:.2f}",
        "result": str(result)
    }

    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

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

    wall_time = time.time() - start_time
    cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime - start_cpu.ru_utime
    memory_usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    memory_usage_mb = memory_usage_kb / 1024  # Convert to MB (platform dependent)

    print(f"\n[Benchmark]")
    print(f"Total operations: {ops:,}")
    print(f"Wall time: {wall_time:.4f} seconds")
    print(f"CPU time: {cpu_time:.4f} seconds")
    print(f"Memory usage: {memory_usage_mb:.2f} MB")

    write_benchmark_to_csv(input_file, method, ops, wall_time, cpu_time, memory_usage_mb, result)
