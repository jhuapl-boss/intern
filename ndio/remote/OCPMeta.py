import requests
import json

from Remote import Remote
from errors import *

DEFAULT_HOSTNAME = "api.neurodata.io"
DEFAULT_PROTOCOL = "http"


class OCPMeta(Remote):

    def __init__(self, hostname=DEFAULT_HOSTNAME, protocol=DEFAULT_PROTOCOL):
        super(OCPMeta, self).__init__(hostname, protocol)


    def get_all(self):
        """
        Get all of the metadata.

        Equivalent to navigating to http://api.neurodata.io/api/metadata/get
        """
        req = requests.get(self.url('/api/metadata/get'))
        return req.json()


    def get_token(self, token):
        req = requests.get(self.url("/metadata/ocp/get/" + token))
        return req.json()


    def set_token(self, token, data):
        req = requests.post(self.url("/metadata/ocp/set/" + token), data=data)
        if req.status_code != 200:
            raise RemoteDataUploadError("Could not upload metadata: " + req.json()['message'])
        return req.json()
