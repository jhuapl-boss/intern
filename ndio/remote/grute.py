from __future__ import absolute_import

try:
    # For Python 3:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import zipfile
import tempfile
import inspect
import threading
import os

from .Remote import Remote
from .errors import *
import ndio.ramon as ramon

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"
DEFAULT_EMAIL = ""
DEFAULT_FIBER_FILE = "fiber.dat"


class Invariants:
    """
    An array of invariant enumerables.
    """

    SCAN_STATISTIC = ss1 = "ss1"        # the Scan Statistic 1
    TRIANGLE_COUNT = tri = "tri"        # the Triangle Count
    CLUSTERING = cc = "cc"              # the Clustering Coefficient
    MAX_AVG_DEGREE = mad = "mad"        # the Maximum Average Degree
    LOCAL_DEGREE = deg = "deg"          # The Local Degree Count
    EIGENS = eig = "eig"                # top 100 or max avail eigvecs, eigvals

    ALL = [
        SCAN_STATISTIC,
        TRIANGLE_COUNT,
        CLUSTERING,
        MAX_AVG_DEGREE,
        LOCAL_DEGREE,
        EIGENS
    ]


class GraphFormats:
    """
    The set of graph format enumerables.
    """

    GRAPHML = graphml = "graphml"
    NCOL = ncol = "ncol"
    EDGELIST = edgelist = "edgelist"
    LGL = lgl = "lgl"
    PAJEK = pajek = "pajek"
    GRAPHDB = graphdb = "graphdb"
    NUMPY = numpy = "numpy"
    MAT = mat = "mat"

    _any = [
        GRAPHML,
        NCOL,
        EDGELIST,
        LGL,
        PAJEK,
        GRAPHDB,
        NUMPY,
        MAT
    ]


