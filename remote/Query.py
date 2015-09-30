#
#
# class Query(object):
#
#     def __init__(self, source):
#         """
#         Initialize a new query, using either a URL, in
#         which case it starts with http*, or read in from
#         a local JSON file, in which case it doesn't.
#
#         Arguments:
#             source:         `string` JSON filename or URL
#
#         Returns:
#             None
#         """
#         if source.startswith('http'):
#             # this is a URL, let's parse it.
#             from_url(self, source)
#         else:
#             # this is a JSON file, let's read it in.
#             from_json_file(self, source)
#
#
#     def from_url(self, source):
#         """
#         Set this Query's parameters using a URL.
#
#         Arguments:
#             source:         `string` URL string
#
#         Returns:
#             None
#         """
#         # (string: server_name)/ocp/ca/(string: token_name)/(string: channel_name)/hdf5/(int: resolution)/(int: min_x),(int: max_x)/(int: min_y),(int: max_y)/(int: min_z),(int: max_z)/(int: min_time),(int: max_time)/
#         # post hdf5
#         (string: server_name)/ocp/ca/(string: token_name)/(string: channel_name)/hdf5/(int: resolution)/(int: min_x),(int: max_x)/(int: min_y),(int: max_y)/(int: min_z),(int: max_z)/(int: min_time),(int: max_time)/
#
#     def to_url(self):
#         pass
#
#     def from_json_file(self):
#         pass
#
#     def to_json_file(self):
#         pass
