import unittest
import ndio.remote.m2g as m2g
from ndio.remote.errors import *
import ndio.ramon
import numpy


class TestRemoteM2g(unittest.TestCase):

    def setUp(self):
        self.m2g = m2g()

    def test_ping(self):
        self.assertEqual(self.m2g.ping(), 200)

    def test_build_graph_failures(self):
        with self.assertRaises(ValueError):
            self.m2g.build_graph("project", "site",
                                 "subject", "session",
                                 "scan", "M")


if __name__ == '__main__':
    unittest.main()
