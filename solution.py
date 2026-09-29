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
        pass

    def check(self, sol):
        """Check if solution sol satisfies problem constraints."""
        pass

# ---------------------------------------------------------
# Local Testing Area
# ---------------------------------------------------------
if __name__ == "__main__":
    # Any code written in this block only runs if you execute THIS script directly.
    # The Moodle auto-grader will ignore it, making it the perfect place to test!
    
    print("Testing CRSproblem...")
    my_problem = CRSproblem()
    
    # Example of how you might test your load function later:
    # with open("example1.dat", "r") as file:
    #     my_problem.load(file)
    #     print("Cost:", my_problem.cost([(10,0), (11,2), (3,4), (0,0)]))