#!/usr/bin/env python3

'''
Try to apply graph2vec to our adjacency matrix.


Requires: graph2vec, numpy, theano

After installing graph2vec via pip, I needed
to modify files (to run on Python3.5):

/usr/local/lib/python3.5/dist-packages/graph2vec/trainer.py:
    from .node_vectors import NodeVectorModel
    from . import parser
    ...
    substitue `xrange` with `range`.

/usr/local/lib/python3.5/dist-packages/graph2vec/node_vectors.py 
    import pickle as cPickle

/usr/local/lib/python3.5/dist-packages/graph2vec/parser.py
    def _get_connected_nodes(xxx, current_depth=1):
        node_idx, adjancency_list, max_degree = xxx
    ...
    degree = float(parsed_line[2])
    ...
    substitute `iteritems` with `items` in two places.

Also, https://github.com/allentran/graph2vec/issues/3 suggests,
that one needs to create two nonempty files: from_to.mat and inverse_degrees.mat.
'''

from graph2vec.trainer import *

gv = Graph2Vec(vector_dimensions=128, output_dir='./gv_data')
gv.parse_graph('./edge.data', extend_paths=2, data_dir='./gv_data', 
        load_edges=False)

gv.fit(batch_size=1000, max_epochs=1000)

# I'm not sure what `origin and destination nodes` mean,
# but let's output Wout and see what happens.
for line in gv.model.Wout.get_value():
    print(' '.join(map(str, line)))

