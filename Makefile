# https://www.gnu.org/prep/standards/html_node/Makefile-Basics.html#Makefile-Basics
SHELL = /bin/sh

POST_DATE = 2008-01-01

CPPFLAGS = --std=c++11 -O2 
CPP = g++

SRC = ./src
DATA = ./data
INTERIM = $(DATA)/interim
PROCESSED = $(DATA)/processed
BHTSNE = $(SRC)/models/use_bhtsne
REV_BHTSNE = ../../../

all:
	@printf "Welcome to SOMap makefile!\n"
	@printf "Please, use one of the following commands:\n"
	@printf "\tmake visualize\n"
	@printf "\tmake visualize_example\n"
	@printf "\tmake generate_tiles POST_DATE=YYYY-MM-DD"

$(DATA)/raw/question_tags.csv $(DATA)/raw/questions.csv: $(SRC)/data/make_raw_data.py
	python3 $(SRC)/data/make_raw_data.py


# Obtain raw data.
raw_data: $(DATA)/raw/questions.csv $(DATA)/raw/question_tags.csv 


# Extract only needed information from raw data.
$(INTERIM)/posts.csv $(INTERIM)/tags.csv $(INTERIM)/post_tag.csv: $(DATA)/raw/questions.csv $(DATA)/raw/question_tags.csv $(SRC)/data/prepare_stacklite_data.py
	python3 $(SRC)/data/prepare_stacklite_data.py


# Compile the adjacency matrix computing program.
$(SRC)/data/compute_matrix: $(SRC)/data/compute_matrix.cpp
	$(CPP) -o $@ $(CPPFLAGS) $<

# Compute an adjacency matrix for all tags.
# http://stackoverflow.com/questions/19985936/current-working-directory-of-makefile
$(INTERIM)/adj_matrix_$(POST_DATE).txt $(INTERIM)/post_count_$(POST_DATE).csv: $(SRC)/data/compute_matrix $(INTERIM)/post_tag.csv
	cd $(SRC)/data && ./compute_matrix $(POST_DATE)


# Compute an adjacency matrix for example set of tags.
$(INTERIM)/adj_matrix_example.txt: $(SRC)/data/convert_datastackexchange_query_result.py
	$(SRC)/data/convert_datastackexchange_query_result.py $(DATA)/example/logarithm.csv $@


# Compile the nearest neighbour matrix computing program.
$(BHTSNE)/compute_nearest_neighbours: $(BHTSNE)/compute_nearest_neighbours.cpp
	$(CPP) -o $@ $(CPPFLAGS) $<

# Compute a nearest neighbours matrix with fixed number of neighbours,
# which t-SNE will use. The number of neighbours should be greater than
# 3 * perplexity.
$(INTERIM)/adj_id_to_nn_id_$(POST_DATE).txt $(INTERIM)/nn_matrix_$(POST_DATE).txt: $(BHTSNE)/compute_nearest_neighbours $(INTERIM)/adj_matrix_$(POST_DATE).txt
	$(BHTSNE)/compute_nearest_neighbours $(INTERIM)/adj_matrix_$(POST_DATE).txt 155 $(INTERIM)/adj_id_to_nn_id_$(POST_DATE).txt > $(INTERIM)/nn_matrix_$(POST_DATE).txt
	
$(INTERIM)/adj_id_to_nn_id_example.txt $(INTERIM)/nn_matrix_example.txt: $(BHTSNE)/compute_nearest_neighbours $(INTERIM)/adj_matrix_example.txt
	$(BHTSNE)/compute_nearest_neighbours $(INTERIM)/adj_matrix_example.txt 155 $(INTERIM)/adj_id_to_nn_id_example.txt > $(INTERIM)/nn_matrix_example.txt


# Obtain mapping from id-s to names for tags.
$(PROCESSED)/id_to_additional_info_$(POST_DATE).csv: $(INTERIM)/adj_id_to_nn_id_$(POST_DATE).txt $(BHTSNE)/merge_mappings.py $(INTERIM)/tags.csv $(INTERIM)/post_count_$(POST_DATE).csv
	$(BHTSNE)/merge_mappings.py $< $(INTERIM)/tags.csv $(INTERIM)/post_count_$(POST_DATE).csv > $@
