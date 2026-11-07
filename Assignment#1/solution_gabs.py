import search
from dataclasses import dataclass

@dataclass
class Task:
    a: int
    p: int
    s: int
    w: int

class CRSproblem(search.Problem):
    def __init__(self):
        """Method that instantiate your class.
        You can change the content of this.
        self.initial is where the initial state of
        the CRS problem should be saved."""
        self.initial = None

        self.S = None # number of CPU's (iniciei a None para não existirerem erros caso não seja inicializado com o load)
        self.N = None # number of tasks
        self.tasks = [] # list of tasks, each task is a tuple (time of arrival, duration of execution, number of cpus required, priority weight)

    def load(self, fh):
        """loads a CRS problem from the file object fh.
        You may initialize self.initial here."""

        for line in fh:

            # 1. Clean up the line (remove \n)
            line = line.strip()
            
            # 2. Skip empty lines or comment lines
            if not line or line.startswith('#'):
                continue

            # 3. Split the line into parts
            data = line.split()

            if self.S is None:
                # This is the first line, which contains the number of CPUs
                self.S = int(data[0])
                self.N = int(data[1])

            else:
                # This is a task line, which contains the task parameters
                a = int(data[0])  # time of arrival
                p = int(data[1])  # duration of execution
                s = int(data[2])  # number of CPUs required
                w = int(data[3])  # priority weight

                # Create a Task object and add it to the list of tasks
                new_task = Task(a, p, s, w)
                self.tasks.append(new_task)

    def cost(self, sol):
        """Compute cost of solution sol."""

        F = 0

        for i in range (self.N):
            u , v = sol[i]
            task = self.tasks[i]

            c = u + self.tasks[i].p

            f = c - self.tasks[i].a

            F += self.tasks[i].w * f

        return F

    def check(self, sol):
        """Check if solution sol satisfies problem constraints."""
        if len(sol) != self.N:
            return False

        for i in range (self.N):
            u , v = sol[i]

            if u < self.tasks[i].a:
                return False

            if v < 0 or v + self.tasks[i].s > self.S:
                return False
        
        for i in range (self.N):
            ui , vi = sol[i]
            for j in range (i + 1, self.N):
                uj , vj = sol[j]
                
                core_overlap = vi + self.tasks[i].s > vj and vj + self.tasks[j].s > vi
                time_overlap = ui + self.tasks[i].p > uj and uj + self.tasks[j].p > ui

                if core_overlap and time_overlap:
                    return False

        return True

# ---------------------------------------------------------
# Local Testing Area
# ---------------------------------------------------------
# if __name__ == "__main__":
#     # Any code written in this block only runs if you execute THIS script directly.
#     # The Moodle auto-grader will ignore it, making it the perfect place to test!
#     my_problem = CRSproblem()

#     file_path = "Public/ex100.dat"  # Check exact folder/file name in your Public folder

#     with open(file_path, "r") as file:
#         my_problem.load(file)

#     print(f"Server Cores (S): {my_problem.S}")
#     print(f"Number of Tasks (N): {my_problem.N}")
#     print("Tasks loaded:")
#     for idx, t in enumerate(my_problem.tasks):
#         print(f"  Task {idx}: arrival={t.a}, duration={t.p}, cores={t.s}, weight={t.w}")

#     plan_sol = [(0, 0), (4, 0)]
#     cost_val = my_problem.cost(plan_sol)
#     print(f"Computed Cost: {cost_val} (Expected: 12)")
#     print("Is plan_sol valid?", my_problem.check(plan_sol))

#     invalid_overlap = [(0, 0), (0, 0)]
#     print("Collision check (expect False):", my_problem.check(invalid_overlap))

#     out_of_bounds = [(0, 2), (4, 0)]
#     print("Out of bounds check (expect False):", my_problem.check(out_of_bounds))

#     early_start = [(-1, 0), (4, 0)]
#     print("Early start check (expect False):", my_problem.check(early_start))

import ast

if __name__ == "__main__":
    print("Testing examples ex100 to ex109...\n")
    
    all_passed = True

    for i in range(100, 110):
        dat_path = f"Public/ex{i}.dat"
        plan_path = f"Public/ex{i}.plan"

        problem = CRSproblem()

        # 1. Load problem definition
        with open(dat_path, "r") as fh:
            problem.load(fh)

        # 2. Parse the schedule from the .plan file
        with open(plan_path, "r") as fh:
            plan_str = fh.read().strip()
            # ast.literal_eval converts the string "[(0, 0), ...]" into a real Python list
            sol = ast.literal_eval(plan_str)

        # 3. Check feasibility and cost
        is_valid = problem.check(sol)
        total_cost = problem.cost(sol)

        status = "PASSED" if is_valid else "FAILED"
        if not is_valid:
            all_passed = False

        print(f"[{status}] ex{i}: Valid = {is_valid} | Cost = {total_cost} | Tasks = {problem.N} | Cores = {problem.S}")

    print("\n" + ("=" * 40))
    if all_passed:
        print("ALL EXAMPLES PASSED AND ARE FEASIBLE!")
    else:
        print("SOME EXAMPLES FAILED CONSTRAINT CHECKS.")
    print("=" * 40)
