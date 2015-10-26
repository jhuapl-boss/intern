import requests
import json

from Remote import Remote
from errors import *

DEFAULT_HOSTNAME = "api.neurodata.io"
DEFAULT_PROTOCOL = "http"


class OCPMeta(Remote):
    """
    OCPMeta Remotes enable access to the Metadata-OCP API endpoints (which
    can be found at `api.neurodata.io/metadata/ocp/`). This class is useful
    for reading metadata for existing projects, or, if you specify a key,
    adding new metadata, manipulating your existing metadata, and archiving
    old metadata. Archived metadata is still stored by the LIMS system.
    """

    def __init__(self,
                 hostname=DEFAULT_HOSTNAME,
                 protocol=DEFAULT_PROTOCOL,
                 key=""):
        super(OCPMeta, self).__init__(hostname, protocol)
        self.key = key


    def get_project_by_token(self, token):
        """
        Get metadata via a project token.

        Arguments:
            token:      The project (token) to access
        Returns:
            JSON metadata associated with this project
        """

        req = requests.get(self.url("/metadata/ocp/get/" + token))
        return req.json()


    def insert_project(self, token, data):
        """
        Insert new metadata into the OCP metadata database.

        Arguments:
            token:      A new token to insert. If your `data` contains a token,
                        it is overwritten by this value.
            data:       A dictionary to insert as metadata.
        Returns:
            JSON of the inserted ID (convenience) or an error message.
        Throws:
            RemoteDataUploadError if the token is already populated, or if you
            have not specified an API key.
        """
        if self.key == "" or not self.key:
            raise BadAPIKeyError("No API key specified. (Request one from support@neurodata.io.)")

        req = requests.post(self.url("/metadata/ocp/set/" + token), data=data)
        if req.status_code != 200:
            raise RemoteDataUploadError("Could not upload metadata: " + req.json()['message'])
        return req.json()
