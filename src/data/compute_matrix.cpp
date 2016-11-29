#include <cassert>
#include <cstring>

#include <iostream>
#include <sstream>
#include <fstream>
#include <string>

#include <unordered_map>
#include <algorithm>
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
 * Input:
 *      1 - date in the form YYYY-MM-DD (e.g. 2008-08-01).
 *          Only posts created later than this date will be considered.
 *
 * Output:
 *      - adjacency matrix
 *      - .csv file with pairs <tag id, number of posts> 
 *
 * Time: less than two minutes.
 *
 * */

namespace
{
    const string post_tag_csv = "../../data/interim/post_tag.csv";
    const string posts_data_csv = "../../data/interim/posts.csv";
    const string matrix_out_file_prefix = "../../data/interim/adj_matrix_";
    const string matrix_out_file_suffix = ".txt";

    const string postcount_prefix = "../../data/interim/post_count_";
    const string postcount_suffix = ".csv";

    vector<int> row_count;
    uint32_t post_count;

    unordered_map<int, vector<int>> post_to_tags;
    vector< pair<int, int> > tags_with_posts;
    unordered_map<int, uint64_t> post_id_to_creation_hash;

    void print_row(ostream& matrix_out, ostream& postcount_out, int row_no)
    {
        matrix_out << row_no << ": ";
        for (size_t i = 0; i < row_count.size(); i++)
        {
            post_count += row_count[i];
            if (row_count[i] > 0)
            {
                matrix_out << i << "," << row_count[i] << " ";
            }
        }

        if (post_count > 0)
        {
            postcount_out << row_no << "," << post_count << endl;
        }

        matrix_out << endl;
    }

    uint64_t get_date_hash(istringstream& ss)
    {
        /*
         * Given a string reader `ss`, which is about
         * to read a date in the form YYYY-MM-DD (e.g. 2008-08-01),
         * return a number representation for this date (so we can
         * compare numbers instead of strings).
         */
        int year, month, day;
        char delim;
        ss >> year >> delim >> month >> delim >> day;
        return static_cast<uint64_t>(year) * 4000 + month * 40 + day;
    }

    void read_posts_data()
    {
        /*
         * Read .csv file with information about posts. 
         *
         * Example:
         *
         *   Id,CreationDate
         *   1,2008-07-31T21:26:37Z
         *   4,2008-07-31T21:42:52Z
         *   6,2008-07-31T22:08:08Z
         *   8,2008-07-31T23:33:19Z
         *   ...
         */
        ifstream post_data(posts_data_csv);
        string current_line;

        getline(post_data, current_line);

        while (getline(post_data, current_line))
        {
            int post_id;
            istringstream ss(current_line);

            ss >> post_id;
            ss.ignore(1);
            uint64_t date_hash = get_date_hash(ss);

            post_id_to_creation_hash[post_id] = date_hash;
        }

    }
} // anon namespace


int main(int argc, char **argv)
{
    uint64_t date_lower_bound_hash = 0;
    istringstream date_reader(argv[1]);
    cout << "Generating an adjacency matrix using posts later than " << argv[1] << endl;
    date_lower_bound_hash = get_date_hash(date_reader);

    ofstream postcount_out(postcount_prefix + string(argv[1]) + postcount_suffix);
    postcount_out << "Id,PostCount" << endl;

    read_posts_data();
    ifstream inp(post_tag_csv);
    ofstream out(matrix_out_file_prefix + string(argv[1]) + matrix_out_file_suffix);
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

        assert (post_id_to_creation_hash.count(post_id));
        if (post_id_to_creation_hash[post_id] <= date_lower_bound_hash)
        {
            // Disregard posts earlier than certain date.
            continue;
        }

        post_to_tags[post_id].push_back(tag_id);
        max_tag_id = max(max_tag_id, tag_id);
        tags_with_posts.push_back(make_pair(tag_id, post_id));
    }
    
    ++max_tag_id;

    sort(tags_with_posts.begin(), tags_with_posts.end());
    row_count.resize(max_tag_id);
    post_count = 0;

    size_t sz = tags_with_posts.size();
    for (size_t i = 0; i < sz; i++)
    {
        if (i > 0 and tags_with_posts[i - 1].first != tags_with_posts[i].first)
        {
            // Encountered a new tag.
            print_row(out, postcount_out, tags_with_posts[i - 1].first);
            row_count.clear();
            row_count.resize(max_tag_id);
            post_count = 0;
        }

        post_id = tags_with_posts[i].second;
        tag_id = tags_with_posts[i].first;

        for (auto const& neighbour_tag: post_to_tags[post_id])
        {
            if (neighbour_tag > tag_id)
                ++row_count[neighbour_tag];
            ++post_count;
        }
    }
    print_row(out, postcount_out, tags_with_posts.back().first);
    return 0;
}
