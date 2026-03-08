def minutes_to_hhmm(m):
    h = int(m // 60)
    m = int(m % 60)
    return f"{h:02d}:{m:02d}"


def build_output(routes, employees, vehicles, baseline, dist, speed, factory_idx, max_delay):

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
        vehicle_type = vehicles.loc[v, "category"]
        actual_sharing = len(route)

        t = vehicles.loc[v, "available_from"]
        prev = v
        total_dist = 0

        route_details = []
        route_points = []
        pickup_times = {}
        vehicle_emp_rows = []

        route_points.append({
            "type": "vehicle_start",
            "label": f"Vehicle {vehicles.loc[v, 'vehicle_id']}",
            "lat": float(vehicles.loc[v, "current_lat"]),
            "lng": float(vehicles.loc[v, "current_lng"])
        })

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
            emp_vehicle_pref = employees.loc[emp, "vehicle_preference"]
            emp_sharing_pref = employees.loc[emp, "sharing_preference"]

            pref = str(emp_sharing_pref).strip().lower()
            if pref == "single":
                limit = 1
            elif pref == "double":
                limit = 2
            elif pref == "triple":
                limit = 3
            else:
                limit = float("inf")

            sharing_ok = actual_sharing <= limit
            vehicle_ok = True
            if str(emp_vehicle_pref).strip().lower() != "any":
                if str(emp_vehicle_pref).strip().lower() != str(vehicle_type).strip().lower():
                    vehicle_ok = False

            baseline_cost = baseline_cost_lookup.get(emp_id, 0)
            baseline_time = baseline_time_lookup.get(emp_id, 0)
            total_baseline_cost += baseline_cost

            vehicle_emp_rows.append({
                "employee_id": emp_id,
                "vehicle_id": vehicles.loc[v, "vehicle_id"],
                "priority": int(employees.loc[emp, "priority"]),
                "vehicle_preference": emp_vehicle_pref,
                "sharing_preference": emp_sharing_pref,
                "assigned_vehicle_type": vehicle_type,
                "actual_sharing": actual_sharing,
                "vehicle_preference_satisfied": vehicle_ok,
                "sharing_preference_satisfied": sharing_ok,
                "earliest_pickup": minutes_to_hhmm(employees.loc[emp, "earliest_pickup"]),
                "latest_drop": minutes_to_hhmm(employees.loc[emp, "latest_drop"]),
                "pickup_time": minutes_to_hhmm(pickup_time),
                "drop_time": None,
                "time_taken_min": None,
                "baseline_time_min": baseline_time,
                "baseline_cost": float(baseline_cost),
                "optimized_cost_share": None,
                "cost_saving":         None,
                "cost_saving_percent": None,
                "is_infeasible": False,
                "delay_min": 0,

            })

            route_details.append({
                "employee_id": emp_id,
                "pickup_time": minutes_to_hhmm(pickup_time)
            })
            route_points.append({
                "type": "pickup",
                "label": f"Employee {emp_id}",
                "lat": float(employees.loc[emp, "pickup_lat"]),
                "lng": float(employees.loc[emp, "pickup_lng"])
            })

            prev = node

        # -------- go to factory --------

        t += dist[prev][factory_idx] / speed[v] * 60
        factory_time = t
        route_points.append({
            "type": "factory",
            "label": "Factory",
            "lat": float(employees.loc[0, "drop_lat"]),
            "lng": float(employees.loc[0, "drop_lng"])
        })

        # -------- enrich employee rows --------

        for row in vehicle_emp_rows:
            emp_id = row["employee_id"]
            emp_index = employees.index[employees["employee_id"] == emp_id][0]
            pickup_min = pickup_times[emp_index]
            time_taken = factory_time - pickup_min
            row["drop_time"] = minutes_to_hhmm(factory_time)
            row["time_taken_min"] = int(round(time_taken))
            emp_priority = employees.loc[emp_index, "priority"]
            deadline = employees.loc[emp_index,
                                     "latest_drop"] + max_delay[emp_priority]
            delay = factory_time - deadline
            row["is_infeasible"] = bool(delay > 0)
            row["delay_min"] = float(round(max(0, delay), 1))

        employee_rows.extend(vehicle_emp_rows)   # ← add this after the loop

        # -------- vehicle summary --------
        vehicle_cost = round(total_dist * vehicles.loc[v, "cost_per_km"], 2)
        cost_per_rider = round(vehicle_cost / actual_sharing, 2)
        total_optimized_cost += vehicle_cost

        for row in vehicle_emp_rows:
            b = row["baseline_cost"]
            row["optimized_cost_share"] = cost_per_rider
            row["cost_saving"] = round(b - cost_per_rider, 2)
            row["cost_saving_percent"] = round(
                ((b - cost_per_rider) / b) * 100, 1
            ) if b > 0 else 0.0

        vehicle_rows.append({
            "vehicle_id": vehicles.loc[v, "vehicle_id"],
            "route": route_details,
            "route_points": route_points,
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

    infeasible_list = [e["employee_id"]
                       for e in employee_rows if e["is_infeasible"]]

    total_travel_time = sum(e["time_taken_min"]
                            for e in employee_rows if e["time_taken_min"])
    avg_saving_percent = round(
        sum(e["cost_saving_percent"]
            for e in employee_rows) / len(employee_rows), 1
    ) if employee_rows else 0.0

    return {
        "employees": employee_rows,
        "vehicles": vehicle_rows,
        "total_baseline_cost": round(total_baseline_cost, 2),
        "total_optimized_cost": round(total_optimized_cost, 2),
        "total_cost_saving":       round(total_baseline_cost - total_optimized_cost, 2),
        "savings_percent": round(savings_percent, 2),
        "avg_cost_saving_percent": avg_saving_percent,
        "total_travel_time_min":   total_travel_time,
        "infeasible_count":     len(infeasible_list),
        "infeasible_employees": infeasible_list
    }
