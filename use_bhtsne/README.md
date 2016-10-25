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

SNE measures "similarity" between objects by means of Gaussian distribution. Each object has a probability
to choose another object as "neighbour". The probability is proportional to gaussian centered on the first object.
Variance of gaussian is chosen independently for each object in a way that "expects" each object to have only `P` 
significantly close neighbours. `P` is the "perplexity". Gaussian is used both in high- and low-dimensional spaces.

Quality of the embedding is measured by [Kullback–Leibler divergence](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence)
between high-dimensional and low-dimensional probability distributions.

### t-SNE
