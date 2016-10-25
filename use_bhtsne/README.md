# Using `bhtsne` implementation

## Introduction
This page tries to shed light on why and how we use t-distributed Stochastic Neighbour Embedding 
(specifically, `bhtsne` implementation).

## History
### SNE
The predecessor of t-SNE is [SNE](http://machinelearning.wustl.edu/mlpapers/paper_files/AA45.pdf),
proposed by Hinton and Roweis. It maps objects described by high-dimensional vectors to a low-dimensional space,
while preserving "similarities" between neighbours. SNE can take pairwise dissimilarities (like distances in euclidean
space, but not limited to symmetric measures) as input.

SNE measures "similarity" between objects by means of [Gaussian distribution](https://en.wikipedia.org/wiki/Gaussian_distribution). Each object has a probability
to choose another object as "neighbour". The probability is proportional to gaussian centered on the first object.
Variance of gaussian is chosen independently for each object in a way that "expects" each object to have only `P` 
significantly close neighbours. `P` is the "perplexity". Gaussian is used both in high- and low-dimensional spaces.

Quality of the embedding is measured by sum of [Kullback–Leibler divergences](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)
between high-dimensional and low-dimensional probability distributions for each point. Authors show
that this measure can be minimized using gradient descent method.

### t-SNE
[t-SNE](https://lvdmaaten.github.io/publications/papers/JMLR_2008.pdf) is a modification of SNE, proposed by van der Maaten
and Hinton. It has the following differences from the original:
 - the KL divergence is is computed only once (per cost function evaluation) for joint probability distributions;
 - [Student-t distribution](https://en.wikipedia.org/wiki/Student%27s_t-distribution) is used in low-dimensional space;
 - some minor tweaks to improve the quality of embeddings.

### t-SNE with optimizations
In 2014, van der Maaten proposed an [optimized version](https://lvdmaaten.github.io/publications/papers/JMLR_2014.pdf) of t-SNE. Its github repo is [bhtsne](https://github.com/lvdmaaten/bhtsne).
It uses two approximation algorithms:
 - similarities for high-dimensional points are sparsely approximated using [Vantage Point Trees](http://stevehanov.ca/blog/index.php?id=130). The main idea is that distant points have low similarity
 anyway - so why bother looking at them? Just get a handful of nearest neighbours, compute similarities with them,
 and treat everything else as zero;
 - gradient evaluation is approximated by Barnes-Hut algorithm. It uses an analogy from physics: gradient
 describes forces of strings between low-dimensional points. Since the output data is 2D, we can use
 quadtree or similar data structure to approximate the joint force of some pack of points to another point.

## Applying `bhtsne` to SOMap problem
In our setting, tags from StackOverflow are connected by questions. They form a rather sparse graph. We use an adjacency matrix of the graph.
It cannot be directly inserted into t-SNE, because: 
 - what we have is really an inverse of distance between points: the higher, the better;
 - distances in the graph do not respect triangle inequality.

However, let's forget about the whole high-dimensional stuff. We can compute similarities between vertices just like
t-SNE itself does: find sufficient number of nearest neighbours and calculate distances. Then plug it into `bhtsne`,
just like some result of euclidean distances computation. I'm positively sure that "similarity", as the concept,
does not depend on triangle inequality, so using our skewed distances is OK.

Since all edge weights are positive, we can run a truncated Dijkstra's algorithm to obtain any number of nearset neighbours
for each vertex. I hope to implement it in something like O(N\*K\*logN) time, where N is the number of vertices, K is the number of nearest
neighbours.
