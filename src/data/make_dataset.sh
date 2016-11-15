#!/usr/bin/bash

# Get raw data from `StackLite` repository.

echo "Getting raw tag data from StackLite repo..."

cd ../../data/raw
echo "Downloading question_tags.csv.gz..."
wget -O ./question_tags.csv.gz "https://github.com/dgrtwo/StackLite/blob/master/question_tags.csv.gz" || exit 1

echo "Downloading questions.csv.gz..."
wget -O ./questions.csv.gz "https://github.com/dgrtwo/StackLite/blob/master/questions.csv.gz" || exit 1

echo "Unpacking raw data files..."
gunzip --keep ./question_tags.csv.gz
gunzip --keep ./questions.csv.gz

echo "Successfully obtained raw data"

