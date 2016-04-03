import unittest
import ndio.remote.neurodata as neurodata
import ndio.remote.errors
import numpy
import h5py
import os


class TestPropagate(unittest.TestCase):

    def setUp(self):
        self.nd = neurodata(check_tokens=True)

    def test_propagate_status_fails_on_bad_token(self):
        token = 'this is not a token'
        with self.assertRaises(ndio.remote.errors.RemoteDataNotFoundError):
            self.nd.get_propagate_status(token, 'channel')

    def test_kasthuri11_is_propagated(self):
        token = 'kasthuri11'
        self.assertEqual(self.nd.get_propagate_status(token, 'image'), '2')


if __name__ == '__main__':
    unittest.main()
