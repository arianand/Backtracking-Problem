
#include <iostream>
#include <vector>
#include <climits>
#include <chrono>
#include <algorithm>

using namespace std;
using namespace chrono;

// Represents a road connecting two intersections
struct Road {
    int destination;
    int distance;
};

class EmergencyRouting {
private:
    int V;

    vector<vector<Road>> graph;
    vector<vector<bool>> blocked;
    vector<bool> visited;

    vector<int> currentPath;
    vector<int> bestPath;

    long long bestDistance = LLONG_MAX;
    long long recursiveCalls = 0;

public:

    // Constructor
    EmergencyRouting(int vertices) {
        V = vertices;

        graph.resize(V);
        blocked.assign(V, vector<bool>(V, false));
        visited.assign(V, false);
    }

    // Add a road between two intersections
    void addRoad(int u, int v, int distance) {

        if (u < 0 || u >= V || v < 0 || v >= V ||
            distance <= 0) {
            cout << "Invalid road information!\n";
            return;
        }

        graph[u].push_back({v, distance});
        graph[v].push_back({u, distance});
    }

    // Mark a road as blocked
    void blockRoad(int u, int v) {

        if (u < 0 || u >= V || v < 0 || v >= V) {
            cout << "Invalid road!\n";
            return;
        }

        blocked[u][v] = true;
        blocked[v][u] = true;
    }

    // Recursive backtracking function
    void backtrack(int current, int destination,
                   long long currentDistance) {

        recursiveCalls++;

        // Destination reached
        if (current == destination) {

            if (currentDistance < bestDistance) {

                bestDistance = currentDistance;
                bestPath = currentPath;
            }

            return;
        }

        // Branch-and-bound pruning
        if (currentDistance >= bestDistance) {
            return;
        }

        // Explore neighboring intersections
        for (const Road& road : graph[current]) {

            int next = road.destination;
            int weight = road.distance;

            // Check whether the road is valid
            if (visited[next] || blocked[current][next]) {
                continue;
            }

            // Avoid unnecessary exploration
            if (currentDistance > bestDistance - weight) {
                continue;
            }

            // Choose
            visited[next] = true;
            currentPath.push_back(next);

            // Explore
            backtrack(next, destination,
                      currentDistance + weight);

            // Undo (backtrack)
            currentPath.pop_back();
            visited[next] = false;
        }
    }

    // Find the shortest feasible route
    void findShortestRoute(int source, int destination) {

        if (source < 0 || source >= V ||
            destination < 0 || destination >= V ||
            source == destination) {

            cout << "Invalid source or destination!\n";
            return;
        }

        bestDistance = LLONG_MAX;
        recursiveCalls = 0;

        fill(visited.begin(), visited.end(), false);

        currentPath.clear();
        bestPath.clear();

        visited[source] = true;
        currentPath.push_back(source);

        auto startTime = high_resolution_clock::now();

        backtrack(source, destination, 0);

        auto endTime = high_resolution_clock::now();

        auto duration = duration_cast<microseconds>(
            endTime - startTime
        ).count();

        // Display results
        cout << "\n========== ROUTE RESULTS ==========\n";

        if (bestPath.empty()) {

            cout << "No feasible route found!\n";

        } else {

            cout << "Optimal Route: ";

            for (int i = 0; i < bestPath.size(); i++) {

                cout << bestPath[i];

                if (i != bestPath.size() - 1) {
                    cout << " -> ";
                }
            }

            cout << "\nMinimum Distance: "
                 << bestDistance << " km\n";
        }

        cout << "Recursive Calls: "
             << recursiveCalls << "\n";

        cout << "Execution Time: "
             << duration << " microseconds\n";

        cout << "===================================\n";
    }
};

// Main function
int main() {

    int n, m;

    cout << "===== EMERGENCY VEHICLE ROUTING =====\n";

    cout << "Enter number of intersections: ";
    cin >> n;

    cout << "Enter number of roads: ";
    cin >> m;

    if (!cin || n < 2 || m < 0) {
        cout << "Invalid graph input!\n";
        return 1;
    }

    EmergencyRouting system(n);

    cout << "\nEnter roads (u v distance):\n";

    for (int i = 0; i < m; i++) {

        int u, v, distance;
        cin >> u >> v >> distance;

        system.addRoad(u, v, distance);
    }

    int k;

    cout << "\nEnter number of blocked roads: ";
    cin >> k;

    if (!cin || k < 0) {
        cout << "Invalid blocked-road input!\n";
        return 1;
    }

    cout << "Enter blocked roads (u v):\n";

    for (int i = 0; i < k; i++) {

        int u, v;
        cin >> u >> v;

        system.blockRoad(u, v);
    }

    int source, destination;

    cout << "\nEnter ambulance starting point: ";
    cin >> source;

    cout << "Enter hospital destination: ";
    cin >> destination;

    system.findShortestRoute(source, destination);

    return 0;
}
