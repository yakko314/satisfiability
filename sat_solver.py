import sys
import time
import resource
from copy import deepcopy


TIME_LIMIT = 10  # seconds
PRINT_INTERVAL = 1_000_000  # Print progress every million ops

ops = 0
last_print = 0
start_time = time.time()

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

def resolution(clauses):
    new = set()
    clause_set = set(tuple(sorted(c)) for c in clauses)
    while True:
        pairs = [(c1, c2) for i, c1 in enumerate(clauses)
                          for c2 in clauses[i+1:]]

        for (c1, c2) in pairs:
            for lit in c1:
                check_time()
                if -lit in c2:
                    res = list(set(c1 + c2))
                    res = [l for l in res if l != lit and l != -lit]
                    res_clause = tuple(sorted(set(res)))
                    if not res:
                        return False
                    new.add(res_clause)

        if new.issubset(clause_set):
            return True
        clause_set.update(new)
        clauses = list(clause_set)

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sat_solver.py [dp|dpll|res] <input_file>")
        sys.exit(1)

    method = sys.argv[1].lower()
    input_file = sys.argv[2]

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
    except RuntimeError as e:
        print(f"[ERROR] {e}")

    # Benchmark report
    wall_time = time.time() - start_time
    cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    cpu_usage = (cpu_time / wall_time) * 100 if wall_time > 0 else 0
    print(f"\n[Benchmark]")
    print(f"Total operations: {ops:,}")
    print(f"Wall time: {wall_time:.2f} seconds")
    print(f"CPU time: {cpu_time:.2f} seconds")
    print(f"CPU usage: {cpu_usage:.2f}%")
