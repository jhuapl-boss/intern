import networkx

from Remote import Remote
from errors import *
import ndio.ramon as ramon

DEFAULT_HOSTNAME = "openconnecto.me"
DEFAULT_PROTOCOL = "http"


class m2g(Remote):

    SMALL = S = 's'
    BIG = B = 'b'

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(m2g, self).__init__(hostname, protocol)

    def ping(self):
        return super(m2g, self).ping()

    def url(self, suffix=""):
        return super(m2g, self).url('/graph-services/' + suffix)

    def build_graph(self, project, site, subject, session, scan, size, email):
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

        Returns:
            networkx.Graph

        Raises:
            ValueError: When the supplied values are invalid (contain invalid
                characters, bad email address supplied, etc.)
            RemoteDataNotFoundError: When the data cannot be processed due to
                a server error.
        """

        if size not in [self.BIG, self.SMALL]:
            raise ValueError("size must be either m2g.BIG or m2g.SMALL.")

        url = "buildgraph/{}/{}/{}/{}/{}/{}".format(
            project,
            site,
            subject,
            session,
            scan,
            size
        )

        if " " in url:
            raise ValueError("Arguments must not contain spaces.")

        raise NotImplementedError(":(")
