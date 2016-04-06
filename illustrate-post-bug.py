import ndio.remote.neurodata as nd
import ndio.ramon as ramon

n0 = nd()
n1 = nd(hostname="brainviz1.cs.jhu.edu")

# get ramon from n0:
rr = n0.get_ramon('kasthuri2015_ramon_v4', 'neurons', 3)

n1.post_ramon('test_kasthuri2', 'test', rr)

import pdb; pdb.set_trace()
