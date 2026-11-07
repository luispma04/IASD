import search
from collections import namedtuple

# Named tuple representing a task:
# a: arrival time, p: processing time (duration), s: number of CPU cores required, w: priority weight
Task = namedtuple('Task', ['a', 'p', 's', 'w'])


class CRSproblem(search.Problem):
    def __init__(self):
        """Method that instantiate your class.
        You can change the content of this.
        self.initial is where the initial state of
        the CRS problem should be saved."""
        super().__init__(initial=None)
        self.initial = None

        self.S = None       # Total number of CPU cores in the cluster
        self.N = None       # Total number of tasks to schedule
        self.tasks = []     # List of Task objects
        self.base_cost = 0  # Precalculated constant cost: sum of (weight * duration)

    def load(self, fh):
        """loads a CRS problem from the file object fh.
        You may initialize self.initial here."""
        # Reset attributes in case load is called multiple times on the same object
        self.S = None
        self.N = None
        self.tasks = []

        for line in fh:
            line = line.strip()
            # Skip empty lines or comment lines starting with '#'
            if not line or line.startswith('#'):
                continue

            data = line.split()

            # The first data line contains S (number of CPUs) and N (number of tasks)
            if self.S is None:
                self.S = int(data[0])
                self.N = int(data[1])
            else:
                # Following lines define each task: arrival, duration, cpus, weight
                a, p, s, w = map(int, data[:4])
                self.tasks.append(Task(a, p, s, w))

        # Handle edge case where no tasks are loaded
        if not self.tasks:
            self.initial = (0, frozenset(), (0,) * (self.S or 0))
            self.base_cost = 0
            return

        # Initial time is the earliest arrival time among all tasks
        earliest_arrival = min(t.a for t in self.tasks)

        # State representation:
        # (current_time, frozenset_of_started_task_indices, tuple_of_cpu_free_times, min_task_index)
        # Initially, no task has started and all CPUs are free from earliest_arrival.
        all_cpus_free_at_start = (earliest_arrival,) * self.S
        self.initial = (earliest_arrival, frozenset(), all_cpus_free_at_start, 0)

        # Precalculate the constant processing cost sum(w_i * p_i)
        self.base_cost = sum(t.w * t.p for t in self.tasks)

    def actions(self, state):
        """Returns the list of actions that can be executed in the given state.
        An action (i, v) starts task i now on cpus v..v+s-1; None advances the
        time to the next arrival or cpu release."""
        now = state[0]
        started_tasks = state[1]
        free = state[2]
        min_task_index = state[3] if len(state) > 3 else 0
        acts = []

        all_cores_free = max(free) <= now

        # Find all ready tasks that can be scheduled at the current time.
        # Enforcing index >= min_task_index breaks permutation symmetry (eliminates k! branches at the same timestamp)
        for i in range(min_task_index, self.N):
            task = self.tasks[i]
            # Skip if task has already started or has not arrived yet
            if i in started_tasks or task.a > now:
                continue

            # When the entire cluster is idle, placing at v = 0 or v = S - s is an exact
            # mirror reflection. We enforce v = 0 to break this left-right mirror symmetry.
            if all_cores_free:
                acts.append((i, 0))
                continue

            # Try placing the task on contiguous cores starting at core v
            for v in range(self.S - task.s + 1):
                # Boundary alignment heuristic:
                # To prevent fragmenting free CPU cores, a task should be placed against
                # the edge of the cluster or against an adjacent busy core.
                touches_left = (v == 0) or (free[v - 1] > now)
                touches_right = (v + task.s == self.S) or (free[v + task.s] > now)
                is_boundary = touches_left or touches_right

                if is_boundary:
                    # Check if all required cores from v to v + task.s - 1 are free right now
                    needed_cores_free = max(free[v:v + task.s]) <= now
                    if needed_cores_free:
                        acts.append((i, v))

        # Action None means: advance time to the next event (task arrival or CPU release).
        # - If no task can be scheduled right now, advancing time is mandatory.
        # - If tasks can be scheduled, waiting may still be beneficial if there is a future event.
        if not acts:
            acts.append(None)
        elif self.next_time(state) is not None:
            acts.append(None)

        return acts

    def next_time(self, state):
        """Returns the next time something changes after the current one, if any."""
        now = state[0]
        started_tasks = state[1]
        free = state[2]

        # Find the earliest time a currently busy core will become free
        next_event = min((f for f in free if f > now), default=None)

        # Find the earliest arrival time of an unstarted task that arrives in the future
        for i, task in enumerate(self.tasks):
            if i not in started_tasks and task.a > now:
                if next_event is None or task.a < next_event:
                    next_event = task.a

        return next_event

    def result(self, state, action):
        """Returns the state that results from executing the given action in the given state."""
        now = state[0]
        started_tasks = state[1]
        free = state[2]

        # Case 1: Advance time to next event
        if action is None:
            next_event = self.next_time(state)
            # Normalize core availability: cores freed in the past become available at next_event.
            # Reset min_task_index to 0 when time advances.
            updated_free = tuple(max(f, next_event) for f in free)
            return (next_event, started_tasks, updated_free, 0)

        # Case 2: Start task i on cores [v .. v + task.s - 1]
        i, v = action
        task = self.tasks[i]

        # 1. Record task i as started
        new_started = started_tasks | frozenset([i])

        # 2. Update completion time for each core allocated to this task
        task_end_time = now + task.p
        new_free = list(free)
        for core in range(v, v + task.s):
            new_free[core] = task_end_time

        # Next task scheduled at this exact same timestamp must have index > i
        return (now, new_started, tuple(new_free), i + 1)

    def goal_test(self, state):
        """Returns True if every task has started."""
        started_tasks = state[1]
        return len(started_tasks) == self.N

    def path_cost(self, c, state1, action, state2):
        """Returns the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. The total
        weighted flow time is the sum of the weighted durations, charged on the
        first step, plus the weight of each waiting task per unit of time."""
        now = state1[0]
        started_tasks = state1[1]

        # At the root node, add the constant base processing cost of all tasks
        if state1 == self.initial:
            c += self.base_cost

        # When time advances (action is None), charge waiting penalty to tasks that have
        # arrived but are waiting to be scheduled
        if action is None:
            waiting_weight = 0
            for i, task in enumerate(self.tasks):
                if i not in started_tasks and task.a <= now:
                    waiting_weight += task.w

            time_elapsed = state2[0] - now
            c += waiting_weight * time_elapsed

        return c

    def solve(self):
        """Calls the uninformed search algorithm chosen.
        Returns a solution using the specified format."""
        # Call the chosen uninformed search algorithm from search.py once and only once
        node = search.uniform_cost_search(self)
        if node is None:
            return None

        # Reconstruct the solution list of tuples [(u_0, v_0), (u_1, v_1), ...]
        solution = [None] * self.N
        for step in node.path()[1:]:
            if step.action is not None:
                task_id, first_core = step.action
                start_time = step.parent.state[0]
                solution[task_id] = (start_time, first_core)

        return solution