import requests
import h5py
import os
import numpy
from cStringIO import StringIO
import zlib
import tempfile

from Remote import Remote

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"


class OCP(Remote):
    def __init__(self,
            hostname=DEFAULT_HOSTNAME,
            protocol=DEFAULT_PROTOCOL):
        """
        Arguments:
            `hostname`:     `str : ndio.remote.OCP.DEFAULT_HOSTNAME`
            `protocol`:     `str : ndio.remote.OCP.DEFAULT_PROTOCOL`
        """
        self.protocol = protocol
        self.hostname = hostname


    def url(self):
        """
        Get the base URL of the Remote.

        Arguments:
            None
        Returns:
            `str` base URL
        """
        return self.protocol + "://" + self.hostname + "/ocp/ca/"


    def ping(self):
        """
        Ping the server to make sure that you can access the base URL.

        Arguments:
            None
        Returns:
            `boolean` Successful access of server (or status code)
        """
        r = requests.get(self.url() + "public_tokens/")
        return r.status_code


    def get_public_tokens(self):
        """
        Get a list of public tokens available on this server.

        Arguments:
            None
        Returns:
            `str[]` list of public tokens
        """
        r = requests.get(self.url() + "public_tokens/")
        return r.json()


    def get_proj_info(self, token):
        """
        Returns the project info for a given token.

        Arguments:
            `token`:        `str` Token to return information for
        Returns:
            JSON representation of proj_info
        """
        r = requests.get(self.url() + "{}/info/".format(token))
        return r.json()


    def get_image(self, token,
                  x_start, x_stop,
                  y_start, y_stop,
                  z_index, resolution=1):
        """
        Return a binary-encoded, decompressed image. You should probably
        check to see that your token has an `image` channel before running this,
        or it won't do anything interesting.

        Arguments:
            :token:                 ``string`` Token to identify data to download
            :Q_start:               ``int`` The lower bound of dimension 'Q'
            :Q_stop:                ``int`` The upper bound of dimension 'Q'
            :z_index:               ``int`` The layer of data to return (1D)
            :resolution:            ``int : 1`` Resolution level
        Returns:
            :``str`` binary image data:
        """
        r = requests.get(self.url() +
            "{}/image/xy/{}/{},{}/{},{}/{}/".format(token, resolution,
            x_start, x_stop,
            y_start, y_stop,
            z_index))
        if r.status_code == 200:
            return r.content
        else:
            return r.status_code


    def get_cutout(self, token, channel,
                 x_start, x_stop,
                 y_start, y_stop,
                 z_start, z_stop,
                 resolution=1,
                 block_size=(256, 256, 16),
                 crop=False):
        """
        Get data from the OCP server.

        Arguments:
            :token:                 ``string`` Token to identify data to download
            :channel:               ``string`` Channel
            :resolution:            ``int : 1`` Resolution level
            :Q_start:               ``int`` The lower bound of dimension 'Q'
            :Q_stop:                ``int`` The upper bound of dimension 'Q'
            :block_size:            ``int(3)`` Block size of this dataset
            :crop:                  ``boolean : True`` whether or not to crop
                                    the volume before returning it

        Returns:
            :``numpy.ndarray``: Downloaded data.
        """

        # Get an array-of-tuples of blocks to request.
        from ndio.utils.parallel import block_compute, snap_to_cube
        small_chunks = block_compute(x_start, x_stop,
                                     y_start, y_stop,
                                     z_start, z_stop)

        # Each time we download a chunk, we'll store it in
        # this, in the format (block_origin, data)
        downloaded_chunks = []
        for c in small_chunks:
            downloaded_chunks.append((
                c, self._get_cutout_no_chunking(token, channel, resolution,
                        c[0][0], c[0][1], c[1][0], c[1][1], c[2][0], c[2][1])))

        x_bounds = snap_to_cube(x_start, x_stop, chunk_depth=256, q_index=0)
        y_bounds = snap_to_cube(y_start, y_stop, chunk_depth=256, q_index=0)
        z_bounds = snap_to_cube(z_start, z_stop, chunk_depth=16,  q_index=1)

        volume = numpy.zeros((x_bounds[1], y_bounds[1], z_bounds[1]-1))


        # TODO: Optimize.
        for chunk in downloaded_chunks:
            x_range, y_range, z_range = chunk[0]
            xi = 0
            for x in range(x_range[0], x_range[1]):
                yi = 0
                for y in range(y_range[0], y_range[1]):
                    zi = 0
                    for z in range(z_range[0], z_range[1]):
                        volume[x][y][z] = chunk[1][zi][xi][yi]
                        # for using format = npz
                        # volume[x][y][z] = chunk[1][0][zi][xi][yi]
                        zi += 1
                    yi += 1
                xi += 1

        if crop == False:
            return volume
        else:
            raise NotImplementedError("Can't handle crops yet, sorry! :(")
            # we have to go get the bounds, subtract what they asked for,
            # and then return a sub-volume.
            x_start_trim = x_start - x_bounds[0]
            y_start_trim = y_start - y_bounds[0]
            z_start_trim = z_start - z_bounds[0]



    def _get_cutout_no_chunking(self, token, channel, resolution,
                                x_start, x_stop, y_start, y_stop,
                                z_start, z_stop):
        req = requests.get(self.url() +
                "{}/{}/hdf5/{}/{},{}/{},{}/{},{}/".format(
                    token, channel, resolution,
                    x_start, x_stop,
                    y_start, y_stop,
                    z_start, z_stop
                ))
        if req.status_code is not 200:
            raise IOError("Bad server response: {}".format(req.status_code))

        with tempfile.NamedTemporaryFile () as tmpfile:
            tmpfile.write(req.content)
            tmpfile.seek(0)
            h5file = h5py.File(tmpfile.name, "r")
            return h5file.get(channel).get('CUTOUT')[:]
        raise IOError("Failed to make tempfile.")

        # For using format = npz
        # decompressed = zlib.decompress(req.content)
        # s = StringIO(decompressed)
        # return numpy.load(s)
