# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
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
from intern.service.boss import BaseVersion
from intern.service.boss.v1 import BOSS_API_VERSION
from intern.resource.boss.resource import *
from requests import HTTPError
import copy


class ProjectService_1(BaseVersion):
    """The Boss API v1 project service.
    """

    def __init__(self):
        BaseVersion.__init__(self)

    @property
    def version(self):
        """Return the API Version for this implementation
        """
        return BOSS_API_VERSION

    def list_groups(self, filtr, url_prefix, auth, session, send_opts):
        """Get the groups the logged in user is a member of.

        Optionally filter by 'member' or 'maintainer'.

        Args:
            filtr (string|None): ['member'|'maintainer'] or defaults to None.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[string]): List of group names.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'GET', 'application/json', url_prefix, auth)
        if filtr is not None:
            if not filtr == 'member' and not filtr == 'maintainer':
                raise RuntimeError(
                    'filtr must be either "member", "maintainer", or None.')
            req.params = {'filter': filtr}

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json['groups']

        msg = ('List groups failed, got HTTP response: ({}) - {}'.format(
            resp.status_code, resp.text))

        raise HTTPError(msg, request = req, response = resp)

    def get_group(self, name, user_name, url_prefix, auth, session, send_opts):
        """Get owner of group and the resources it's attached to.

        Args:
            name (string): Name of group to query.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dict): Keys include 'owner', 'name', 'resources'.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'GET', 'application/json', url_prefix, auth, name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = ('Get failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))

        raise HTTPError(msg, request = req, response = resp)

    def create_group(self, name, url_prefix, auth, session, send_opts):
        """Create a new group.

        Args:
            name (string): Name of the group to create.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'POST', 'application/json', url_prefix, auth, name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = ('Create failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def delete_group(self, name, url_prefix, auth, session, send_opts):
        """Delete given group.

        Args:
            name (string): Name of group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_request(
            'DELETE', 'application/json', url_prefix, auth, name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Delete failed for group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def list_group_members(self, name, url_prefix, auth, session, send_opts):
        """Get the members of a group (does not include maintainers).

        Args:
            name (string): Name of group to query.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[string]): List of member names.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_members_request(
            'GET', 'application/json', url_prefix, auth, name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json['members']

        msg = ('Failed getting members of group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def get_is_group_member(self, grp_name, user, url_prefix, auth, session, send_opts):
        """Check if the given user is a member of the named group.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): False if user not a member.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_members_request(
            'GET', 'application/json', url_prefix, auth, grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json['result']

        msg = ('Failed determining if user {} is member of group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def add_group_member(self, grp_name, user, url_prefix, auth, session, send_opts):
        """Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_members_request(
            'POST', 'application/json', url_prefix, auth, grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Failed adding user {} to group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def delete_group_member(
        self, grp_name, user, url_prefix, auth, session, send_opts):
        """Delete the given user from the named group.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_members_request(
            'DELETE', 'application/json', url_prefix, auth,
            grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Failed deleting maintainer {} from group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def list_group_maintainers(self, name, url_prefix, auth, session, send_opts):
        """Get the maintainers of a group.

        Args:
            name (string): Name of group to query.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[string]): List of maintainer names.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_maintainers_request(
            'GET', 'application/json', url_prefix, auth, name)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json['maintainers']

        msg = ('Failed getting maintainers of group {}, got HTTP response: ({}) - {}'.format(
            name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)


    def get_is_group_maintainer(self, grp_name, user, url_prefix, auth, session, send_opts):
        """Check if the given user is a maintainer of the named group.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (bool): False if user not a maintainer.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_maintainers_request(
            'GET', 'application/json', url_prefix, auth, grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            resp_json = resp.json()
            return resp_json['result']

        msg = ('Failed determining if user {} is maintainer of group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def add_group_maintainer(self, grp_name, user, url_prefix, auth, session, send_opts):
        """Add the given user to the named group.

        Both group and user must already exist for this to succeed.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_maintainers_request(
            'POST', 'application/json', url_prefix, auth, grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Failed adding maintainer {} to group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def delete_group_maintainer(
        self, grp_name, user, url_prefix, auth, session, send_opts):
        """Delete the given user from the named group.

        Args:
            name (string): Name of group.
            user (string): User to add to group.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_group_maintainers_request(
            'DELETE', 'application/json', url_prefix, auth,
            grp_name, user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Failed deleting maintainer {} from group {}, got HTTP response: ({}) - {}'.format(
            user, grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def list_permissions(self, group_name=None, resource=None,
                        url_prefix=None, auth=None, session=None, send_opts=None):
        """List the permission sets for the logged in user

        Optionally filter by resource or group.

        Args:
            group_name (string): Name of group to filter on
            resource (intern.resource.boss.BossResource): Identifies which data model object to filter on
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[dict]): List of dictionaries of permission sets
        """
        filter_params = {}
        if group_name:
            filter_params["group"] = group_name

        if resource:
            filter_params.update(resource.get_dict_route())

        req = self.get_permission_request('GET', 'application/json',
                                          url_prefix, auth, query_params=filter_params)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code != 200:
            msg = "Failed to get permission sets. "
            if group_name:
                msg = "{} Group: {}".format(msg, group_name)
            if resource:
                msg = "{} Resource: {}".format(msg, resource.name)

            msg = '{}, got HTTP response: ({}) - {}'.format(msg, resp.status_code, resp.text)

            raise HTTPError(msg, request=req, response=resp)
        else:
            return resp.json()["permission-sets"]

    def get_permissions(self, group_name, resource,url_prefix, auth, session, send_opts):
        """Get the permission set for a specific group/resource combination

        Args:
            group_name (string): Name of group to filter on
            resource (intern.resource.boss.BossResource): Identifies which data model object to filter on
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list[str]): List of permissions
        """
        filter_params = {"group": group_name}
        filter_params.update(resource.get_dict_route())

        req = self.get_permission_request('GET', 'application/json',
                                          url_prefix, auth, query_params=filter_params)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code != 200:
            msg = "Failed to get permission set for Group: {} Resource: {}".format(group_name, resource.name)
            msg = '{}, got HTTP response: ({}) - {}'.format(msg, resp.status_code, resp.text)

            raise HTTPError(msg, request=req, response=resp)
        else:
            if resp.json()["permission-sets"]:
                return resp.json()["permission-sets"][0]['permissions']
            else:
                return []

    def add_permissions(self, group_name, resource, permissions, url_prefix, auth, session, send_opts):
        """
        Args:
            group_name (string): Name of group.
            resource (intern.resource.boss.BossResource): Identifies which data model object to operate on.
            permissions (list): List of permissions to add to the given resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().
        """
        post_data = {"group": group_name,
                     "permissions": permissions,
                     }
        post_data.update(resource.get_dict_route())
        req = self.get_permission_request('POST', 'application/json',
                                          url_prefix, auth, post_data=post_data)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code != 201:
            msg = ('Failed adding permissions to group {}, got HTTP response: ({}) - {}'.format(group_name,
                                                                                                resp.status_code,
                                                                                                resp.text))
            raise HTTPError(msg, request=req, response=resp)

    def update_permissions(self, group_name, resource, permissions, url_prefix, auth, session, send_opts):
        """
        Args:
            group_name (string): Name of group.
            resource (intern.resource.boss.BossResource): Identifies which data model object to operate on.
            permissions (list): List of permissions to attach to the given resource. Will overwrite existing permissions
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().
        """
        post_data = {"group": group_name,
                     "permissions": permissions,
                     }
        post_data.update(resource.get_dict_route())
        req = self.get_permission_request('PATCH', 'application/json',
                                          url_prefix, auth, post_data=post_data)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code != 200:
            msg = ('Failed adding permissions to group {}, got HTTP response: ({}) - {}'.format(group_name,
                                                                                                resp.status_code,
                                                                                                resp.text))
            raise HTTPError(msg, request=req, response=resp)

    def delete_permissions(self, grp_name, resource, url_prefix, auth, session, send_opts):
        """
        Args:
            grp_name (string): Name of group.
            resource (intern.resource.boss.BossResource): Identifies which data model object to operate on.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        filter_params = {"group": grp_name}
        filter_params.update(resource.get_dict_route())

        req = self.get_permission_request('DELETE', 'application/json',
                                          url_prefix, auth, query_params=filter_params)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = ('Failed deleting permissions to group {}, got HTTP response: ({}) - {}'.format(
            grp_name, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def get_user_roles(self, user, url_prefix, auth, session, send_opts):
        """Get roles associated with the given user.

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of roles that user has.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'GET', 'application/json', url_prefix, auth,
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = (
            'Failed getting roles for user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def add_user_role(self, user, role, url_prefix, auth, session, send_opts):
        """Add role to given user.

        Args:
            user (string): User name.
            role (string): Role to assign.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'POST', 'application/json', url_prefix, auth,
            user, role)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = (
            'Failed adding role: {} to user: {}, got HTTP response: ({}) - {}'
            .format(role, user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def delete_user_role(self, user, role, url_prefix, auth, session, send_opts):
        """Remove role from given user.

        Args:
            user (string): User name.
            role (string): Role to remove.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_role_request(
            'DELETE', 'application/json', url_prefix, auth,
            user, role)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = (
            'Failed deleting role: {} from user: {}, got HTTP response: ({}) - {}'
            .format(role, user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def get_user(self, user, url_prefix, auth, session, send_opts):
        """Get user's data (first and last name, email, etc).

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (dictionary): User's data encoded in a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'GET', 'application/json', url_prefix, auth,
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        msg = (
            'Failed getting user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request=req, response=resp)

    def add_user(
        self, user, first_name, last_name, email, password,
        url_prefix, auth, session, send_opts):
        """Add a new user.

        Args:
            user (string): User name.
            first_name (string): User's first name.
            last_name (string): User's last name.
            email: (string): User's email address.
            password: (string): User's password.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'POST', 'application/json', url_prefix, auth,
            user, first_name, last_name, email, password)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 201:
            return

        msg = (
            'Failed adding user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def delete_user(self, user, url_prefix, auth, session, send_opts):
        """Delete the given user.

        Args:
            user (string): User name.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_user_request(
            'DELETE', 'application/json', url_prefix, auth,
            user)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        msg = (
            'Failed deleting user: {}, got HTTP response: ({}) - {}'
            .format(user, resp.status_code, resp.text))
        raise HTTPError(msg, request = req, response = resp)

    def list(self, resource, url_prefix, auth, session, send_opts):
        """List all resources of the same type as the given resource.

        Args:
            resource (intern.resource.boss.BossResource): List resources of the same type as this..
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (list): List of resources.  Each resource is a dictionary.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth,
            proj_list_req=True)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return self._get_resource_list(resp.json())

        err = ('List failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def create(self, resource, url_prefix, auth, session, send_opts):
        """Create the given resource.

        Args:
            resource (intern.resource.boss.BossResource): Create a data model object with attributes matching those of the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (intern.resource.boss.BossResource): Returns resource of type requested on success.

        Raises:
            requests.HTTPError on failure.
        """
        json = self._get_resource_params(resource)
        req = self.get_request(resource, 'POST', 'application/json', url_prefix, auth, json=json)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 201:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Create failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def get(self, resource, url_prefix, auth, session, send_opts):
        """Get attributes of the given resource.

        Args:
            resource (intern.resource.boss.BossResource): Create a data model object with attributes matching those of the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (intern.resource.boss.BossResource): Returns resource of type requested on success.

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Get failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def update(self, resource_name, resource, url_prefix, auth, session, send_opts):
        """Updates an entity in the data model using the given resource.

        Args:
            resource_name (string): Current name of the resource (in case the resource is getting its name changed).
            resource (intern.resource.boss.BossResource): New attributes for the resource.
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Returns:
            (intern.resource.boss.BossResource): Returns updated resource of given type on success.

        Raises:
            requests.HTTPError on failure.
        """

        # Create a copy of the resource and change its name to resource_name
        # in case the update includes changing the name of a resource.
        old_resource = copy.deepcopy(resource)
        old_resource.name = resource_name

        json = self._get_resource_params(resource, for_update=True)

        req = self.get_request(old_resource, 'PUT', 'application/json', url_prefix, auth, json=json)

        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            return self._create_resource_from_dict(resource, resp.json())

        err = ('Update failed on {}, got HTTP response: ({}) - {}'.format(
            old_resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)


    def delete(self, resource, url_prefix, auth, session, send_opts):
        """Deletes the entity described by the given resource.

        Args:
            resource (intern.resource.boss.BossResource)
            url_prefix (string): Protocol + host such as https://api.theboss.io
            auth (string): Token to send in the request header.
            session (requests.Session): HTTP session to use for request.
            send_opts (dictionary): Additional arguments to pass to session.send().

        Raises:
            requests.HTTPError on failure.
        """
        req = self.get_request(
            resource, 'DELETE', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return

        err = ('Delete failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        raise HTTPError(err, request = req, response = resp)

    def _get_resource_params(self, resource, for_update=False):
        """Get dictionary containing all parameters for the given resource.

        When getting params for a coordinate frame update, only name and
        description are returned because they are the only fields that can
        be updated.

        Args:
            resource (intern.resource.boss.resource.BossResource): A sub-class
                whose parameters will be extracted into a dictionary.
            for_update (bool): True if params will be used for an update.

        Returns:
            (dictionary): A dictionary containing the resource's parameters as
            required by the Boss API.

        Raises:
            TypeError if resource is not a supported class.
        """
        if isinstance(resource, CollectionResource):
            return self._get_collection_params(resource)

        if isinstance(resource, ExperimentResource):
            return self._get_experiment_params(resource, for_update)

        if isinstance(resource, CoordinateFrameResource):
            return self._get_coordinate_params(resource, for_update)

        if isinstance(resource, ChannelResource):
            return self._get_channel_params(resource, for_update)

        raise TypeError('resource is not supported type.')

    def _get_collection_params(self, coll):
        return { 'name': coll.name, 'description': coll.description }

    def _get_experiment_params(self, exp, for_update):
        if not for_update:
            return {
                'name': exp.name,
                'description': exp.description ,
                'coord_frame': exp.coord_frame,
                'num_hierarchy_levels': exp.num_hierarchy_levels,
                'hierarchy_method': exp.hierarchy_method,
                'num_time_samples': exp.num_time_samples,
                'collection': exp.coll_name,
                'time_step': exp.time_step,
                'time_step_unit': exp.time_step_unit
            }

        return {
            'name': exp.name,
            'description': exp.description ,
            'num_hierarchy_levels': exp.num_hierarchy_levels,
            'hierarchy_method': exp.hierarchy_method
        }

    def _get_coordinate_params(self, coord, for_update):
        if not for_update:
            return {
                'name': coord.name,
                'description': coord.description ,
                'x_start': coord.x_start,
                'x_stop': coord.x_stop,
                'y_start': coord.y_start,
                'y_stop': coord.y_stop,
                'z_start': coord.z_start,
                'z_stop': coord.z_stop,
                'x_voxel_size': coord.x_voxel_size,
                'y_voxel_size': coord.y_voxel_size,
                'z_voxel_size': coord.z_voxel_size,
                'voxel_unit': coord.voxel_unit
            }

        return { 'name': coord.name, 'description': coord.description }

    def _get_channel_params(self, chan, for_update):
        if not for_update:
            return {
                'name': chan.name,
                'description': chan.description ,
                'default_time_sample': chan.default_time_sample,
                'datatype': chan.datatype,
                'base_resolution': chan.base_resolution,
                'type': chan.type,
                'sources': chan.sources,
                'related': chan.related
            }

        return {
            'name': chan.name,
            'description': chan.description,
            'base_resolution': chan.base_resolution,
            'sources': chan.sources,
            'related': chan.related
        }

    def _create_resource_from_dict(self, resource, dict):
        """
        Args:
            resource (intern.resource.boss.BossResource): Used to determine type of resource to create.
            dict (dictionary): JSON data returned by the Boss API.

        Returns:
            (intern.resource.boss.BossResource): Instance populated with values from dict.

        Raises:
            KeyError if dict missing required key.
            TypeError if resource is not a supported class.
        """
        if isinstance(resource, CollectionResource):
            return self._get_collection(dict)

        if isinstance(resource, ExperimentResource):
            return self._get_experiment(dict, resource.coll_name)

        if isinstance(resource, CoordinateFrameResource):
            return self._get_coordinate(dict)

        if isinstance(resource, ChannelResource):
            return self._get_channel(dict, resource.coll_name, resource.exp_name)

        raise TypeError('resource is not supported type.')

    def _get_collection(self, dict):
        name = dict['name']
        description = dict['description']
        creator = dict['creator']
        return CollectionResource(
            name, description, creator, raw=dict)

    def _get_experiment(self, dict, coll_name):
        exp_keys = [
            'name', 'description', 'creator', 'coord_frame',
            'num_hierarchy_levels', 'hierarchy_method', 'num_time_samples', 
            'time_step', 'time_step_unit'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in exp_keys }
        return ExperimentResource(
            collection_name=coll_name, raw=dict, **filtered)

    def _get_coordinate(self, dict):
        coord_keys = [
            'name', 'description', 'x_start', 'x_stop',
            'y_start', 'y_stop', 'z_start', 'z_stop',
            'x_voxel_size', 'y_voxel_size', 'z_voxel_size',
            'voxel_unit'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in coord_keys }
        return CoordinateFrameResource(raw=dict, **filtered)

    def _get_channel(self, dict, coll_name, exp_name):
        chan_keys = [
            'name', 'description', 'creator', 'default_time_sample',
            'datatype', 'base_resolution', 'type', 'sources', 'related',
            'downsample_status'
        ]

        filtered = { k:v for (k, v) in dict.items() if k in chan_keys }
        collection = coll_name
        return ChannelResource(
            collection_name=collection,
            experiment_name=exp_name, raw=dict, **filtered)

    def _get_resource_list(self, rsrc_dict):
        """Extracts list of resources from the HTTP response.

        Args:
            rsrc_dict (dict): HTTP response encoded in a dictionary.

        Returns:
            (list[string]): List of a type of resource (collections, experiments, etc).

        Raises:
            (RuntimeError): If rsrc_dict does not contain any known resources.
        """
        if 'collections' in rsrc_dict:
            return rsrc_dict['collections']
        if 'experiments' in rsrc_dict:
            return rsrc_dict['experiments']
        if 'channels' in rsrc_dict:
            return rsrc_dict['channels']
        if 'coords' in rsrc_dict:
            return rsrc_dict['coords']

        raise RuntimeError('Invalid list response received from Boss.  No known resource type returned.')
