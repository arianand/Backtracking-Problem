
import heapq


# ---------------------------------------
# 1. ROAD CLASS
# ---------------------------------------

class Road:
    def __init__(self, destination, traffic_profile):
        self.destination = destination
        self.traffic_profile = traffic_profile
        self.is_closed = False

    def travel_time(self, current_time):
        """
        Returns estimated travel time based on
        when the emergency vehicle enters the road.

        Traffic profile format:
        [(minute, travel_time), ...]
        """

        profile = self.traffic_profile

        if current_time <= profile[0][0]:
            return profile[0][1]

        for i in range(len(profile) - 1):
            time1, cost1 = profile[i]
            time2, cost2 = profile[i + 1]

            if time1 <= current_time <= time2:
                fraction = (current_time - time1) / (time2 - time1)

                # Interpolate between traffic observations
                return cost1 + fraction * (cost2 - cost1)

        return profile[-1][1]


# ---------------------------------------
# 2. GRAPH REPRESENTATION
# ---------------------------------------

graph = {
    "A": [
        Road("B", [(0, 3)]),
        Road("C", [(0, 6)])
    ],

    "B": [
        Road("D", [(0, 5), (30, 11)]),
        Road("E", [(0, 7), (30, 8)])
    ],

    "C": [
        Road("D", [(0, 4)]),
        Road("E", [(0, 5)])
    ],

    "D": [
        Road("F", [(0, 4)])
    ],

    "E": [
        Road("F", [(0, 3)])
    ],

    "F": []
}


# ---------------------------------------
# 3. TIME-DEPENDENT DIJKSTRA
# ---------------------------------------

def dijkstra(graph, start, destination, start_time):

    # Priority queue stores (arrival time, intersection)
    priority_queue = [(start_time, start)]

    # Earliest known arrival time at each intersection
    arrival_times = {start: start_time}

    # Stores where each intersection came from
    previous = {}

    while priority_queue:

        current_time, current_node = heapq.heappop(priority_queue)

        # Ignore outdated queue entries
        if current_time > arrival_times[current_node]:
            continue

        # Destination reached
        if current_node == destination:
            break

        # Examine roads leaving current intersection
        for road in graph[current_node]:

            if road.is_closed:
                continue

            # Determine travel time when entering this road
            duration = road.travel_time(current_time)

            # Calculate arrival time at next intersection
            new_arrival = current_time + duration

            neighbor = road.destination

            if new_arrival < arrival_times.get(neighbor, float("inf")):

                arrival_times[neighbor] = new_arrival
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_arrival, neighbor)
                )

    # No route found
    if destination not in arrival_times:
        return None, float("inf")

    # Reconstruct the fastest route
    path = []
    current = destination

    while current != start:
        path.append(current)
        current = previous[current]

    path.append(start)
    path.reverse()

    total_time = arrival_times[destination] - start_time

    return path, total_time


# ---------------------------------------
# 4. TRAFFIC CHANGE DETECTION
# ---------------------------------------

def save_traffic_snapshot(graph, current_time):
    """
    Records current estimated travel times
    for all roads.
    """

    snapshot = {}

    for source, roads in graph.items():
        for road in roads:
            snapshot[(source, road.destination)] = (
                road.travel_time(current_time),
                road.is_closed
            )

    return snapshot


def traffic_changed_significantly(
    graph, old_snapshot, current_time, threshold
):
    """
    Checks whether any road has changed enough
    to justify recalculating the route.
    """

    for source, roads in graph.items():
        for road in roads:

            old_time, was_closed = old_snapshot[
                (source, road.destination)
            ]

            # A newly closed road always triggers recalculation
            if road.is_closed and not was_closed:
                print("A road has closed!")
                return True

            # A significant travel-time change triggers recalculation
            new_time = road.travel_time(current_time)

            if abs(new_time - old_time) >= threshold:
                print(
                    f"Significant traffic change on "
                    f"{source} -> {road.destination}"
                )
                return True

    return False


# ---------------------------------------
# 5. UPDATE TRAFFIC CONDITIONS
# ---------------------------------------

def update_traffic(graph):

    # Traffic becomes heavier on B -> D
    for road in graph["B"]:
        if road.destination == "D":
            road.traffic_profile = [(0, 12)]

        # Traffic becomes lighter on B -> E
        if road.destination == "E":
            road.traffic_profile = [(0, 4)]


# ---------------------------------------
# 6. EMERGENCY VEHICLE SIMULATION
# ---------------------------------------

def emergency_vehicle_simulation():

    start = "A"
    destination = "F"

    # Time 0 represents 5:00 PM
    current_time = 0

    # Recalculate if travel time changes by 3 minutes or more
    traffic_threshold = 3

    print("INITIAL ROUTE")

    route, total_time = dijkstra(
        graph, start, destination, current_time
    )

    if route is None:
        print("No available route.")
        return

    print("Route:", " -> ".join(route))
    print("Estimated travel time:", total_time, "minutes")

    # Save traffic conditions before the update
    old_snapshot = save_traffic_snapshot(graph, current_time)

    # Simulate traveling from A to B
    first_road = next(
        road for road in graph["A"]
        if road.destination == "B"
    )

    current_time += first_road.travel_time(current_time)

    current_location = "B"

    print("\nEMERGENCY VEHICLE REACHES B")
    print("Elapsed time:", current_time, "minutes")

    # Simulate receiving updated traffic information
    update_traffic(graph)

    print("\nTRAFFIC CONDITIONS UPDATED")

    # Check whether a new route is needed
    if traffic_changed_significantly(
        graph,
        old_snapshot,
        current_time,
        traffic_threshold
    ):

        print("\nRECALCULATING ROUTE...")

        new_route, new_total_time = dijkstra(
            graph,
            current_location,
            destination,
            current_time
        )

        if new_route is None:
            print("No available alternative route.")
            return

        remaining_time = new_total_time

        print("New route:", " -> ".join(new_route))
        print(
            "Estimated remaining travel time:",
            remaining_time,
            "minutes"
        )

        print(
            "Estimated total journey time:",
            current_time + remaining_time,
            "minutes"
        )

    else:
        print("\nTraffic has not changed significantly.")
        print("Continue following the original route.")


# ---------------------------------------
# 7. RUN PROGRAM
# ---------------------------------------

if __name__ == "__main__":
    emergency_vehicle_simulation()
