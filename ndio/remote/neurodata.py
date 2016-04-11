from __future__ import absolute_import
import ndio
import requests
import os
import numpy
from io import BytesIO
import zlib
import tempfile
import blosc
import h5py

from .Remote import Remote
from .errors import *
import ndio.ramon as ramon
from six.moves import range
import six

from functools import wraps

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_SUFFIX = "ocp"
DEFAULT_PROTOCOL = "http"


class neurodata(Remote):

    # SECTION:
    # Enumerables
    IMAGE = IMG = 'image'
    ANNOTATION = ANNO = 'annotation'

    def __init__(self,
                 hostname=DEFAULT_HOSTNAME,
                 protocol=DEFAULT_PROTOCOL,
                 meta_root="http://lims.neurodata.io/",
                 meta_protocol=DEFAULT_PROTOCOL, **kwargs):

        self._check_tokens = kwargs.get('check_tokens', False)
        self._chunk_threshold = kwargs.get('chunk_threshold', 1E9 / 4)
        self._ext = kwargs.get('suffix', DEFAULT_SUFFIX)

        # Prepare meta url
        self.meta_root = meta_root
        if not self.meta_root.endswith('/'):
            self.meta_root = self.meta_root + "/"
        if self.meta_root.startswith('http'):
            self.meta_root = self.meta_root[self.meta_root.index('://')+3:]
        self.meta_protocol = meta_protocol

        super(neurodata, self).__init__(hostname, protocol)

    # SECTION:
    # Decorators
    def _check_token(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            if self._check_tokens:
                if 'token' in kwargs:
                    token = kwargs['token']
                else:
                    token = args[0]
                if self.ping('{}/info/'.format(token)) != 200:
                    raise RemoteDataNotFoundError("Bad token {}".format(token))
            return f(self, *args, **kwargs)
        return wrapped

    # SECTION:
    # Utilities
    def ping(self, suffix='public_tokens/'):
        """
        Returns the status-code of the API (estimated using the public-tokens
        lookup page).

        Arguments:
            suffix (str : 'public_tokens/'): The url endpoint to check

        Returns:
            int: status code
        """
        return super(neurodata, self).ping(suffix)

    def url(self, suffix=""):
        """
        Returns a constructed URL, appending an optional suffix (uri path).

        Arguments:
            suffix (str : ""): The suffix to append to the end of the URL

        Returns:
            str: The complete URL
        """
        return super(neurodata, self).url('{}/ca/'.format(self._ext) + suffix)

    def meta_url(self, suffix=""):
        """
        Returns a constructed URL, appending an optional suffix (uri path),
        for the metadata server. (Should be temporary, until the LIMS shim
        is fixed.)

        Arguments:
            suffix (str : ""): The suffix to append to the end of the URL

        Returns:
            str: The complete URL
        """
        return self.meta_protocol + "://" + self.meta_root + suffix

    def __repr__(self):
        """
        Returns a string representation that can be used to reproduce this
        instance. `eval(repr(this))` should return an identical copy.

        Arguments:
            None

        Returns:
            str: Representation of reproducible instance.
        """
        return "ndio.remote.neurodata('{}', '{}')".format(
            self.hostname,
            self.protocol,
            self.meta_url,
            self.meta_protocol
        )

    # SECTION:
    # Metadata
    def get_public_tokens(self):
        """
        Get a list of public tokens available on this server.

        Arguments:
            None

        Returns:
            str[]: list of public tokens
        """
        r = requests.get(self.url() + "public_tokens/")
        return r.json()

    def get_public_datasets(self):
        """
        NOTE: VERY SLOW!
        Gets a list of public datasets. Different than public tokens!

        Arguments:
            None

        Returns:
            str[]: list of public datasets
        """
        return list(self.get_public_datasets_and_tokens().keys())

    def get_public_datasets_and_tokens(self):
        """
        NOTE: VERY SLOW!
        Gets a dictionary relating key:dataset to value:[tokens] that rely
        on that dataset.

        Arguments:
            None

        Returns:
            dict: relating key:dataset to value:[tokens]
        """
        datasets = {}
        tokens = self.get_public_tokens()
        for t in tokens:
            dataset = self.get_token_dataset(t)
            if dataset in datasets:
                datasets[dataset].append(t)
            else:
                datasets[dataset] = [t]
        return datasets

    @_check_token
    def get_token_dataset(self, token):
        """
        Get the dataset for a given token.

        Arguments:
            token (str): The token to inspect

        Returns:
            str: The name of the dataset
        """
        return self.get_proj_info(token)['dataset']['description']

    @_check_token
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

    @_check_token
    def get_metadata(self, token):
        """
        An alias for get_proj_info.
        """
        return self.get_proj_info(token)

    @_check_token
    def get_channels(self, token):
        """
        Wraps get_proj_info to return a dictionary of just the channels of
        a given project.

        Arguments:
            token (str): Token to return channels for

        Returns:
            JSON: dictionary of channels.
        """
        return self.get_proj_info(token)['channels']

    @_check_token
    def get_image_size(self, token, resolution=0):
        """
        Returns the size of the volume (3D). Convenient for when you want
        to download the entirety of a dataset.

        Arguments:
            token (str): The token for which to find the dataset image bounds
            resolution (int : 0): The resolution at which to get image bounds.
                Defaults to 0, to get the largest area available.

        Returns:
            int[3]: The size of the bounds. Should == get_volume.shape

        Raises:
            RemoteDataNotFoundError: If the token is invalid, or if the
                metadata at that resolution is unavailable in projinfo.
        """
        info = self.get_proj_info(token)
        res = str(resolution)
        if res not in info['dataset']['imagesize']:
            raise RemoteDataNotFoundError("Resolution " + res +
                                          " is not available.")
        return info['dataset']['imagesize'][str(resolution)]

    @_check_token
    def set_metadata(self, token, data):
        """
        Insert new metadata into the OCP metadata database.

        Arguments:
            token (str): Token of the datum to set
            data (str): A dictionary to insert as metadata. Include `secret`.

        Returns:
            json: Info of the inserted ID (convenience) or an error message.

        Throws:
            RemoteDataUploadError: If the token is already populated, or if
                there is an issue with your specified `secret` key.
        """
        req = requests.post(self.meta_url("metadata/ocp/set/" + token),
                            json=data)

        if req.status_code != 200:
            raise RemoteDataUploadError(
                "Could not upload metadata: " + req.json()['message']
            )
        return req.json()

    @_check_token
    def get_subvolumes(self, token):
        """
        Returns a list of subvolumes taken from LIMS, if available.

        Arguments:
            token (str): The token to read from in LIMS

        Returns:
            dict: or None if unavailable
        """
        md = self.get_metadata(token)['metadata']
        if 'subvolumes' in md:
            return md['subvolumes']
        else:
            return None

    @_check_token
    def add_subvolume(self, token, channel, secret,
                      x_start, x_stop,
                      y_start, y_stop,
                      z_start, z_stop,
                      resolution, title, notes):
        """
        Adds a new subvolume to a token/channel.

        Arguments:
            token (str): The token to write to in LIMS
            channel (str): Channel to add in the subvolume. Can be `None`
            Q_start (int): The start of the Q dimension
            Q_stop (int): The top of the Q dimension,
            resolution (int): The resolution at which this subvolume is seen
            title (str): The title to set for the subvolume
            notes (str): Optional extra thoughts on the subvolume

        Returns:
            boolean: success
        """
        md = self.get_metadata(token)['metadata']
        if 'subvolumes' in md:
            subvols = md['subvolumes']
        else:
            subvols = []

        subvols.append({
            'token': token,
            'channel': channel,
            'x_start': x_start,
            'x_stop': x_stop,
            'y_start': y_start,
            'y_stop': y_stop,
            'z_start': z_start,
            'z_stop': z_stop,
            'resolution': resolution,
            'title': title,
            'notes': notes
        })

        return self.set_metadata(token, {
            'secret': secret,
            'subvolumes': subvols
        })

    # SECTION:
    # Data Download
    @_check_token
    def get_block_size(self, token, resolution=None):
        """
        Gets the block-size for a given token at a given resolution.

        Arguments:
            token (str): The token to inspect
            resolution (int : None): The resolution at which to inspect data.
                If none is specified, uses the minimum available.

        Returns:
            int[3]: The xyz blocksize.
        """
        cdims = self.get_metadata(token)['dataset']['cube_dimension']
        if resolution is None:
            resolution = min(cdims.keys())
        return cdims[str(resolution)]

    @_check_token
    def get_image_offset(self, token, resolution=0):
        """
        Gets the image offset for a given token at a given resolution. For
        instance, the `kasthuri11` dataset starts at (0, 0, 1), so its 1850th
        slice is slice 1850, not 1849. When downloading a full dataset, the
        result of this function should be your x/y/z starts.

        Arguments:
            token (str): The token to inspect
            resolution (int : 0): The resolution at which to gather the offset

        Returns:
            int[3]: The origin of the dataset, as a list
        """
        info = self.get_proj_info(token)
        res = str(resolution)
        if res not in info['dataset']['offset']:
            raise RemoteDataNotFoundError("Resolution " + res +
                                          " is not available.")
        return info['dataset']['offset'][str(resolution)]

    @_check_token
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

    @_check_token
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

    @_check_token
    def get_volume(self, token, channel,
                   x_start, x_stop,
                   y_start, y_stop,
                   z_start, z_stop,
                   resolution=1,
                   block_size=None,
                   neariso=False):
        """
        Get a RAMONVolume volumetric cutout from the neurodata server.

        Arguments:
            token (str): Token to identify data to download
            channel (str): Channel
            resolution (int): Resolution level
            Q_start (int): The lower bound of dimension 'Q'
            Q_stop (int): The upper bound of dimension 'Q'
            block_size (int[3]): Block size of this dataset
            neariso (bool : False): Passes the 'neariso' param to the cutout.
                If you don't know what this means, ignore it!

        Returns:
            ndio.ramon.RAMONVolume: Downloaded data.
        """

        size = (x_stop-x_start)*(y_stop-y_start)*(z_stop-z_start)
        volume = ramon.RAMONVolume()
        volume.xyz_offset = [x_start, y_start, z_start]
        volume.resolution = resolution

        volume.cutout = self.get_cutout(token, channel, x_start,
                                        x_stop, y_start, y_stop,
                                        z_start, z_stop,
                                        resolution=resolution,
                                        block_size=block_size,
                                        neariso=neariso)
        return volume

    @_check_token
    def get_cutout(self, token, channel,
                   x_start, x_stop,
                   y_start, y_stop,
                   z_start, z_stop,
                   resolution=1,
                   block_size=None,
                   neariso=False):
        """
        Get volumetric cutout data from the neurodata server.

        Arguments:
            token (str): Token to identify data to download
            channel (str): Channel
            resolution (int): Resolution level
            Q_start (int): The lower bound of dimension 'Q'
            Q_stop (int): The upper bound of dimension 'Q'
            block_size (int[3]): Block size of this dataset. If not provided,
                ndio uses the metadata of this tokenchannel to set. If you find
                that your downloads are timing out or otherwise failing, it may
                be wise to start off by making this smaller.
            neariso (bool : False): Passes the 'neariso' param to the cutout.
                If you don't know what this means, ignore it!

        Returns:
            numpy.ndarray: Downloaded data.
        """

        if block_size is None:
            # look up block size from metadata
            block_size = self.get_block_size(token, resolution)

        origin = self.get_image_offset(token, resolution)

        # Calculate size of the data to be downloaded.
        size = (x_stop - x_start) * (y_stop - y_start) * (z_stop - z_start)

        # Switch which download function to use based on which libraries are
        # available in this version of python.
        if six.PY2:
            dl_func = self._get_cutout_blosc_no_chunking
        elif six.PY3:
            dl_func = self._get_cutout_no_chunking
        else:
            raise ValueError("Invalid Python version.")

        if size < self._chunk_threshold:
            vol = dl_func(token, channel, resolution,
                          x_start, x_stop,
                          y_start, y_stop,
                          z_start, z_stop, neariso=neariso)
            vol = numpy.rollaxis(vol, 1)
            vol = numpy.rollaxis(vol, 2)
            return vol
        else:
            from ndio.utils.parallel import block_compute
            blocks = block_compute(x_start, x_stop,
                                   y_start, y_stop,
                                   z_start, z_stop,
                                   origin, block_size)

            vol = numpy.zeros(((z_stop - z_start),
                              (y_stop - y_start),
                              (x_stop - x_start)))
            for b in blocks:
                data = dl_func(token, channel, resolution,
                               b[0][0], b[0][1],
                               b[1][0], b[1][1],
                               b[2][0], b[2][1], neariso=neariso)

                vol[b[2][0]-z_start: b[2][1]-z_start,
                    b[1][0]-y_start: b[1][1]-y_start,
                    b[0][0]-x_start: b[0][1]-x_start] = data

            vol = numpy.rollaxis(vol, 1)
            vol = numpy.rollaxis(vol, 2)
            return vol

    def _get_cutout_no_chunking(self, token, channel, resolution,
                                x_start, x_stop, y_start, y_stop,
                                z_start, z_stop, neariso=False):
        url = self.url() + "{}/{}/hdf5/{}/{},{}/{},{}/{},{}/".format(
           token, channel, resolution,
           x_start, x_stop,
           y_start, y_stop,
           z_start, z_stop
        )

        if neariso:
            url += "neariso/"

        req = requests.get(url)
        if req.status_code is not 200:
            raise IOError("Bad server response for {}: {}: {}".format(
                          url,
                          req.status_code,
                          req.text))

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(req.content)
            tmpfile.seek(0)
            h5file = h5py.File(tmpfile.name, "r")
            return h5file.get(channel).get('CUTOUT')[:]
        raise IOError("Failed to make tempfile.")

    def _get_cutout_blosc_no_chunking(self, token, channel, resolution,
                                      x_start, x_stop, y_start, y_stop,
                                      z_start, z_stop, neariso=False):

        url = self.url() + "{}/{}/blosc/{}/{},{}/{},{}/{},{}/".format(
           token, channel, resolution,
           x_start, x_stop,
           y_start, y_stop,
           z_start, z_stop
        )

        if neariso:
            url += "neariso/"

        req = requests.get(url)
        if req.status_code is not 200:
            raise IOError("Bad server response for {}: {}: {}".format(
                          url,
                          req.status_code,
                          req.text))

        return blosc.unpack_array(req.content)[0]  # TODO: 4D - 3D array

        raise IOError("Failed to retrieve blosc cutout.")

    # SECTION:
    # Data Upload

    @_check_token
    def post_cutout(self, token, channel,
                    x_start,
                    y_start,
                    z_start,
                    data,
                    dtype='',
                    resolution=0):
        """
        Post a cutout to the server.

        Arguments:
            token (str)
            channel (str)
            x_start (int)
            y_start (int)
            z_start (int)
            data (numpy.ndarray): A numpy array of data. Pass in (x, y, z)
            dtype (str : ''): Pass in explicit datatype, or we use projinfo
            resolution (int : 0): Resolution at which to insert the data

        Returns:
            bool: True on success

        Raises:
            RemoteDataUploadError: if there's an issue during upload.
        """

        datatype = self.get_proj_info(token)['channels'][channel]['datatype']
        if data.dtype.name != datatype:
            data = data.astype(datatype)

        data = numpy.rollaxis(data, 1)
        data = numpy.rollaxis(data, 2)

        if six.PY3 or data.nbytes > 1.5e9:
            ul_func = self._post_cutout_no_chunking_npz
        elif six.PY2:
            ul_func = self._post_cutout_no_chunking_blosc
        else:
            raise OSError("Check yo version of Python!")

        if data.size < self._chunk_threshold:
            return ul_func(token, channel, x_start,
                           y_start, z_start, data,
                           resolution)
        else:
            # must chunk first
            from ndio.utils.parallel import block_compute
            blocks = block_compute(x_start, x_start + data.shape[2],
                                   y_start, y_start + data.shape[1],
                                   z_start, z_start + data.shape[0])

            for b in blocks:
                subvol = data[b[2][0]-z_start: b[2][1]-z_start,
                              b[1][0]-y_start: b[1][1]-y_start,
                              b[0][0]-x_start: b[0][1]-x_start]
                # upload the chunk:
                ul_func(token, channel, x_start,
                        y_start, z_start, subvol,
                        resolution)

        return True

    def _post_cutout_no_chunking_npz(self, token, channel,
                                     x_start, y_start, z_start,
                                     data, resolution):

        data = numpy.expand_dims(data, axis=0)
        tempfile = BytesIO()
        numpy.save(tempfile, data)
        compressed = zlib.compress(tempfile.getvalue())

        url = self.url("{}/{}/npz/{}/{},{}/{},{}/{},{}/".format(
            token, channel,
            resolution,
            x_start, x_start + data.shape[3],
            y_start, y_start + data.shape[2],
            z_start, z_start + data.shape[1]
        ))

        req = requests.post(url, data=compressed, headers={
            'Content-Type': 'application/octet-stream'
        })

        if req.status_code is not 200:
            raise RemoteDataUploadError(req.text)
        else:
            return True

    def _post_cutout_no_chunking_blosc(self, token, channel,
                                       x_start, y_start, z_start,
                                       data, resolution):
        """
        Accepts data in zyx. !!!
        """

        data = numpy.expand_dims(data, axis=0)
        blosc_data = blosc.pack_array(data)

        url = self.url("{}/{}/blosc/{}/{},{}/{},{}/{},{}/".format(
            token, channel,
            resolution,
            x_start, x_start + data.shape[3],
            y_start, y_start + data.shape[2],
            z_start, z_start + data.shape[1]
        ))

        req = requests.post(url, data=blosc_data, headers={
            'Content-Type': 'application/octet-stream'
        })

        if req.status_code is not 200:
            raise RemoteDataUploadError(req.text)
        else:
            return True

    # SECTION:
    # RAMON Download

    @_check_token
    def get_ramon_bounding_box(self, token, channel, r_id, resolution=0):
        """
        Get the bounding box for a RAMON object (specified by ID).

        Arguments:
            token (str): Project to use
            channel (str): Channel to use
            r_id (int): Which ID to get a bounding box
            resolution (int : 0): The resolution at which to download

        Returns:
            (x_start, x_stop, y_start, y_stop, z_start, z_stop): ints
        """
        url = self.url('{}/{}/{}/boundingbox/{}/'.format(token, channel,
                                                         r_id, resolution))

        r_id = str(r_id)
        res = requests.get(url)

        if res.status_code != 200:
            rt = self.get_ramon_metadata(token, channel, r_id)[r_id]['type']
            if rt in ['neuron']:
                raise ValueError("ID {} is of type '{}'".format(r_id, rt))
            raise RemoteDataNotFoundError("No such ID {}".format(r_id))

        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(res.content)
            tmpfile.seek(0)
            h5file = h5py.File(tmpfile.name, "r")
            origin = h5file["{}/XYZOFFSET".format(r_id)][()]
            size = h5file["{}/XYZDIMENSION".format(r_id)][()]
            return (origin[0], origin[0] + size[0],
                    origin[1], origin[1] + size[1],
                    origin[2], origin[2] + size[2])

    @_check_token
    def get_ramon_ids(self, token, channel, ramon_type=None):
        """
        Return a list of all IDs available for download from this token and
        channel.

        Arguments:
            token (str): Project to use
            channel (str): Channel to use
            ramon_type (int : None): Optional. If set, filters IDs and only
                returns those of RAMON objects of the requested type.

        Returns:
            int[]: A list of the ids of the returned RAMON objects

        Raises:
            RemoteDataNotFoundError: If the channel or token is not found
        """

        url = self.url("{}/{}/query/".format(token, channel))
        if ramon_type is not None:
            # User is requesting a specific ramon_type.
            if type(ramon_type) is not int:
                ramon_type = ramon.AnnotationType.get_int(ramon_type)
            url += "type/{}/".format(str(ramon_type))

        req = requests.get(url)

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No query results for token {}.'
                                          .format(token))
        else:
            with tempfile.NamedTemporaryFile() as tmpfile:
                tmpfile.write(req.content)
                tmpfile.seek(0)
                h5file = h5py.File(tmpfile.name, "r")
                if 'ANNOIDS' not in h5file:
                    return []
                return [i for i in h5file['ANNOIDS']]
            raise IOError("Could not successfully mock HDF5 file for parsing.")

    @_check_token
    def get_ramon(self, token, channel, ids, resolution=None,
                  include_cutout=False, sieve=None, batch_size=100):
        """
        Download a RAMON object by ID.

        Arguments:
            token (str): Project to use
            channel (str): The channel to use
            ids (int, str, int[], str[]): The IDs of a RAMON object to gather.
                Can be int (3), string ("3"), int[] ([3, 4, 5]), or string
                (["3", "4", "5"]).
            resolution (int : None): Resolution. Defaults to the most granular
                resolution (0 for now)
            include_cutout (bool : False):  If True, r.cutout is populated
            sieve (function : None): A function that accepts a single ramon
                and returns True or False depending on whether you want that
                ramon object to be included in your response or not.
                For example,
                ```
                def is_even_id(ramon):
                    return ramon.id % 2 == 0
                ```
                You can then pass this to get_ramon like this:
                ```
                ndio.remote.neurodata.get_ramon( . . . , sieve=is_even_id)
                ```
            batch_size (int : 100): The amount of RAMON objects to download at
                a time. If this is greater than 100, we anticipate things going
                very poorly for you. So if you set it <100, ndio will use it.
                If >=100, set it to 100.

        Returns:
            ndio.ramon.RAMON[]: A list of returned RAMON objects.

        Raises:
            RemoteDataNotFoundError: If the requested ids cannot be found.
        """

        b_size = min(100, batch_size)

        mdata = self.get_ramon_metadata(token, channel, ids)

        if resolution is None:
            resolution = 0
            # probably should be dynamic...

        BATCH = False
        _return_first_only = False

        if type(ids) is not list:
            _return_first_only = True
            ids = [ids]
        if type(ids) is list:
            ids = [str(i) for i in ids]
            if len(ids) > b_size:
                BATCH = True
        # now ids is a list of strings

        if BATCH:
            rs = []
            id_batches = [ids[i:i+b_size] for i in xrange(0, len(ids), b_size)]
            for batch in id_batches:
                rs.extend(self._get_ramon_batch(token, channel,
                                                batch, resolution))
        else:
            rs = self._get_ramon_batch(token, channel, ids, resolution)

        if sieve is not None:
            rs = [r for r in rs if sieve(r)]

        if include_cutout:
            for r in rs:
                if 'cutout' not in dir(r):
                    continue
                origin = r.xyz_offset
                # Get the bounding box (cube-aligned)
                bbox = self.get_ramon_bounding_box(token, channel,
                                                   r.id, resolution=resolution)
                # Get the cutout (cube-aligned)
                cutout = self.get_cutout(token, channel,
                                         *bbox, resolution=resolution)
                cutout[cutout != int(r.id)] = 0

                # Compute upper offset and crop
                bounds = numpy.argwhere(cutout)
                mins = [min([i[dim] for i in bounds]) for dim in range(3)]
                maxs = [max([i[dim] for i in bounds]) for dim in range(3)]

                r.cutout = cutout[
                    mins[0]:maxs[0],
                    mins[1]:maxs[1],
                    mins[2]:maxs[2]
                ]

        if _return_first_only:
            return rs[0]
        return rs

    def _get_ramon_batch(self, token, channel, ids, resolution):
        url = self.url("{}/{}/{}/json/".format(token, channel, ",".join(ids)))
        req = requests.get(url)

        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(ids))
        else:
            return ramon.from_json(req.json())

    @_check_token
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

        if type(anno_id) in [int, numpy.uint32]:
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
            results = []
            for i in anno_id:
                results.append(self._get_single_ramon_metadata(token, channel,
                                                               str(i)))
            return results

    def _get_single_ramon_metadata(self, token, channel, anno_id):
        req = requests.get(self.url() +
                           "{}/{}/{}/json/".format(token, channel, anno_id))
        if req.status_code is not 200:
            raise RemoteDataNotFoundError('No data for id {}.'.format(anno_id))
        return req.json()

    @_check_token
    def delete_ramon(self, token, channel, anno):
        """
        Deletes an annotation from the server. Probably you should be careful
        with this function, it seems dangerous.

        Arguments:
            token (str): The token to inspect
            channel (str): The channel to inspect
            anno (int OR list(int) OR RAMON): The annotation to delete. If a
                RAMON object is supplied, the remote annotation will be deleted
                by an ID lookup. If an int is supplied, the annotation will be
                deleted for that ID. If a list of ints are provided, they will
                all be deleted.

        Returns:
            bool: Success
        """
        if type(anno) is int:
            a = anno
        if type(anno) is str:
            a = int(anno)
        if type(anno) is list:
            a = ",".join(anno)
        else:
            a = anno.id

        req = requests.delete(self.url("{}/{}/{}/".format(token, channel, a)))
        if req.status_code is not 200:
            raise RemoteDataNotFoundError("Could not delete id {}: {}"
                                          .format(a, req.text))
        else:
            return True

    @_check_token
    def post_ramon(self, token, channel, r, batch_size=100):
        """
        Posts a RAMON object to the Remote.

        Arguments:
            token (str): Project to use
            channel (str): The channel to use
            r (RAMON or RAMON[]): The annotation(s) to upload
            batch_size (int : 100): The number of RAMONs to post simultaneously
                at maximum in one file. If len(r) > batch_size, the batch will
                be split and uploaded automatically. Must be less than 100.

        Returns:
            bool: Success = True

        Throws:
            RemoteDataUploadError: if something goes wrong
        """

        # Max out batch-size at 100.
        b_size = min(100, batch_size)

        # Coerce incoming IDs to a list.
        if type(r) is not list:
            r = [r]

        # If there are too many to fit in one batch, split here and call this
        # function recursively.
        if len(r) > batch_size:
            batches = [r[i:i+b_size] for i in xrange(0, len(r), b_size)]
            for batch in batches:
                self.post_ramon(token, channel, batch, b_size)
            return

        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            for i in r:
                tmpfile = ramon.to_hdf5(i, tmpfile)

            url = self.url("{}/{}/overwrite/".format(token, channel))
            req = urllib2.Request(url, tmpfile.read())
            res = urllib2.urlopen(req)

            if res.code == 404:
                raise RemoteDataUploadError('[400] Could not upload {}'
                                            .format(str(r)))
            if res.code == 500:
                raise RemoteDataUploadError('[500] Could not upload {}'
                                            .format(str(r)))

            rets = res.read()
            if six.PY3:
                rets = rets.decode()
            return_ids = [int(rid) for rid in rets.split(',')]

            # Now post the cutout separately:
            for ri in r:
                if 'cutout' in dir(ri) and ri.cutout is not None:
                    orig = ri.xyz_offset
                    self.post_cutout(token, channel,
                                     orig[0], orig[1], orig[2],
                                     ri.cutout, resolution=r.resolution)
            return return_ids
        return True

    # SECTION:
    # ID Manipulation

    @_check_token
    def reserve_ids(self, token, channel, quantity):
        """
        Requests a list of next-available-IDs from the server.

        Arguments:
            quantity (int): The number of IDs to reserve

        Returns:
            int[quantity]: List of IDs you've been granted
        """
        quantity = str(quantity)
        url = self.url("{}/{}/reserve/{}/".format(token, channel, quantity))
        req = requests.get(url)
        if req.status_code is not 200:
            raise RemoteDataNotFoundError('Invalid req: ' + req.status_code)
        out = req.json()
        return [out[0] + i for i in range(out[1])]

    @_check_token
    def merge_ids(self, token, channel, ids, delete=False):
        """
        Call the restful endpoint to merge two RAMON objects into one.

        Arguments:
            token (str): The token to inspect
            channel (str): The channel to inspect
            ids (int[]): the list of the IDs to merge
            delete (bool : False): Whether to delete after merging.

        Returns:
            json: The ID as returned by ndstore
        """
        req = requests.get(self.url() + "/merge/{}/"
                           .format(','.join([str(i) for i in ids])))
        if req.status_code is not 200:
            raise RemoteDataUploadError('Could not merge ids {}'.format(
                                        ','.join([str(i) for i in ids])))
        if delete:
            self.delete_ramon(token, channel, ids[1:])
        return True

    # SECTION:
    # Channels

    @_check_token
    def create_channel(self, token, name, channel_type, dtype, readonly):
        """
        Create a new channel on the Remote, using channel_data.

        Arguments:
            token (str): The token the new channel should be added to
            name (str): The name of the channel to add
            type (str): Type of the channel to add (e.g. `neurodata.IMAGE`)
            dtype (str): The datatype of the channel's data (e.g. `uint8`)
            readonly (bool): Can others write to this channel?

        Returns:
            bool: `True` if successful, `False` otherwise.

        Raises:
            ValueError: If your args were bad :(
            RemoteDataUploadError: If the channel data is valid but upload
                fails for some other reason.
        """

        for c in name:
            if not c.isalnum():
                raise ValueError("Name cannot contain character {}.".format(c))

        if channel_type not in ['image', 'annotation']:
            raise ValueError('Channel type must be ' +
                             'neurodata.IMAGE or neurodata.ANNOTATION.')

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

    @_check_token
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
        return True

    # Propagation

    @_check_token
    def propagate(self, token, channel):
        if self.get_propagate_status(token, channel) is not 0:
            return
        url = self.url('{}/{}/setPropagate/1/'.format(token, channel))
        req = requests.get(url)
        if req.status_code is not 200:
            raise RemoteDataUploadError('Propagate fail: {}'.format(req.text))
        return True

    @_check_token
    def get_propagate_status(self, token, channel):
        url = self.url('{}/{}/getPropagate/'.format(token, channel))
        req = requests.get(url)
        if req.status_code is not 200:
            raise ValueError('Bad pair: {}/{}'.format(token, channel))
        return req.text
