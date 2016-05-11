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

from .base import Base
from ndio.ndresource.boss.resource import *

class ProjectService_0_4(Base):
    def __init__(self):
        super().__init__()

    @property
    def endpoint(self):
        return 'resource'

    def list(self, resource, url_prefix, auth, session, send_opts):
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth, 
            proj_list_req = True)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        resp.raise_for_status()

    def create(self, resource, url_prefix, auth, session, send_opts):
        json = self._get_resource_params(resource)
        req = self.get_request(
            resource, 'POST', 'application/x-www-form-urlencoded', url_prefix, auth, 
            data = json)
            # json content-type currently broken.
            #resource, 'POST', 'application/json', url_prefix, auth, 
            #json = json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 201:
            return True

        print('Create failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        return False

    def get(self, resource, url_prefix, auth, session, send_opts):
        req = self.get_request(
            resource, 'GET', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 200:
            return resp.json()

        resp.raise_for_status()

    def update(self, old_resource, new_resource, url_prefix, auth, session, send_opts):
        json = self._get_resource_params(new_resource)
        req = self.get_request(
            old_resource, 'PUT', 'application/application/x-www-form-urlencoded',
            url_prefix, auth, json = json)
            #old_resource, 'PUT', 'application/json', url_prefix, auth, 
            #json = json)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)

        if resp.status_code == 200:
            return True

        print('Update failed on {}, got HTTP response: ({}) - {}'.format(
            old_resource.name, resp.status_code, resp.text))
        return False


    def delete(self, resource, url_prefix, auth, session, send_opts):
        req = self.get_request(
            resource, 'DELETE', 'application/json', url_prefix, auth)
        prep = session.prepare_request(req)
        resp = session.send(prep, **send_opts)
        if resp.status_code == 204:
            return True

        if resp.status_code == 404:
            print('Delete failed, {} not found.'.format(resource.name))
            return False

        if resp.status_code == 403:
            print('Delete failed on {}, access denied.'.format(resource.name))
            return False
        
        print('Delete failed on {}, got HTTP response: ({}) - {}'.format(
            resource.name, resp.status_code, resp.text))
        return False

    def _get_resource_params(self, resource):
        if isinstance(resource, CollectionResource):
            return self._get_collection_params(resource)

        if isinstance(resource, ExperimentResource):
            return self._get_experiment_params(resource)

        if isinstance(resource, CoordinateFrameResource):
            return self._get_coordinate_params(resource)

        if isinstance(resource, LayerResource):
            params = self._get_channel_layer_params(resource)
            params['is_channel'] = False
            return params

        if isinstance(resource, ChannelResource):
            params = self._get_channel_layer_params(resource)
            params['is_channel'] = True
            return params
        
        raise TypeError('resource is not supported type.')

    def _get_collection_params(self, coll):
        return { 'name': coll.name, 'description': coll.description }

    def _get_experiment_params(self, exp):
        return { 
            'description': exp.description ,
            'coord_frame': exp.coord_frame,
            'num_hierarchy_levels': exp.num_hierarchy_levels,
            'hierarchy_method': exp.hierarchy_method,
            'max_time_sample': exp.max_time_sample
        }

    def _get_coordinate_params(self, coord):
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
            'voxel_unit': coord.voxel_unit,
            'time_step': coord.time_step,
            'time_step_unit': coord.time_step_unit
        }

    def _get_channel_layer_params(self, chlyr):
        return {
            'description': chlyr.description ,
            'default_time_step': chlyr.default_time_step,
            'datatype': chlyr.datatype,
            'base_resolution': chlyr.base_resolution
        }