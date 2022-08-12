from numba import jit
import numpy as np
import time
import math
import core.func

def compute(parent, pos, target_pos, occupied, map_size):
    
    start_time = time.time()
    if pos == target_pos:
        #parent.target_pos = target_pos
        return
    parent.finding_route = True
    open_routes = [[pos.copy()]]
    max_length =  round(math.sqrt((target_pos[0] - pos[0])**2 + (target_pos[1] - pos[1])**2)+2)
    points_covered = []
    while 1:
        if time.time() - start_time > 0.5:
            parent.finding_route = False
            return

        if len(open_routes) == 0:
            parent.finding_route = False
            parent.target_pos = target_pos
            return

        route = open_routes[0]
        open_routes.remove(route)
        if len(route) >= max_length:
            continue

        point = route[-1]

        for x, y in [
            [1, 0],
            [0, 1],
            [-1, 0],
            [0, -1],
            [1, 1],
            [1, -1],
            [-1, -1],
            [-1, 1],
        ]:
            point_2 = point.copy()
            point_2 = [point_2[0]+x, point_2[1]+y]
            if point_2 in occupied or not 0 <= point_2[0] < map_size[0] or not 0 <= point_2[1] < map_size[1]:
                continue

            if point_2 not in points_covered:
                points_covered.append(point_2)
            else:
                continue

            route_2 = route.copy()
            route_2.append(point_2)

            if point_2 == target_pos:
                parent.finding_route = False
                parent.route_to_pos = route_2
                parent.target_pos = target_pos
                return route_2
            open_routes.append(route_2)

if __name__ == "__main__":
    for x in range(10):
        t = time.time()
        result = compute([1,1], [24,24], tiles, map_size = [25,25])
        print("RESULT:", result)
        print("Time:", time.time()-t)
