# Applying `graph2vec` to SOMap problem

There is a proof-of-concept [graph2vec](http://allentran.github.io/graph2vec) tool by Allen Tran. It attempts to 
represent every vertex in a given graph as a point in multidimensional space.

This feature can be useful for our problem. We can convert our tag graph into points, and feed them into t-SNE.

In order to do that, some changes are required. Specifically, the tool was written for Python2, while we are using Python3. 
Moreover, we need to convert the graph from adjacency matrix to adjacency list, and to understand the output format of the tool.

This is a "plan b" solution, but it would be interesting to compare results of different methods.
