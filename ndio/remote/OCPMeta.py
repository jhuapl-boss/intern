import requests
import tempfile

from Remote import Remote
from errors import *

DEFAULT_HOSTNAME = "api.neurodata.io"
DEFAULT_PROTOCOL = "http"


class OCPMeta(Remote):

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(OCPMeta, self).__init__(hostname, protocol)


    def url(self):
        return super(OCPMeta, self).url('/api/')


    def get_all(self):
        """
        Get all of the metadata.

        Equivalent to navigating to http://api.neurodata.io/api/metadata/get
        """
        req = requests.get(self.url() + 'metadata/get')
        return req.json()
