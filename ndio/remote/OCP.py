import requests
import h5py
import os
import numpy
from cStringIO import StringIO
import zlib
import tempfile

from Remote import Remote
from errors import *
import ndio.ramon as ramon

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"


class OCP(Remote):

    # SECTION:
    # Enumerables

    IMAGE = IMG = 'image'
    ANNOTATION = ANNO = 'annotation'

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(OCP, self).__init__(hostname, protocol)

    def ping(self):
        return super(OCP, self).ping('public_tokens/')

    def url(self, suffix=""):
        return super(OCP, self).url('/ocp/ca/' + suffix)

    # SECTION:
    # Metadata

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
            token (str): Token to return information for

        Returns:
            JSON: representation of proj_info
        """
        r = requests.get(self.url() + "{}/info/".format(token))
        return r.json()

    # SECTION:
    # Data Download

    def get_xy_slice(self, token, channel,
                     x_start, x_stop,
                     y_start, y_stop,
                     z_index,
                     resolution=0):
        """
        Return a binary-encoded, decompressed 2d image. You should
        specify a 'token' and 'channel' pair.  For image data, users
        should use the channel 'image.'

        Arguments:
            token (str): Token to identify data to download
            channel (str): Channel
            resolution (int): Resolution level
            Q_start (int):` The lower bound of dimension 'Q'
            Q_stop (int): The upper bound of dimension 'Q'
            z_index (int): The z-slice to image

        Returns:
            str: binary image data
        """
        im = self._get_cutout_no_chunking(token, channel, resolution,
                                          x_start, x_stop, y_start, y_stop,
                                          z_index, z_index+1)[0]
        return im

    def get_image(self, token, channel,
                  x_start, x_stop,
                  y_start, y_stop,
                  z_index,
                  resolution=0):
        """
        Alias for the `get_xy_slice` function for backwards compatibility.
        """
        return self.get_xy_slice(token, channel,
                                 x_start, x_stop,
                                 y_start, y_stop,
                                 z_index,
                                 resolution)

    def get_volume(self, token, channel,
                   x_start, x_stop,
                   y_start, y_stop,
                   z_start, z_stop,
                   resolution=1,
                   block_size=(256, 256, 16),
                   crop=False):
        """
        Get a RAMONVolume volumetric cutout from the OCP server.

        Arguments:
            token (str): Token to identify data to download
            channel (str): Channel
            resolution (int): Resolution level
            Q_start (int):` The lower bound of dimension 'Q'
            Q_stop (int): The upper bound of dimension 'Q'
            block_size (int[3]): Block size of this dataset
            crop (bool): whether or not to crop the volume before returning it

        Returns:
            ndio.ramon.RAMONVolume: Downloaded data.

        Raises:
            NotImplementedError: If you try to crop... Sorry :(
        """

        size = (x_stop-x_start)*(y_stop-y_start)*(z_stop-z_start)
        volume = ramon.RAMONVolume()
        volume.xyz_offset = [x_start, y_start, z_start]
        volume.resolution = resolution
        volume.cutout = self.get_cutout(token, channel, x_start, x_stop,
                                        y_start, y_stop, z_start, z_stop,
                                        resolution=resolution)
        return volume

    def get_cutout(self, token, channel,
                   x_start, x_stop,
                   y_start, y_stop,
                   z_start, z_stop,
                   resolution=1,
                   block_size=(256, 256, 16),
                   crop=False):
        """
        Get volumetric cutout data from the OCP server.

        Arguments:
            token (str): Token to identify data to download
            channel (str): Channel
            resolution (int): Resolution level
            Q_start (int):` The lower bound of dimension 'Q'
            Q_stop (int): The upper bound of dimension 'Q'
            block_size (int[3]): Block size of this dataset
            crop (bool): whether or not to crop the volume before returning it

        Returns:
            numpy.ndarray: Downloaded data.

        Raises:
            NotImplementedError: If you try to crop... Sorry :(
        """

        if crop is True:
            raise NotImplementedError("Can't handle crops yet, sorry! :(")

        size = (x_stop-x_start)*(y_stop-y_start)*(z_stop-z_start)

        # For now, max out at 1GB
        if size < 1E9:
            return self._get_cutout_no_chunking(token, channel, resolution,
                                                x_start, x_stop,
                                                y_start, y_stop,
                                                z_start, z_stop)

        else:
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
                                                    c[0][0], c[0][1],
                                                    c[1][0], c[1][1],
                                                    c[2][0], c[2][1])))

            x_bounds = snap_to_cube(x_start, x_stop,
                                    chunk_depth=256, q_index=0)
            y_bounds = snap_to_cube(y_start, y_stop,
                                    chunk_depth=256, q_index=0)
            z_bounds = snap_to_cube(z_start, z_stop,
                                    chunk_depth=16,  q_index=1)

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
                            volume[x-x_range[0]][y-y_range[0]][z-z_range[0]] =\
                                chunk[1][zi][xi][yi]
                            zi += 1
                        yi += 1
                    xi += 1
            return volume

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

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(req.content)
            tmpfile.seek(0)
            h5file = h5py.File(tmpfile.name, "r")
            return h5file.get(channel).get('CUTOUT')[:]
        raise IOError("Failed to make tempfile.")

    # SECTION:
    # Data Upload

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

        Arguments:
            token (str)
            channel (str)
            q_start (int)
            q_stop (int)
            data:           A numpy array of data. Pass in (x, y, z)
            resolution:     Default resolution of the data
            roll_axis:      Default True. Pass False if you're supplying data
                            in (z, x, y) order.
            dtype:          Pass in datatype if you know it. Otherwise we'll
                            check the projinfo.
        Returns:
            bool: True on success

        Raises:
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

        req = requests.post(url, data=compressed, headers={
            'Content-Type': 'application/octet-stream'
        })

        if req.status_code is not 200:
            raise RemoteDataUploadError(req.text)
        else:
            return True

    # SECTION:
    # RAMON Download

    def get_ramon_ids(self, token, channel='annotation'):
        """
        Return a list of all IDs available for download from this token and
        channel.

        Arguments:
            token (str): Project to use
            channel (str): Channel to use (default 'annotation')
        Returns:
            int[]: A list of the ids of the returned RAMON objects
        Raises:
            RemoteDataNotFoundError: If the channel or token is not found
        """

        req = requests.get(self.url() + "{}/{}/query/".format(token, channel))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No query results for token {}.'
                                          .format(token))
        else:
            with tempfile.NamedTemporaryFile() as tmpfile:
                tmpfile.write(req.content)
                tmpfile.seek(0)
                h5file = h5py.File(tmpfile.name, "r")
                return [i for i in h5file['ANNOIDS']]
            raise IOError("Could not successfully mock HDF5 file for parsing.")

    def get_ramon(self, token, channel, anno_id, resolution,
                  metadata_only=False):
        """
        Download a RAMON object by ID.

        Arguments:
            token (str): Project to use
            channel (str): The channel to use
            anno_id (int, str): The ID of a RAMON object to gather. Coerced str
            resolution (int): Resolution (if not working, try a higher num)
            metadata_only (bool):  True = returns `get_ramon_metadata` instead

        Returns:
            ndio.ramon.RAMON

        Raises:
            RemoteDataNotFoundError: If the requested anno_id cannot be found.
        """

        metadata = self.get_ramon_metadata(token, channel, anno_id)

        if metadata_only:
            return metadata

        metadata = metadata[str(anno_id)]

        # Download the data itself
        req = requests.get(self.url() +
                           "{}/{}/{}/cutout/{}".format(token, channel,
                                                       anno_id, resolution))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        else:

            with tempfile.NamedTemporaryFile() as tmpfile:
                tmpfile.write(req.content)
                tmpfile.seek(0)
                h5file = h5py.File(tmpfile.name, "r")

                r = ramon.hdf5_to_ramon(h5file)
                return r

    def get_ramon_metadata(self, token, channel, anno_id):
        """
        Download a RAMON object by ID. `anno_id` can be a string `"123"`, an
        int `123`, an array of ints `[123, 234, 345]`, an array of strings
        `["123", "234", "345"]`, or a comma-separated string list
        `"123,234,345"`.

        Arguments:
            token (str): Project to use
            channel (str): The channel to use
            anno_id: An int, a str, or a list of ids to gather

        Returns:
            JSON. If you pass a single id in str or int, returns a single datum
            If you pass a list of int or str or a comma-separated string, will
            return a dict with keys from the list and the values are the JSON
            returned from the server.

        Raises:
            RemoteDataNotFoundError: If the data cannot be found on the Remote
        """

        if type(anno_id) is int:
            # there's just one ID to download
            return self._get_single_ramon_metadata(token, channel,
                                                   str(anno_id))
        elif type(anno_id) is str:
            # either "id" or "id,id,id":
            if (len(anno_id.split(',')) > 1):
                results = {}
                for i in anno_id.split(','):
                    results[i] = self._get_single_ramon_metadata(
                        token, channel, anno_id.strip()
                    )
                return results
            else:
                # "id"
                return self._get_single_ramon_metadata(token, channel,
                                                       anno_id.strip())
        elif type(anno_id) is list:
            # [id, id] or ['id', 'id']
            results = {}
            for i in anno_id:
                results[i] = self._get_single_ramon_metadata(token, channel,
                                                             str(anno_id)
                                                             .strip())
            return results

    def _get_single_ramon_metadata(self, token, channel, anno_id):
        req = requests.get(self.url() +
                           "{}/{}/{}/json/".format(token, channel,
                                                   anno_id))

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        else:
            return req.json()

    # SECTION:
    # RAMON Upload

    def post_ramon(self, token, channel, r):
        """
        Posts a RAMON object to the Remote.

        Arguments:
            token (str): Project to use
            channel (str): The channel to use
            ramon (RAMON): The annotation to upload

        Returns:
            bool: Success = True

        Throws:
            RemoteDataUploadError if something goes wrong
        """

        # First, create the hdf5 file.
        filename = str(r.id) + ".hdf5"
        ramon.ramon_to_hdf5(r)

        with open(filename, 'rb') as hdf5_data:

            req = requests.post(self.url("{}/{}/"
                                .format(token, channel)), headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }, data=hdf5_data)
            if req.status_code is not 200:
                return False
            else:
                return True

    # SECTION:
    # Channels

    def create_channel(self, token, name, channel_type, dtype, readonly):
        """
        Create a new channel on the Remote, using channel_data.

        Arguments:
            token (str): The token the new channel should be added to
            name (str): The name of the channel to add
            type (str): Type of the channel to add (e.g. OCP.IMAGE)
            dtype (str): The datatype of the channel's data (e.g. 'uint8')
            readonly (bool): Can others write to this channel?

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: If your args were bad :(
            RemoteDataUploadError: If the channel data is valid but upload
                fails for some other reason.
        """

        for c in name:
            if not c.isalnum():
                raise ValueError("Name cannot contain character {}.".format(c))

        if channel_type not in ['image', 'annotation']:
            raise ValueError('Type must be OCP.IMAGE or OCP.ANNOTATION.')

        if readonly * 1 not in [0, 1]:
            raise ValueError("readonly must be 0 (False) or 1 (True).")

        # Good job! You supplied very nice arguments.
        req = requests.post(self.url("{}/createChannel/".format(token)), json={
            "channels": {
                name: {
                    "channel_name": name,
                    "channel_type": channel_type,
                    "datatype": dtype,
                    "readonly": readonly * 1
                }
            }
        })

        if req.status_code is not 200:
            raise RemoteDataUploadError('Could not upload {}'.format(req.text))
        else:
            return True

    def delete_channel(self, token, name):
        """
        Delete an existing channel on the Remote. Be careful!

        Arguments:
            token (str): The token the new channel should be deleted from
            name (str): The name of the channel to delete

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            RemoteDataUploadError: If the upload fails for some reason.
        """

        req = requests.post(self.url("{}/deleteChannel/".format(token)), json={
            "channels": [name]
        })

        if req.status_code is not 200:
            raise RemoteDataUploadError('Could not delete {}'.format(req.text))
        else:
            return True
