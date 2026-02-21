def minutes_to_hhmm(m):
    h = int(m // 60)
    m = int(m % 60)
    return f"{h:02d}:{m:02d}"


def build_output(routes, employees, vehicles, dist, speed, factory_idx):

    employee_rows = []
    vehicle_rows = []

    for v, route in enumerate(routes):

        if not route:
            continue

        t = vehicles.loc[v, "available_from"]
        prev = v
        total_dist = 0

        emp_ids = []

        for node in route:

            d = dist[prev][node]
            t += d / speed[v] * 60
            total_dist += d

            emp = node - len(vehicles)

            if t < employees.loc[emp, "earliest_pickup"]:
                t = employees.loc[emp, "earliest_pickup"]

            employee_rows.append({
                "employee_id": employees.loc[emp, "employee_id"],
                "vehicle_id": vehicles.loc[v, "vehicle_id"],
                "pickup_time": minutes_to_hhmm(t)
            })

            emp_ids.append(employees.loc[emp, "employee_id"])
            prev = node

        t += dist[prev][factory_idx] / speed[v] * 60

        vehicle_rows.append({
            "vehicle_id": vehicles.loc[v, "vehicle_id"],
            "route": emp_ids,
            "factory_time": minutes_to_hhmm(t),
            "distance_km": round(total_dist, 2),
            "cost": round(total_dist * vehicles.loc[v, "cost_per_km"], 2)
        })

    return {
        "employees": employee_rows,
        "vehicles": vehicle_rows
    }
