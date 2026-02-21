import json
from data_loader import load_data
from distance import build_distance_matrix
from optimizer import Optimizer
from output_formatter import build_output


def run_optimisation(FILE):

    employees, vehicles, baseline, meta, max_delay = load_data(FILE)

    pickup_coords = list(zip(employees["pickup_lat"], employees["pickup_lng"]))
    vehicle_coords = list(zip(vehicles["current_lat"], vehicles["current_lng"]))
    factory_coord = (
        employees.loc[0, "drop_lat"],
        employees.loc[0, "drop_lng"]
    )

    dist = build_distance_matrix(
        vehicle_coords,
        pickup_coords,
        factory_coord
    )

    opt = Optimizer(employees, vehicles, dist, max_delay)

    routes = opt.run()

    result = build_output(
        routes,
        employees,
        vehicles,
        dist,
        vehicles["avg_speed_kmph"].values,
        len(vehicle_coords) + len(pickup_coords)
    )

    return result