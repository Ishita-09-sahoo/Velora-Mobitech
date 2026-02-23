def minutes_to_hhmm(m):
    h = int(m // 60)
    m = int(m % 60)
    return f"{h:02d}:{m:02d}"


def build_output(routes, employees, vehicles, baseline, dist, speed, factory_idx):

    employee_rows = []
    vehicle_rows = []
    total_baseline_cost = 0
    total_optimized_cost = 0

    baseline_cost_lookup = dict(
        zip(baseline["employee_id"], baseline["baseline_cost"])
    )
    baseline_time_lookup = dict(
        zip(baseline["employee_id"], baseline["baseline_time_min"])
    )

    for v, route in enumerate(routes):

        if not route:
            continue

        t = vehicles.loc[v, "available_from"]
        prev = v
        total_dist = 0

        route_details = []
        pickup_times = {}

        # -------- pickup sequence --------

        for node in route:

            d = dist[prev][node]
            t += d / speed[v] * 60
            total_dist += d

            emp = node - len(vehicles)

            if t < employees.loc[emp, "earliest_pickup"]:
                t = employees.loc[emp, "earliest_pickup"]

            pickup_time = t
            pickup_times[emp] = pickup_time

            emp_id = employees.loc[emp, "employee_id"]

            baseline_cost = baseline_cost_lookup.get(emp_id, 0)
            baseline_time = baseline_time_lookup.get(emp_id, 0)
            total_baseline_cost += baseline_cost

            employee_rows.append({
                "employee_id": emp_id,
                "vehicle_id": vehicles.loc[v, "vehicle_id"],
                "priority": int(employees.loc[emp, "priority"]),
                "earliest_pickup": minutes_to_hhmm(employees.loc[emp, "earliest_pickup"]),
                "latest_drop": minutes_to_hhmm(employees.loc[emp, "latest_drop"]),
                "pickup_time": minutes_to_hhmm(pickup_time),
                "drop_time": None,              # filled later
                "time_taken_min": None,         # filled later
                "baseline_time_min": baseline_time
            })

            route_details.append({
                "employee_id": emp_id,
                "pickup_time": minutes_to_hhmm(pickup_time)
            })
            prev = node

        # -------- go to factory --------

        t += dist[prev][factory_idx] / speed[v] * 60
        factory_time = t

        # -------- enrich employee rows --------

        for row in employee_rows:
            if row["vehicle_id"] == vehicles.loc[v, "vehicle_id"]:

                emp_id = row["employee_id"]
                emp_index = employees.index[
                    employees["employee_id"] == emp_id
                ][0]

                pickup_min = pickup_times[emp_index]
                time_taken = factory_time - pickup_min

                row["drop_time"] = minutes_to_hhmm(factory_time)
                row["time_taken_min"] = int(round(time_taken))

        # -------- vehicle summary --------
        vehicle_cost = round(total_dist * vehicles.loc[v, "cost_per_km"], 2)
        total_optimized_cost += vehicle_cost

        vehicle_rows.append({
            "vehicle_id": vehicles.loc[v, "vehicle_id"],
            "route": route_details,
            "drop_time": minutes_to_hhmm(factory_time),
            "distance_km": round(total_dist, 2),
            "cost": vehicle_cost

        })

    employee_rows.sort(key=lambda x: x["employee_id"])

    savings_percent = 0
    if total_baseline_cost > 0:
        savings_percent = (
            (total_baseline_cost - total_optimized_cost)
            / total_baseline_cost
        ) * 100

    return {
        "employees": employee_rows,
        "vehicles": vehicle_rows,
        "total_baseline_cost": round(total_baseline_cost, 2),
        "total_optimized_cost": round(total_optimized_cost, 2),
        "savings_percent": round(savings_percent, 2)
    }
