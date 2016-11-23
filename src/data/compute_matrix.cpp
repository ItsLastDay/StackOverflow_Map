#include <iostream>
#include <cstring>
#include <algorithm>
#include <sstream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

/*
 * Precompute the adjacency matrix, 
 * using `post_tag.csv` produced by `prepare_stacklite_data.py`.
 *
 * The python version `compute_matrix.py` using PostgreSQL works
 * very slow, so we decided to rewrite it in C++ without any DBMS usage.
 *
 * Only the higher-than-main-diagonal part is output.
 *
 * Time: less than two minutes.
 *
 * */

namespace
{
    const string post_tag_csv = "../../data/interim/post_tag.csv";
    const string out_file = "../../data/interim/adj_matrix.txt";

    vector<int> row_count;

    unordered_map<int, vector<int>> post_to_tags;
    vector< pair<int, int> > tags_with_posts;

    void print_row(ostream& out, int row_no)
    {
        out << row_no << ": ";
        for (size_t i = 0; i < row_count.size(); i++)
        {
            if (row_count[i] > 0)
            {
                out << i << "," << row_count[i] << " ";
            }
        }
        out << endl;
    }
};


int main()
{
    ifstream inp(post_tag_csv);
    ofstream out(out_file);
    string current_line;
    int post_id, tag_id;

    // Skip header.
    getline(inp, current_line);

    int max_tag_id = 0;

    while (getline(inp, current_line))
    {
        istringstream ss(current_line);

        ss >> post_id;
        ss.ignore(1);
        ss >> tag_id;

        post_to_tags[post_id].push_back(tag_id);
        max_tag_id = max(max_tag_id, tag_id);
        tags_with_posts.push_back(make_pair(tag_id, post_id));
    }
    
    ++max_tag_id;

    sort(tags_with_posts.begin(), tags_with_posts.end());
    row_count.resize(max_tag_id);

    size_t sz = tags_with_posts.size();
    for (size_t i = 0; i < sz; i++)
    {
        if (i > 0 and tags_with_posts[i - 1].first != tags_with_posts[i].first)
        {
            // Encountered a new tag.
            print_row(out, tags_with_posts[i - 1].first);
            row_count.clear();
            row_count.resize(max_tag_id);
        }

        post_id = tags_with_posts[i].second;
        tag_id = tags_with_posts[i].first;

        for (auto const& neighbour_tag: post_to_tags[post_id])
        {
            if (neighbour_tag > tag_id)
                ++row_count[neighbour_tag];
        }
    }
    print_row(out, tags_with_posts.back().first);
    return 0;
}