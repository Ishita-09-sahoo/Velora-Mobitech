import numpy as np
from math import radians, sin, cos, sqrt, atan2


def haversine(a, b):
    lat1, lon1 = a
    lat2, lon2 = b

    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    x = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * atan2(sqrt(x), sqrt(1 - x))


def build_distance_matrix(vehicle_coords, pickup_coords, factory_coord):

    nodes = vehicle_coords + pickup_coords + [factory_coord]
    N = len(nodes)

    dist = np.zeros((N, N))

    for i in range(N):
        for j in range(N):
            if i != j:
                dist[i, j] = haversine(nodes[i], nodes[j])

    return dist
