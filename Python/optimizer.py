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

    #------helper----

    def route_arrival_time(self, v, route):
        ok, t = self.simulate(v, route)
        return t if ok else None

    def compute_slack(self, v, route):
        arrival = self.route_arrival_time(v, route)
        if arrival is None:
            return None

        slack = {}
        for node in route:
            emp = node - self.V
            slack[node] = self.allowed_deadline[emp] - arrival
        return slack

    #--------main solver

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

        # ====================
        # Repair phase (swap)
        # ====================

        assigned = {n for r in self.routes for n in r}
        unassigned = [n for n in nodes if n not in assigned]

        for x in unassigned:

            repaired = False
            candidates = []

            for v in range(self.V):

                if not self.routes[v]:
                    continue

                slack_info = self.compute_slack(v, self.routes[v])
                if slack_info is None:
                    continue

                for node in self.routes[v]:
                    emp = node - self.V
                    candidates.append(
                        (node, v, slack_info[node], self.priority[emp])
                    )

            candidates.sort(key=lambda x: (-x[2], x[3]))

            for y_node, y_vehicle, _, _ in candidates:

                temp_route = self.routes[y_vehicle].copy()
                temp_route.remove(y_node)

                for pos in range(len(temp_route) + 1):

                    trial = temp_route[:pos] + [x] + temp_route[pos:]
                    ok, _ = self.simulate(y_vehicle, trial)

                    if not ok:
                        continue

                    for v2 in range(self.V):

                        if len(self.routes[v2]) >= self.vehicles.loc[v2, "capacity"]:
                            continue

                        for pos2 in range(len(self.routes[v2]) + 1):

                            trial2 = self.routes[v2][:pos2] + \
                                [y_node] + self.routes[v2][pos2:]

                            ok2, _ = self.simulate(v2, trial2)

                            if ok2:
                                self.routes[y_vehicle] = trial
                                self.routes[v2] = trial2
                                repaired = True
                                break

                        if repaired:
                            break
                    if repaired:
                        break
                if repaired:
                    break


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

                    if best is None or lateness < best[0] or \
                       (lateness == best[0] and t < best[1]):
                        best = (lateness, t, v, pos)

            if best:
                _, _, v, pos = best
                self.routes[v].insert(pos, x)

        return self.routes
