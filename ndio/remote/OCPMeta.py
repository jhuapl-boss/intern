import requests
import json

from Remote import Remote
from errors import *


DEFAULT_HOSTNAME = "lims.neurodata.io"
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
                 protocol=DEFAULT_PROTOCOL):
        super(OCPMeta, self).__init__(hostname, protocol)

    def get_metadata(self, token):
        """
        Get metadata via a project token.

        Arguments:
            token (str):      The project (token) to access

        Returns:
            JSON metadata associated with this project
        """

        req = requests.get(self.url("/metadata/ocp/get/" + token))
        return req.json()

    def set_metadata(self, token, data):
        """
        Insert new metadata into the OCP metadata database.

        Arguments:
            token (str): Token of the datum to set
            data (str): A dictionary to insert as metadata. Include `secret`.

        Returns:
            JSON of the inserted ID (convenience) or an error message.

        Throws:
            RemoteDataUploadError: If the token is already populated, or if
                there is an issue with your specified `secret` key.
        """

        req = requests.post(self.url("/metadata/ocp/set/" + token), data=data)

        if req.status_code != 200:
            raise RemoteDataUploadError(
                "Could not upload metadata: " + req.json()['message']
            )
        return req.json()
