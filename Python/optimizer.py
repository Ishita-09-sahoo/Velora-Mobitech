import numpy as np
from sklearn.cluster import KMeans


class Optimizer:
    def __init__(self, employees, vehicles, dist_matrix, max_delay, cost_weight, time_weight):
        self.employees = employees
        self.vehicles = vehicles
        self.dist = dist_matrix
        self.V = len(vehicles)
        self.E = len(employees)
        self.FACTORY = self.V + self.E
        self.cost_weight = cost_weight
        self.time_weight = time_weight
        self.sharing_pref = employees["sharing_preference"].values
        self.vehicle_pref = employees["vehicle_preference"].values
        self.vehicle_type = vehicles["category"].values
        self.priority = employees["priority"].values
        self.max_priority = max(self.priority)
        self.speed = vehicles["avg_speed_kmph"].values
        self.earliest = employees["earliest_pickup"].values
        self.latest = employees["latest_drop"].values
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

    def route_total_distance(self, v, route):
        if not route:
            return 0
        total_distance = self.dist[v][route[0]]
        for i in range(len(route) - 1):
            total_distance += self.dist[route[i]][route[i + 1]]
        total_distance += self.dist[route[-1]][self.FACTORY]
        return total_distance

    def sharing_limit(self, emp):
        p = str(self.sharing_pref[emp]).strip().lower()
        if p == "single":
            return 1
        elif p == "double":
            return 2
        elif p == "triple":
            return 3
        else:
            return self.vehicles["capacity"].max()

    def cluster_employee_nodes(self):
        coords = self.employees[["pickup_lat", "pickup_lng"]].values
        num_clusters = min(self.V, self.E)
        if self.E <= num_clusters:
            return list(range(self.V, self.V + self.E))
        kmeans = KMeans(n_clusters=num_clusters, random_state=0)
        labels = kmeans.fit_predict(coords)
        clusters = {}
        for i in range(self.E):
            cluster_id = labels[i]
            clusters.setdefault(cluster_id, []).append(i)
        for c in clusters:
            clusters[c].sort(key=lambda i: self.allowed_deadline[i])
        cluster_order = sorted(
            clusters.keys(),
            key=lambda c: min(self.allowed_deadline[i] for i in clusters[c])
        )
        nodes = []
        for c in cluster_order:
            nodes.extend(self.V + i for i in clusters[c])
        return nodes

    def two_opt(self, v, route):
        if len(route) < 3:
            return route
        best_route = route.copy()
        best_distance = self.route_total_distance(v, best_route)
        improved = True
        while improved:
            improved = False
            for i in range(len(best_route) - 1):
                for j in range(i + 2, len(best_route)):
                    new_route = (
                        best_route[:i+1]
                        + best_route[i+1:j+1][::-1]
                        + best_route[j+1:]
                    )
                    ok, _ = self.simulate(v, new_route)
                    if not ok:
                        continue
                    new_distance = self.route_total_distance(v, new_route)
                    if new_distance < best_distance:
                        best_route = new_route
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break
        return best_route

    def greedy_insert(self, nodes, hard_sharing=True, hard_vehicle=True):
        """
        Try to insert each node into the best feasible slot.

        hard_sharing=True  → strictly reject slots that violate sharing preference
        hard_sharing=False → allow sharing violations, penalise lightly in score

        hard_vehicle=True  → strictly reject slots that violate vehicle preference
        hard_vehicle=False → allow vehicle violations, penalise lightly in score

        Both flags are True in Pass 1 so high-priority employees grab
        compliant slots first. Both are False in Pass 2 (last resort).

        Returns list of nodes that could not be assigned.
        """
        unassigned = []

        for x in nodes:
            emp = x - self.V
            limit = self.sharing_limit(emp)
            candidates = []

            emp_pref = str(self.vehicle_pref[emp]).strip().lower()

            vehicle_order = sorted(
                range(self.V), key=lambda v: self.dist[v][x]
            )

            for v in vehicle_order:
                if len(self.routes[v]) >= self.vehicles.loc[v, "capacity"]:
                    continue

                veh_type = str(self.vehicle_type[v]).strip().lower()

                # ----- hard vehicle preference check -----
                if hard_vehicle and emp_pref != "any" and emp_pref != veh_type:
                    continue   # hard reject wrong vehicle category

                current_route = self.routes[v]

                for pos in range(len(current_route) + 1):
                    trial = current_route[:pos] + [x] + current_route[pos:]

                    # ----- hard sharing check -----
                    if hard_sharing and len(trial) > limit:
                        continue   # hard reject sharing violation

                    ok, arrival = self.simulate(v, trial)
                    if not ok:
                        continue

                    distance = self.route_total_distance(v, trial)
                    cost = distance * self.vehicles.loc[v, "cost_per_km"]

                    sharing_violated = max(0, len(trial) - limit)
                    vehicle_violated = (
                        emp_pref != "any" and emp_pref != veh_type)

                    candidates.append({
                        "vehicle": v,
                        "position": pos,
                        "arrival": arrival,
                        "cost": cost,
                        "sharing_violated": sharing_violated,
                        "vehicle_violated": vehicle_violated
                    })

            if not candidates:
                unassigned.append(x)
                continue

            # ---- normalise and score ----
            arrival_values = [c["arrival"] for c in candidates]
            cost_values = [c["cost"] for c in candidates]
            min_time, max_time = min(arrival_values), max(arrival_values)
            min_cost, max_cost = min(cost_values),    max(cost_values)

            best_obj = None
            best_vehicle = None
            best_position = None

            for c in candidates:
                norm_time = 0 if max_time == min_time else \
                    (c["arrival"] - min_time) / (max_time - min_time)
                norm_cost = 0 if max_cost == min_cost else \
                    (c["cost"] - min_cost) / (max_cost - min_cost)

                # in relaxed pass, lightly penalise violations so
                # least-violated slot still wins
                violation_score = c["sharing_violated"] * 0.3 + \
                    (0.1 if c["vehicle_violated"] else 0)

                objective = (
                    self.time_weight * norm_time +
                    self.cost_weight * norm_cost +
                    violation_score
                )

                if best_obj is None or objective < best_obj:
                    best_obj = objective
                    best_vehicle = c["vehicle"]
                    best_position = c["position"]

            if best_vehicle is not None:
                self.routes[best_vehicle].insert(best_position, x)

        return unassigned

    def run(self):

        nodes = self.cluster_employee_nodes()

        # -------------------------------------------------------
        # PASS 1 — greedy with HARD sharing constraint
        # High-priority / tight-deadline employees (ordered by
        # clustering + deadline sort) grab slots first.
        # -------------------------------------------------------
        unassigned_after_greedy = self.greedy_insert(
            nodes, hard_sharing=True, hard_vehicle=True)

        # -------------------------------------------------------
        # Repair phase — swap to find room for unassigned nodes
        # (same logic as before, still respects hard sharing)
        # -------------------------------------------------------
        still_unassigned = []

        for x in unassigned_after_greedy:
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

            candidates.sort(key=lambda c: (-c[2], c[3]))

            for y_node, y_vehicle, _, _ in candidates:
                temp_route = self.routes[y_vehicle].copy()
                temp_route.remove(y_node)

                emp_x = x - self.V
                emp_y = y_node - self.V
                limit_x = self.sharing_limit(emp_x)
                limit_y = self.sharing_limit(emp_y)

                for pos in range(len(temp_route) + 1):
                    trial = temp_route[:pos] + [x] + temp_route[pos:]

                    if len(trial) > limit_x:
                        continue   # still respect hard sharing in repair

                    ok, _ = self.simulate(y_vehicle, trial)
                    if not ok:
                        continue

                    for v2 in range(self.V):
                        if len(self.routes[v2]) >= self.vehicles.loc[v2, "capacity"]:
                            continue
                        # prevent inserting y_node into a route it's already in
                        if y_node in self.routes[v2]:
                            continue
                        for pos2 in range(len(self.routes[v2]) + 1):
                            trial2 = self.routes[v2][:pos2] + \
                                [y_node] + self.routes[v2][pos2:]

                            if len(trial2) > limit_y:
                                continue  # respect displaced node's sharing too

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

            if not repaired:
                still_unassigned.append(x)

        # -------------------------------------------------------
        # PASS 2 — relaxed greedy for employees who genuinely
        # could not be assigned without a sharing violation.
        # Process in priority order (best priority first).
        # -------------------------------------------------------
        still_unassigned.sort(key=lambda x: self.priority[x - self.V])

        truly_unassigned = self.greedy_insert(
            still_unassigned, hard_sharing=False, hard_vehicle=False
        )

        # -------------------------------------------------------
        # Last resort soft-force for anything still remaining
        # (e.g. TC04 E10 which is genuinely infeasible on time)
        # -------------------------------------------------------
        truly_unassigned.sort(key=lambda x: self.priority[x - self.V])

        for x in truly_unassigned:
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

        # -------------------------------------------------------
        # 2-OPT route improvement
        # -------------------------------------------------------
        for v in range(self.V):
            if self.routes[v]:
                self.routes[v] = self.two_opt(v, self.routes[v])

        return self.routes
