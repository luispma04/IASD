import search
import sys
import ast
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
        pass

# ---------------------------------------------------------
# Local Testing Area
# --------------------------------------------------------

# PARA TESTAR, INVOCAR O SCRIPT ASSIM: python solution.py <path_and_name_without_extension>
# EXEMPLO: python solution.py Public/costum1

if __name__ == "__main__":
    # Check if the base path argument was provided
    if len(sys.argv) < 2:
        print("Usage: python solution.py <path_and_name_without_extension>")
        print("Example: python solution.py test/test")
        sys.exit(1)
        
    base_path = sys.argv[1]
    dat_path = base_path + ".dat"
    plan_path = base_path + ".plan"
    
    print(f"Loading problem from: {dat_path}")
    my_problem = CRSproblem()
    
    try:
        # 1. Load the .dat file
        with open(dat_path, "r") as dat_file:
            my_problem.load(dat_file)
            
        print(f"Problem successfully loaded! (S: {my_problem.S}, N: {my_problem.N})")
        
        # 2. Read and parse the .plan file
        print(f"Reading solution plan from: {plan_path}")
        with open(plan_path, "r") as plan_file:
            plan_content = plan_file.read().strip()
            solution = ast.literal_eval(plan_content)
            
        print(f"Parsed solution: {solution}")
        
        # 3. Calculate and print the cost
        total_cost = my_problem.cost(solution)
        print(f"Total cost (F): {total_cost}")
        
    except FileNotFoundError as e:
        print(f"Error: File not found -> {e}")
    except Exception as e:
        print(f"An error occurred: {e}")