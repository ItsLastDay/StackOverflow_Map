#!/bin/bash 

# Run t-SNE on input adjacency matrix.

#1 = path to adjacency matrix
#2 = path to mapping from id in matrix to tag name (.csv)

full_path_adj_mat="$(readlink -f "$1")"
full_path_mapping="$(readlink -f "$2")"

conv_map_file=$(mktemp)
id_to_tag_file="${full_path_adj_mat}_id_to_tag"
path_to_neighbours_matrix="${full_path_adj_mat}_neighbours"

./compute_neighbours.sh "$full_path_adj_mat" 155 "$conv_map_file" > "$path_to_neighbours_matrix" || exit 1
./merge_mappings.py "$conv_map_file" "$full_path_mapping" > "$id_to_tag_file" || exit 1

cd ./nearest_neighbour_bhtsne
./run.sh "$path_to_neighbours_matrix" "$id_to_tag_file"
