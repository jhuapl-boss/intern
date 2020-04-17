# Copyright 2019 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from intern.service.dvid import DVIDService
import requests
import numpy as np
import json
import ast


class VersioningService(DVIDService):
    """ VersioningService for DVID service.
    """

    def __init__(self, base_url):
        """ Constructor.

        Args:
            base_url (str): Base url (host) of project service.

        Raises:
            (KeyError): if given invalid version.
        """
        DVIDService.__init__(self)
        self.base_url = base_url

    def merge(self, UUID, parents, mergeType, note):
        """ Creates a conflict-free merge of a set of committed parent UUIDs into a child.  Note
            the merge will not necessarily create an error immediately

        Args:
            mergeType (str) = "conflict-free"
            parents (array) = [ "parent-uuid1", "parent-uuid2", ... ]
            note (str) = this is a description of what I did on this commit

        Returns:
            merge_child_uuid (str): child generated uuid after merge

        Raises:
            HTTPError: On non 200 status code
        """

        merge_resp = requests.post(
            "{}/api/repo/{}/merge".format(self.base_url, UUID),
            json={"mergeType": mergeType, "parents": parents, "note": note},
        )
        if merge_resp.status_code != 200:
            raise requests.HTTPError(merge_resp.content)

        merge_child_uuid = merge_resp.json()["child"]
        return merge_child_uuid

    def resolve(self, UUID, data, parents, note):
        """ Forces a merge of a set of committed parent UUIDs into a child by specifying a
            UUID order that establishes priorities in case of conflicts

        Args:
            data (array) = [ "instance-name-1", "instance-name2", ... ],
            parents (array): [ "parent-uuid1", "parent-uuid2", ... ],
            note (str): this is a description of what I did on this commit

        Returns:
            resolve_child_uuid (str): child generated uuid after resolution

        Raises:
            HTTPError: On non 200 status code
        """

        resolve_resp = requests.post(
            "{}/api/repo/{}/resolve".format(self.base_url, UUID),
            json={"data": data, "parents": parents, "note": note},
        )
        if resolve_resp.status_code != 200:
            raise requests.HTTPError(resolve_resp.content)

        resolve_child_uuid = resolve_resp.json()["child"]
        return resolve_child_uuid

    def get_log(self, UUID):
        """The log is a list of strings that will be appended to the repo's log.  They should be
            descriptions for the entire repo and not just one node.

        Args:
            UUID (str): UUID of the DVID repository

        Returns:
            str: list of all log recordings related to the DVID repository

        Raises:
            (ValueError): if given invalid UUID.
        """
        if UUID == "":
            raise ValueError("The UUID was not specified")
        else:
            log_resp = requests.get("{}/api/node/{}/log".format(self.base_url, UUID))
            if log_resp.status_code != 200:
                raise requests.HTTPError(log_resp.content)
            log_m = log_resp.content
            return log_m

    def post_log(self, UUID, log_m):
        """Allows the user to write a short description of the content in the repository
            { "log": [ "provenance data...", "provenance data...", ...] }
        Args:
            UUID (str): UUID of the DVID repository (str)
            log_m (str): Message to record on the repositories history log (str)

        Returns:
            HTTP Response

        Raises:
            (ValueError): if given invalid UUID or log.
        """

        if UUID == "":
            raise ValueError("The UUID was not specified")
        elif log_m == "":
            raise ValueError("Your log submission cannot be empty")
        else:
            log_resp = requests.post(
                "{}/api/node/{}/log".format(self.base_url, UUID), json={"log": [log_m]}
            )
            if log_resp.status_code != 200:
                raise requests.HTTPError(log_resp.content)
            return log_resp

    def commit(self, UUID, note="", log_m=""):
        """Allows the user to write a short description of the content in the repository

        Args:
            UUID (str): UUID of the DVID repository
            note (str): human-readable commit message
            log_m (str): Message to record on the repositories history log

        Returns:
            commit_uuid (str): commit hash

        Raises:
            (ValueError): if given invalid UUID.
        """

        if UUID == "":
            raise ValueError("The UUID was not specified")
        else:
            committed = requests.post(
                "{}/api/node/{}/commit".format(self.base_url, UUID),
                json={"note": note, "log": [log_m]},
            )
            if committed.status_code != 200:
                raise requests.HTTPError(committed.content)

            commit_uuid = committed.json()["committed"]
            return commit_uuid

    def branch(self, UUID, note=""):
        """Allows the user to write a short description of the content in the repository

        Args:
            UUID (str): UUID of the DVID repository
            note (str): Message to record when branching

        Returns:
            branch_uuid (str): The child branch UUID

        Raises:
            (KeyError): if given invalid version.
        """

        if UUID == "":
            raise ValueError("The UUID was not specified")
        else:
            branch = requests.post(
                "{}/api/node/{}/branch".format(self.base_url, UUID), json={"note": note}
            )
            if branch.status_code != 200:
                raise requests.HTTPError(branch.content)

            branch_uuid = branch.json()["child"]
            return branch_uuid
