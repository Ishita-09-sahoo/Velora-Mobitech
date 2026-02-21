import numpy as np


class Optimizer:

    def __init__(self, employees, vehicles, dist_matrix, max_delay):
        self.employees = employees
        self.vehicles = vehicles
        self.dist = dist_matrix

        self.V = len(vehicles)
        self.E = len(employees)
        self.FACTORY = self.V + self.E

        self.speed = vehicles["avg_speed_kmph"].values

        self.earliest = employees["earliest_pickup"].values
        self.latest = employees["latest_drop"].values
        self.priority = employees["priority"].values

        self.allowed_deadline = np.array([
            self.latest[i] + max_delay[self.priority[i]]
            for i in range(self.E)
        ])

        self.routes = [[] for _ in range(self.V)]

    def simulate(self, v, route, soft=False):

        t = self.vehicles.loc[v, "available_from"]
        prev = v

        for node in route:
            t += self.dist[prev][node] / self.speed[v] * 60
            emp = node - self.V
            if t < self.earliest[emp]:
                t = self.earliest[emp]
            prev = node

        t += self.dist[prev][self.FACTORY] / self.speed[v] * 60

        if not soft:
            for node in route:
                emp = node - self.V
                if t > self.allowed_deadline[emp]:
                    return False, t

        return True, t

    def run(self):

        nodes = list(range(self.V, self.V + self.E))
        nodes.sort(key=lambda n: self.allowed_deadline[n - self.V])

        # Greedy insert
        for x in nodes:
            best = None

            for v in range(self.V):
                if len(self.routes[v]) >= self.vehicles.loc[v, "capacity"]:
                    continue

                for pos in range(len(self.routes[v]) + 1):
                    trial = self.routes[v][:pos] + [x] + self.routes[v][pos:]
                    ok, t = self.simulate(v, trial)

                    if ok and (best is None or t < best[0]):
                        best = (t, v, pos)

            if best:
                _, v, pos = best
                self.routes[v].insert(pos, x)

        # Force assign soft
        assigned = {n for r in self.routes for n in r}
        remaining = [n for n in nodes if n not in assigned]

        for x in remaining:

            best = None

            for v in range(self.V):
                if len(self.routes[v]) >= self.vehicles.loc[v, "capacity"]:
                    continue

                for pos in range(len(self.routes[v]) + 1):
                    trial = self.routes[v][:pos] + [x] + self.routes[v][pos:]
                    _, t = self.simulate(v, trial, soft=True)

                    emp = x - self.V
                    lateness = max(0, t - self.allowed_deadline[emp])

                    if best is None or lateness < best[0]:
                        best = (lateness, t, v, pos)

            if best:
                _, _, v, pos = best
                self.routes[v].insert(pos, x)

        return self.routes
