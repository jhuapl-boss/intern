import zipfile
import tempfile
import inspect
import urllib2

from Remote import Remote
from errors import *
import ndio.ramon as ramon

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"


class Invariants:
    SCAN_STATISTIC = ss1 = "ss1"        # the Scan Statistic 1
    TRIANGLE_COUNT = tri = "tri"        # the Triangle Count
    CLUSTERING = cc = "cc"              # the Clustering Coefficient
    MAX_AVG_DEGREE = mad = "mad"        # the Maximum Average Degree
    LOCAL_DEGREE = deg = "deg"          # The Local Degree Count
    EIGENS = eig = "eig"                # the Top-k (100 or maximum
                                        #   available/computable)
                                        #   eigenvectors and eigenvalues
    ALL = [
        self.SCAN_STATISTIC
        self.TRIANGLE_COUNT
        self.CLUSTERING
        self.MAX_AVG_DEGREE
        self.LOCAL_DEGREE
        self.EIGENS
    ]


class m2g(Remote):

    SMALL = S = 's'
    BIG = B = 'b'

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(m2g, self).__init__(hostname, protocol)

    def ping(self):
        return super(m2g, self).ping()

    def url(self, suffix=""):
        return super(m2g, self).url('/graph-services/' + suffix)

    def build_graph(self, project, site, subject, session, scan,
                    size, email, invariants,
                    fiber_file, atlas_file=None,
                    use_threads=True, callback=None):
        """
        Builds a graph using the graph-services endpoint.

        Arguments:
            project (str): The project to use
            site (str): The site in question
            subject (str): The subject's identifier
            session (str): The session (per subject)
            scan (str): The scan identifier
            size (str): Whether to return a big or (m2g.BIG) small (m2g.SMALL)
                graph. For a better explanation of each, see m2g.io.
            email (str): An email to which to send the download link
            invariants (str[]: Invariants.ALL): An array of invariants to
                compute. You can use the m2g.Invariants class to construct this
                list, or simply pass m2g.Invariants.ALL to compute them all.
            fiber_file (str): A local filename of an MRI Studio .dat file
            atlas_file (str: None): A local atlas file, in NIFTI .nii format.
                If none is specified, the Desikan atlas is used by default.
            use_threads (bool: True): Whether to run the download in a Python
                thread. If set to True, the call to `build_graph` will end
                quickly, and the `callback` will be called with the returned
                status-code of the restful call as its only argument.
            callback (function: None): The function to run upon completion of
                the call, if using threads. (Will not be called if use_threads
                is set to False.)

        Returns:
            networkx.Graph

        Raises:
            ValueError: When the supplied values are invalid (contain invalid
                characters, bad email address supplied, etc.)
            RemoteDataNotFoundError: When the data cannot be processed due to
                a server error.
        """

        if use_threads and callback is not None:
            if not hasattr(callback, '__call__'):
                raise ValueError("callback must be a function.")
            if len(inspect.getargspec(callback).args) != 1:
                raise ValueError("callback must take exactly 1 argument.")

        # Once we get here, we know the callback is
        if size not in [self.BIG, self.SMALL]:
            raise ValueError("size must be either m2g.BIG or m2g.SMALL.")

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

            # At the end, call the callback with the return status.
            raise NotImplementedError(":(")
            result = ??
            callback(result)
        else:
            # Run in the foreground.
            raise NotImplementedError(":(")


    def _run_graph_download(url, fiber_file, atlas_file=None):

        try:
            # Create a temporary file to store zip contents in memory
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
            # Call the URL
            req = urllib2.Request(call_url, tmpfile.read())
            response = urllib2.urlopen(req)

        except:
            raise RemoteDataUploadError("Failed to upload data at " + url)
