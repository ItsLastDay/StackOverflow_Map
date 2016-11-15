# https://www.gnu.org/prep/standards/html_node/Makefile-Basics.html#Makefile-Basics
SHELL = /bin/sh

SRC = ./src
DATA = ./data

all:
	@printf "Welcome to SOMap makefile!\n"
	@printf "Please, use one of the following commands:\n"
	@printf "\tmake data\n"

$(DATA)/raw/questions.csv: $(SRC)/data/make_dataset.py
	python3 $(SRC)/data/make_dataset.py
$(DATA)/raw/question_tags.csv: $(SRC)/data/make_dataset.py
	python3 $(SRC)/data/make_dataset.py

# Obtain raw data.
data: $(DATA)/raw/questions.csv $(DATA)/raw/question_tags.csv 




.PHONY: data all
