# https://www.gnu.org/prep/standards/html_node/Makefile-Basics.html#Makefile-Basics
SHELL = /bin/sh

SRC = ./src
DATA = ./data

# Obtain raw data.
data: $(DATA)/questions.csv $(DATA)/question_tags.csv $(SRC)/data/make_dataset.py
	python3 $(SRC)/data/make_dataset.py

.PHONY: data
