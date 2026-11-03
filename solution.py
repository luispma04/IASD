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

        self.S = None # number of CPU's
        self.N = None # number of tasks
        self.tasks = [] # list of tasks (time of arrival, duration, number of cpus, priority weight)

    def load(self, fh):
        """loads a CRS problem from the file object fh.
        You may initialize self.initial here."""

        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            data = line.split()

            if self.S is None:
                self.S = int(data[0])
                self.N = int(data[1])
            else:
                a, p, s, w = map(int, data[:4])
                self.tasks.append(Task(a, p, s, w))

        # state: (current time, bitmask of started tasks, for each cpu the time it becomes free)
        t0 = min(t.a for t in self.tasks)
        self.initial = (t0, 0, (t0,) * self.S)

    def actions(self, state):
        """Returns the list of actions that can be executed in the given state.
        An action (i, v) starts task i now on cpus v..v+s-1; None advances the
        time to the next arrival or cpu release."""
        now, done, free = state
        acts = []
        for i, t in enumerate(self.tasks):
            if done >> i & 1 or t.a > now:
                continue
            for v in range(self.S - t.s + 1):
                if all(f <= now for f in free[v:v + t.s]):
                    acts.append((i, v))
        if self.next_time(state) is not None:
            acts.append(None)
        return acts

    def next_time(self, state):
        """Returns the next time something changes after the current one, if any."""
        now, done, free = state
        times = [t.a for i, t in enumerate(self.tasks) if not done >> i & 1]
        times += free
        return min((x for x in times if x > now), default=None)

    def result(self, state, action):
        """Returns the state that results from executing the given action in the given state."""
        now, done, free = state
        if action is None:
            now = self.next_time(state)
            return now, done, tuple(max(f, now) for f in free)
        i, v = action
        t = self.tasks[i]
        return now, done | 1 << i, free[:v] + (now + t.p,) * t.s + free[v + t.s:]

    def goal_test(self, state):
        """Returns True if every task has started."""
        return state[1] == (1 << self.N) - 1

    def path_cost(self, c, state1, action, state2):
        """Returns the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. The total
        weighted flow time is the sum of the weighted durations, charged on the
        first step, plus the weight of each waiting task per unit of time."""
        now, done, free = state1
        if state1 == self.initial:
            c += sum(t.w * t.p for t in self.tasks)
        if action is None:
            waiting = sum(t.w for i, t in enumerate(self.tasks) if not done >> i & 1 and t.a <= now)
            c += waiting * (state2[0] - now)
        return c

    def solve(self):
        """Calls the uninformed search algorithm chosen.
        Returns a solution using the specified format."""
        node = search.uniform_cost_search(self)
        if node is None:
            return None
        sol = [None] * self.N
        for n in node.path()[1:]:
            if n.action is not None:
                i, v = n.action
                sol[i] = (n.parent.state[0], v)
        return sol