class grute(Remote):
    """
    The grute remote, for interfacing with ndgrutedb (NeuroData.io)
    """

    SMALL = S = 's'
    BIG = B = 'b'

    def __init__(self,
                 hostname=DEFAULT_HOSTNAME,
                 protocol=DEFAULT_PROTOCOL,
                 email=DEFAULT_EMAIL):
        """
        Initialize a new grute remote.

        Arguments:
            hostname (str: "openconnecto.me"): The hostname where grute lives
            protocol (str: "http"): The protocol over which to access grute
            email (str: ""): The email to which completion notifications should
                be sent (unless overridden in individual calls). Note that the
                completion URLs are also accessible via this Python API.
        """
        super(grute, self).__init__(hostname, protocol)
        self.email = email

    def __repr__(self):
        """
        Returns a string representation that can be used to reproduce this
        instance. `eval(repr(this))` should return an identical copy.

        Arguments:
            None

        Returns:
            str: Representation of reproducible instance.
        """
        return "ndio.remote.grute('{}', '{}', '{}')".format(
            self.hostname,
            self.protocol,
            self.email
        )

    def ping(self):
        """
        Check the server for proof of life.
        """
        return super(grute, self).ping()

    def url(self, suffix=""):
        """
        Construct a valid URL from the base grutedb url.

        Arguments:
            suffix (str: ""): The suffix that should be appended to the base

        Returns:
            str: Fully formed absolute URL
        """
        return super(grute, self).url('/graph-services/' + suffix)

    def set_default_email(self, email):
        """
        Sets the default email to use for notifications if none is specified.
        Does only basic error-checking.

        Arguments:
            email (str): The email to notify for all server graph services.

        Returns:
            None

        Raises:
            ValueError: If an invalid email is supplied.
        """
        if "@" not in email:
            raise ValueError("Invalid email.")
        self.email = email

    def build_graph(self, project, site, subject, session, scan,
                    size, email=None, invariants=Invariants.ALL,
                    fiber_file=DEFAULT_FIBER_FILE, atlas_file=None,
                    use_threads=False, callback=None):
        """
        Builds a graph using the graph-services endpoint.

        Arguments:
            project (str): The project to use
            site (str): The site in question
            subject (str): The subject's identifier
            session (str): The session (per subject)
            scan (str): The scan identifier
            size (str): Whether to return a big (grute.BIG) or small
                (grute.SMALL) graph. For a better explanation, see m2g.io.
            email (str : self.email)*: An email to notify
            invariants (str[]: Invariants.ALL)*: An array of invariants to
                compute. You can use the grute.Invariants class to construct a
                list, or simply pass grute.Invariants.ALL to compute them all.
            fiber_file (str: DEFAULT_FIBER_FILE)*: A local filename of an
                MRI Studio .dat file
            atlas_file (str: None)*: A local atlas file, in NIFTI .nii format.
                If none is specified, the Desikan atlas is used by default.
            use_threads (bool: False)*: Whether to run the download in a Python
                thread. If set to True, the call to `build_graph` will end
                quickly, and the `callback` will be called with the returned
                status-code of the restful call as its only argument.
            callback (function: None)*: The function to run upon completion of
                the call, if using threads. (Will not be called if use_threads
                is set to False.)

        Returns:
            HTTP Response if use_threads is False. Otherwise, None

        Raises:
            ValueError: When the supplied values are invalid (contain invalid
                characters, bad email address supplied, etc.)
            RemoteDataNotFoundError: When the data cannot be processed due to
                a server error.
        """
        if email is None:
            email = self.email

        if not set(invariants) <= set(Invariants.ALL):
            raise ValueError("Invariants must be a subset of Invariants.ALL.")

        if use_threads and callback is not None:
            if not hasattr(callback, '__call__'):
                raise ValueError("callback must be a function.")
            if len(inspect.getargspec(callback).args) != 1:
                raise ValueError("callback must take exactly 1 argument.")

        # Once we get here, we know the callback is
        if size not in [self.BIG, self.SMALL]:
            raise ValueError("size must be either grute.BIG or grute.SMALL.")

        url = "buildgraph/{}/{}/{}/{}/{}/{}/{}/{}/".format(
            project,
            site,
            subject,
            session,
            scan,
            size,
            email,
            "/".join(invariants)
        )

        if " " in url:
            raise ValueError("Arguments must not contain spaces.")

        if use_threads:
            # Run in the background.
            download_thread = threading.Thread(
                target=self._run_build_graph,
                args=[url, fiber_file, atlas_file, callback]
            )
            download_thread.start()
        else:
            # Run in the foreground.
            return self._run_build_graph(url, fiber_file, atlas_file)
        return

    def _run_build_graph(self, url,
                         fiber_file, atlas_file=None, callback=None):

        try:
            tmpfile = tempfile.NamedTemporaryFile()
            zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)
            zfile.write(file_file)
            if atlas_file:
                zfile.write(atlas_file)
                zfile.close()
                tmpfile.flush()
                tmpfile.seek(0)
        except:
            raise ValueError("Invalid atlas or fiber file. I don't have " +
                             "any more information than that, sorry!")

        try:
            req = urllib2.Request(self.url(url), tmpfile.read())
            response = urllib2.urlopen(req)

            if callback is not None:
                callback(response)
            else:
                return response.read()
        except:
            raise RemoteDataUploadError("Failed to upload data at " + url)

    def compute_invariants(self, graph_file, input_format,
                           invariants=Invariants.ALL, email=None,
                           use_threads=False, callback=None):
        """
        Compute invariants from an existing GraphML file using the remote
        grute graph services.

        Arguments:
            graph_file (str): The filename of the graphml file
            input_format (str): One of grute.GraphFormats
            invariants (str[]: Invariants.ALL)*: An array of grute.Invariants
                to compute on the graph
            email (str: self.email)*: The email to notify upon completion
            use_threads (bool: False)*: Whether to use Python threads to run
                computation in the background when waiting for the server to
                return the invariants
            callback (function: None)*: The function to run upon completion of
                the call, if using threads. (Will not be called if use_threads
                is set to False.)

        Returns:
            HTTP Response if use_threads is False. Otherwise, None

        Raises:
            ValueError: If the graph file does not exist, or if there are
                issues with the passed arguments
            RemoteDataUploadError: If there is an issue packing the file
            RemoteError: If the server experiences difficulty computing invs
        """
        if email is None:
            email = self.email

        if input_format not in GraphFormats._any:
            raise ValueError("Invalid input format, {}.".format(input_format))

        if not set(invariants) <= set(Invariants.ALL):
            raise ValueError("Invariants must be a subset of Invariants.ALL.")

        if use_threads and callback is not None:
            if not hasattr(callback, '__call__'):
                raise ValueError("callback must be a function.")
            if len(inspect.getargspec(callback).args) != 1:
                raise ValueError("callback must take exactly 1 argument.")

        url = "graphupload/{}/{}/{}/".format(
            email,
            input_format,
            "/".join(invariants)
        )

        if " " in url:
            raise ValueError("Arguments cannot have spaces in them.")

        if not (os.path.exists(graph_file)):
            raise ValueError("File {} does not exist.".format(graph_file))

        if use_threads:
            # Run in the background.
            upload_thread = threading.Thread(
                target=self._run_compute_invariants,
                args=[url, graph_file, callback]
            )
            upload_thread.start()

        else:
            # Run in the foreground.
            return self._run_compute_invariants(url, graph_file)
        return

    def _run_compute_invariants(self, url, graph_file, callback=None):
        try:
            tmpfile = tempfile.NamedTemporaryFile()
            zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)
            zfile.write(graph_file)
            zfile.close()
            tmpfile.flush()
            tmpfile.seek(0)
        except:
            raise ValueError("Unable to zip graph file for upload.")

        try:
            req = urllib2.Request(self.url(url), tmpfile.read())
            response = urllib2.urlopen(req)

            if callback is not None:
                callback(response.read())
            else:
                return response.read()
        except:
            raise RemoteDataUploadError("Failed to upload graph file. Try " +
                                        "troubleshooting with a ping()?")

    def convert_graph(self, graph_file, input_format, output_formats,
                      email=None, use_threads=False, callback=None):
        """
        Convert a graph from one GraphFormat to another.

        Arguments:
            graph_file (str): Filename of the file to convert
            input_format (str): A grute.GraphFormats
            output_formats (str[]): A grute.GraphFormats
            email (str: self.email)*: The email to notify
            use_threads (bool: False)*: Whether to use Python threads to run
                computation in the background when waiting for the server
            callback (function: None)*: The function to run upon completion of
                the call, if using threads. (Will not be called if use_threads
                is set to False.)

        Returns:
            HTTP Response if use_threads=False. Else, no return value.

        Raises:
            RemoteDataUploadError: If there's an issue uploading the data
            RemoteError: If there's a server-side issue
            ValueError: If there's a problem with the supplied arguments
        """
        if email is None:
            email = self.email

        if input_format not in GraphFormats._any:
            raise ValueError("Invalid input format {}.".format(input_format))

        if not set(output_formats) <= set(GraphFormats._any):
            raise ValueError("Output formats must be a GraphFormats.")

        if use_threads and callback is not None:
            if not hasattr(callback, '__call__'):
                raise ValueError("callback must be a function.")
            if len(inspect.getargspec(callback).args) != 1:
                raise ValueError("callback must take exactly 1 argument.")

        if not (os.path.exists(graph_file)):
            raise ValueError("No such file, {}!".format(graph_file))

        url = "convert/{}/{}/{}/l".format(
            email,
            input_format,
            ','.join(output_formats)
        )

        if " " in url:
            raise ValueError("Spaces are not permitted in arguments.")

        if use_threads:
            # Run in the background.
            convert_thread = threading.Thread(
                target=self._run_convert_graph,
                args=[url, graph_file, callback]
            )
            convert_thread.start()
        else:
            # Run in the foreground.
            return self._run_convert_graph(url, graph_file)
        return

    def _run_convert_graph(self, url, graph_file, callback=None):

        try:
            tmpfile = tempfile.NamedTemporaryFile()
            zfile = zipfile.ZipFile(tmpfile.name, "w", allowZip64=True)
            zfile.write(graph_file)
            zfile.close()
            tmpfile.flush()
            tmpfile.seek(0)
        except:
            raise ValueError("Unable to zip graph file for upload.")

        try:
            req = urllib2.Request(self.url(url), tmpfile.read())
            response = urllib2.urlopen(req)

            if callback is not None:
                callback(response.read())
            else:
                return response.read()
        except:
            raise RemoteDataUploadError("Failed to upload graph file. Try " +
                                        "troubleshooting with a ping()?")
