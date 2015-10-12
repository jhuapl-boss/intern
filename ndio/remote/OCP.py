import requests
import h5py
import os
import numpy
from cStringIO import StringIO
import zlib
import tempfile

from Remote import Remote
from errors import *

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"


class OCP(Remote):

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(OCP, self).__init__(hostname, protocol)


    def ping(self):
        return super(OCP, self).ping('public_tokens/')

    def url(self):
        return super(OCP, self).url('/ocp/ca/')


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

        volume = numpy.zeros((
                x_bounds[1]-x_bounds[0],
                y_bounds[1]-y_bounds[0],
                z_bounds[1]-z_bounds[0]))


        # TODO: Optimize.
        for chunk in downloaded_chunks:
            x_range, y_range, z_range = chunk[0]
            xi = 0
            for x in range(x_range[0], x_range[1]):
                yi = 0
                for y in range(y_range[0], y_range[1]):
                    zi = 0
                    for z in range(z_range[0], z_range[1]):
                        volume[x-x_range[0]][y-y_range[0]][z-z_range[0]] = chunk[1][zi][xi][yi]
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



    def post_cutout(self, token, channel,
                    x_start, x_stop,
                    y_start, y_stop,
                    z_start, z_stop,
                    data,
                    dtype='',
                    resolution=0,
                    roll_axis=True):
        """
        Post a cutout to the server.

        Arguemnts:
            token
            channel
            q_start
            q_stop
            data:           A numpy array of data. Pass in (x, y, z)
            resolution:     Default resolution of the data
            roll_axis:      Default True. Pass False if you're supplying data in
                            (z, x, y) order.
            dtype:          Pass in datatype if you know it. Otherwise we'll
                            check the projinfo.
        Returns:
            True on success

        Throws:
            RemoteDataUploadError if there's an issue during upload.
        """

        datatype = self.get_proj_info(token)['channels'][channel]['datatype']
        if data.dtype.name != datatype:
            data = data.astype(datatype)

        if roll_axis:
            # put the z-axis first
            data = numpy.rollaxis(data, 2)

        data = numpy.expand_dims(data, axis=0)
        tempfile = StringIO()
        numpy.save(tempfile, data)

        compressed = zlib.compress(tempfile.getvalue())

        url = self.url() + "{}/{}/npz/{}/{},{}/{},{}/{},{}/".format(
            token, channel,
            resolution,
            x_start, x_stop,
            y_start, y_stop,
            z_start, z_stop
        )

        req = requests.post(url, data=compressed, headers={'Content-Type': 'application/octet-stream'})

        if req.status_code is not 200:
            raise RemoteDataUploadError(req.text, req.status_code)
        else:
            return True


    def get_ramon(self, token, channel, anno_id, opts="", resolution=1,
                  metadata_only=False):
        """
        Download a RAMON object by ID.

        Arguments:
            token:          Project to use
            channel:        The channel to use
            id:             The ID of a RAMON object to gather
            opts:           String options (ignored)
            resolution:     The scale to return (defaults to 1)
            metadata_only:  Defers to `get_ramon_metadata` instead
        Returns:
            ndio.ramon.RAMON
        Throws:
            RemoteDataNotFoundError
        """

        if metadata_only:
            return self.get_ramon_metadata(token, channel, anno_id)

        req = requests.get(self.url() +
                "{}/{}/{}/{}/{}/".format(token, channel,
                anno_id, opts, resolution))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        else:
            return True



    def get_ramon_metadata(self, token, channel, anno_id):
        """
        Download a RAMON object by ID.

        Arguments:
            token:      Project to use
            channel:    The channel to use
            anno_id:    An int, a str, or a list of ids to gather
        Returns:
            JSON. If you pass a single id in str or int, returns a single datum.
            If you pass a list of int or str or a comma-separated string, will
            return a dict with keys from the list and the values are the server-
            returned JSON.
        Throws:
            RemoteDataNotFoundError
        """

        if type(anno_id) is int:
            # there's just one ID to download
            return _get_single_ramon_metadata(token, channel, str(anno_id))
        elif type(anno_id) is str:
            # either "id" or "id,id,id":
            if (len(anno_id.split(',')) > 1):
                results = {}
                for i in anno_id.split(','):
                    results[i] = _get_single_ramon_metadata(token, channel,
                                                            anno_id.strip())
                return results
            else:
                # "id"
                return _get_single_ramon_metadata(token, channel, anno_id.strip())
        elif type(anno_id) is list:
            # [id, id] or ['id', 'id']
            results = {}
            for i in anno_id:
                results[i] = _get_single_ramon_metadata(token, channel,
                                                        str(anno_id).strip())
            return results



    def _get_single_ramon_metadata(self, token, channel, anno_id):
        req = requests.get(self.url() +
                "{}/{}/{}/json/".format(token, channel,
                anno_id))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        else:
            return req.json()


    def post_ramon(self, token, channel, ramon, opts=""):
        """
        Download a RAMON object by ID.

        Arguments:
            token:      Project to use
            channel:    The channel to use
            ramon:      A ndio.ramon.RAMON object
            opts:       String options (ignored)
        Returns:
            ndio.ramon.RAMON
        Throws:
            RemoteDataNotFoundError
        """

        req = requests.get(self.url() +
                "{}/{}/{}/".format(token, channel, opts))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        else:
            return True
