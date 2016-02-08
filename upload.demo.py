import ndio.remote.neurodata as ND

nd = ND()

r = nd.get_ramon('kasthuri2015_ramon_v1', 'neurons', 3, resolution=3)

r.id = 4009
#nd.delete_ramon('ndio_demos', 'ramontests', r)
nd.post_ramon('ndio_demos', 'ramontests', r)

nd.get_ramon('ndio_demos', 'ramontests', r.id, resolution=3)
