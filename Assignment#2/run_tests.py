import ast
import glob
import os
import sys
import time

from solution import CRSproblem

def cost(problem, sol):
    return sum(t.w * (u + t.p - t.a) for t, (u, _) in zip(problem.tasks, sol))

def check(problem, sol):
    if len(sol) != problem.N:
        return False
    for t, (u, v) in zip(problem.tasks, sol):
        if u < t.a or v < 0 or v + t.s > problem.S:
            return False
    for i, (ui, vi) in enumerate(sol):
        ti = problem.tasks[i]
        for j in range(i + 1, problem.N):
            uj, vj = sol[j]
            tj = problem.tasks[j]
            if ui + ti.p > uj and uj + tj.p > ui and vi + ti.s > vj and vj + tj.s > vi:
                return False
    return True

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "Public"
    for dat in sorted(glob.glob(os.path.join(folder, "*.dat"))):
        problem = CRSproblem()
        with open(dat) as fh:
            problem.load(fh)

        start = time.time()
        sol = problem.solve()
        elapsed = time.time() - start

        plan = dat[:-4] + ".plan"
        expected = ""
        if os.path.exists(plan):
            with open(plan) as fh:
                expected = f" | plan cost = {cost(problem, ast.literal_eval(fh.read().strip()))}"

        print(f"{os.path.basename(dat)}: valid = {check(problem, sol)} | cost = {cost(problem, sol)}{expected} | {elapsed:.2f}s")
