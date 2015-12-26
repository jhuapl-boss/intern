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

    def test_build_graph_failures_bad_size(self):
        """
        Fails when the size value is wrong.
        """
        with self.assertRaises(ValueError):
            self.m2g.build_graph("project", "site",
                                 "subject", "session",
                                 "scan", "M")

    def test_build_graph_failures_spaces(self):
        """
        Fails when there's a space in a parameter.
        """
        with self.assertRaises(ValueError):
            self.m2g.build_graph("pro ject", "site",
                                 "subject", "session",
                                 "scan", m2g.SMALL)
        with self.assertRaises(ValueError):
            self.m2g.build_graph("project", "site",
                                 "subject", "ses sion",
                                 "scan", m2g.SMALL)


if __name__ == '__main__':
    unittest.main()