$(PROCESSED)/id_to_additional_info_example.csv: $(INTERIM)/adj_id_to_nn_id_example.txt $(BHTSNE)/merge_mappings.py 
	$(BHTSNE)/merge_mappings.py $< $(DATA)/example/data_stackexchange_tags.csv > $@


# Obtain all data needed for t-SNE run
data: $(DATA)/raw/questions.csv $(DATA)/raw/question_tags.csv $(INTERIM)/nn_matrix_$(POST_DATE).txt $(INTERIM)/id_to_additional_info_$(POST_DATE).txt
data_example: $(INTERIM)/nn_matrix_example.txt $(INTERIM)/id_to_additional_info_example.txt





$(BHTSNE)/nearest_neighbour_bhtsne/bh_tsne: $(BHTSNE)/nearest_neighbour_bhtsne/tsne.cpp $(BHTSNE)/nearest_neighbour_bhtsne/sptree.cpp
	$(CPP) $(CPPFLAGS) -o $@ $^


# Run a rewritten version of `bhtsne` on out nearest neighbour matrix.
$(PROCESSED)/raw_tsne_output_$(POST_DATE).txt: $(BHTSNE)/nearest_neighbour_bhtsne/run.sh $(BHTSNE)/nearest_neighbour_bhtsne/bh_tsne $(INTERIM)/nn_matrix_$(POST_DATE).txt 
	$(BHTSNE)/nearest_neighbour_bhtsne/run.sh $(INTERIM)/nn_matrix_$(POST_DATE).txt > $@
$(PROCESSED)/raw_tsne_output_example.txt: $(BHTSNE)/nearest_neighbour_bhtsne/run.sh $(BHTSNE)/nearest_neighbour_bhtsne/bh_tsne $(INTERIM)/nn_matrix_example.txt
	$(BHTSNE)/nearest_neighbour_bhtsne/run.sh $(INTERIM)/nn_matrix_example.txt > $@


$(SRC)/visualization/tsne_output_$(POST_DATE).tsv: $(PROCESSED)/raw_tsne_output_$(POST_DATE).txt $(BHTSNE)/extract_tsv.py $(PROCESSED)/id_to_additional_info_$(POST_DATE).csv
	python3 $(BHTSNE)/extract_tsv.py $(PROCESSED)/raw_tsne_output_$(POST_DATE).txt > $@
	python3 $(SRC)/visualization/get_tiling.py $@ $(PROCESSED)/id_to_additional_info_$(POST_DATE).csv 7 $(POST_DATE)
$(SRC)/visualization/tsne_output_example.tsv: $(PROCESSED)/raw_tsne_output_example.txt $(BHTSNE)/extract_tsv.py $(PROCESSED)/id_to_additional_info_example.csv
	python3 $(BHTSNE)/extract_tsv.py $(PROCESSED)/raw_tsne_output_example.txt > $(SRC)/visualization/tsne_output_example.tsv
	python3 $(SRC)/visualization/get_tiling.py $(SRC)/visualization/tsne_output_example.tsv $(PROCESSED)/id_to_additional_info_example.csv 7 example


visualize: $(SRC)/visualization/tsne_output_$(POST_DATE).tsv
visualize_example: $(SRC)/visualization/tsne_output_example.tsv


# If we already have all required files, but we've updated tiling
# generation routine OR we obtained those files from somewhere else,
# we need a rule to just regenerate tiles.
generate_tiles:
	python3 $(BHTSNE)/extract_tsv.py $(PROCESSED)/raw_tsne_output_$(POST_DATE).txt > $(SRC)/visualization/tsne_output_$(POST_DATE).tsv
	python3 $(SRC)/visualization/get_tiling.py $(SRC)/visualization/tsne_output_$(POST_DATE).tsv  $(PROCESSED)/id_to_additional_info_$(POST_DATE).csv 7 $(POST_DATE)


# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
# "A phony target should not be a prerequisite of a real target file; if it is, its recipe will be run every time make goes to update that file. As long as a phony target is never a prerequisite of a real target, the phony target recipe will be executed only when the phony target is a specified goal".
.PHONY: all data raw_data data_example visualize visualize_example generate_tiles

.DELETE_ON_ERROR: 
