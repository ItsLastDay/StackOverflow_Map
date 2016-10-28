#include <bits/stdc++.h>
using namespace std;

/*
 * Given an adjacency matrix for our problem, compute the
 * set of K nearest neighbours for each vertex.
 *
 * Since our edge weighting scheme is "inverse",
 * meaning that the more - the better, we translate
 * weights.
 *
 * All weights are positive, so we use Dijkstra's algorithm,
 * and terminate it after K steps.
 *
 * Input arguments: 
 *   - path to a text file with matrix;
 *   - integer K.
 *
 * Output: 
 *   for each vertex, a set of pairs "neighbour_num,distance".
 *   Vertex numbers are normalized to 1..number_of_verices.
 *
 *
 * Example output:
 *   1: 2,0.5 10,493 15,1.1
 *   2: 1,0.5 123,45
 *   ...
 *
 *
 * Complexity: 
 *   not exactly known, something like
 *   O(N^2 * K * log(N)), constant is high due to floating point ops.
 *   On the full graph with K = 150, it works with 3500rows/5min speed.
 *  
 */

struct dijkstra
{
    void find_nearest_neighbours(int vertex_num, int num_of_neighbours)
    {
        auto st = set< pair<double, int> >();
        int num_vertices = number_of_verices();

        for (int i = 1; i <= num_vertices; i++)
        {
            current_distance_[i] = 1e15;
        }

        current_distance_[vertex_num] = 0.0;
        for (int i = 1; i <= num_vertices; i++)
        {
            st.insert(make_pair(current_distance_[i], i));
        }

        cout << vertex_num << ": ";
        for (int it = 0; it <= num_of_neighbours; it++)
        {
            auto iter = st.begin();
            int best_vertex = iter->second;
            st.erase(iter);
            for (const auto& edge: adj_list_[best_vertex])
            {
                int to_vertex = edge.first;
                double weight = edge.second;
                double cur_dist = current_distance_[to_vertex];
                double proposed_dist = current_distance_[best_vertex] + weight;

                if (proposed_dist < cur_dist)
                {
                    current_distance_[to_vertex] = proposed_dist;
                    st.erase(make_pair(cur_dist, to_vertex));
                    st.insert(make_pair(proposed_dist, to_vertex));
                }
                current_distance_[to_vertex] = min(current_distance_[to_vertex],
                        current_distance_[best_vertex] + weight);
            }

            // First neighbour is always self.
            if (it > 0)
            {
                cout << best_vertex << "," << current_distance_[best_vertex] << " ";
            }
        }

        cout << endl;
    }

    void read_graph(const char* path_to_matrix)
    {
        ifstream inp(path_to_matrix);
        string row_representation;
        while (getline(inp, row_representation))
        {
            istringstream ss(row_representation);
            int source_vertex;
            ss >> source_vertex;
            source_vertex = normalize_vertex_num(source_vertex);
            ss.ignore(1);

            int dest_vertex, edge_w;
            while (ss >> dest_vertex)
            {
                dest_vertex = normalize_vertex_num(dest_vertex);
                ss.ignore(1);
                ss >> edge_w;
                double edge_weight = convert_edge_w_to_weight(edge_w);
                adj_list_[source_vertex].push_back(make_pair(dest_vertex, edge_weight));
                adj_list_[dest_vertex].push_back(make_pair(source_vertex, edge_weight));
            }
        }
        cout << "Preprocessing end" << endl;
    }

    int number_of_verices()
    {
        return vertex_num_to_normalized_num_.size();
    }
private:
    static const int max_vertices_ = 60000;
    map<int, int> vertex_num_to_normalized_num_;
    vector< pair<int, double> > adj_list_[max_vertices_];
    double current_distance_[max_vertices_];

    int normalize_vertex_num(int vertex_num)
    {
        if (not vertex_num_to_normalized_num_.count(vertex_num))
        {
            vertex_num_to_normalized_num_[vertex_num] = 
                vertex_num_to_normalized_num_.size();
        }
        return vertex_num_to_normalized_num_[vertex_num];
    }

    double convert_edge_w_to_weight(int edge_w)
    {
        // Possible functions: 1000 / x, exp(-x), 100 / log(x), ...
        return 100 / log(edge_w + 1);
    }
};

int main(int argc, char** argv)
{
    assert(argc == 3);
    auto dij = dijkstra();
    int num_of_neighbours = atoi(argv[2]);
    dij.read_graph(argv[1]);

    int num_vertices = dij.number_of_verices();
    for (int i = 1; i <= num_vertices; i++)
    {
        dij.find_nearest_neighbours(i, num_of_neighbours);
    }
    return 0;
}
