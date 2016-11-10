# StackOverflow Map

This is a project for creating 2D visualization of [StackOverflow](http://stackoverflow.com/)
tags using [t-SNE](https://lvdmaaten.github.io/tsne/) 
algorithm.

Everything is written in Python 3.5 and C++.

## The problem
Consider all tags from StackOverflow: `Java`, `C#`, `multiprocessing`, etc. Let's build a graph,
where each vertex is a tag. Edges are represented by questions: each question connects
all pairs of tags that are assigned to the question. Let's say that  
`w(tag_1, tag_2) = number of edges connecting tag_1 and tag_2`  
The more `w(t1,t2)` is, the better - tags are "similar" in that sense.

Given such structure, plot all tags on a 2D map using t-SNE algorithm.

### Steps required to solve the problem
 - Obtain data about StackOverflow tags;
 - create an adjacency matrix `w[i][j]` with weights between tags;
 - feed the matrix to one of t-SNE implementations;
 - plot the result nicely.
 
### Difficulties
 - There are around 50k tags on SO, and more than 10M questions;
 - gathering the latest data from SO is not straightforward;
 - t-SNE does not work with graphs out-of-the-box;
 - the whole thing must run in less than 24 hours (i.e. plotting a single dump).

### Authors
Mikhail Koltsov ([ItsLastDay](https://github.com/ItsLastDay))  
Arkady Kalakutsky ([testlnord](https://github.com/testlnord))
