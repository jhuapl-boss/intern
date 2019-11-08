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

class VolumeService(DVIDService):
    """
        VolumeService for DVID service.
    """
    def __init__(self, base_url):
        """Constructor.

        Args:
            base_url (string): Base url (host) of project service.

        Raises:
            (KeyError): if given invalid version.
        """
        DVIDService.__init__(self)
        self.base_url = base_url

    def get_cutout(self, resource, res, xrange, yrange, zrange):

        """
        Upload a cutout to the Boss data store.

        Args:
            resource (intern.resource.resource.Resource): Resource compatible
                with cutout operations
            resolution (int): 0 (not applicable on DVID Resource).
            x_range (list[int]): x range such as [10, 20] which means x>=10 and x<20.
            y_range (list[int]): y range such as [10, 20] which means y>=10 and y<20.
            z_range (list[int]): z range such as [10, 20] which means z>=10 and z<20.

        Returns:
            (numpy.array): A 3D or 4D numpy matrix in ZXY(time) order.

        Raises:
            requests.HTTPError
        """
        #Defining used variables
        UUID = resource.UUID
        data_instance = resource.name

        """
            xpix = "x" how many pixels traveled in x
            ypix = "y" how many pixels traveled in y
            zpix = "z" how many pixels traveled in z
            xo, yo, zo (x,y,z offsets)
            type = "raw"
            scale = "grayscale"
        """
        xpix = xrange[1]-xrange[0]
        xo = xrange[0]
        ypix = yrange[1]-yrange[0]
        yo = yrange[0]
        zpix = zrange[1]-zrange[0]
        zo = zrange[0]

        size = str(xpix) + "_" + str(ypix) + "_" + str(zpix)
        offset = str(xo) + "_" + str(yo) + "_" + str(zo)

        #User entered IP address with added octet-stream line to obtain data from api in octet-stream form
        #0_1_2 specifies a 3 dimensional octet-stream "xy" "xz" "yz"
        address = self.base_url + "/api/node/" + UUID + "/" + data_instance + "/raw/0_1_2/" + size + "/" + offset + "/octet-stream"
        r = requests.get(address)
        octet_stream = r.content

         #Converts obtained octet-stream into a numpy array of specified type uint8
        block = np.fromstring(octet_stream, dtype = np.uint8)
        try:
            #Specifies the 3 dimensional shape of the numpy array of the size given by the user
            volumeOut =  block.reshape(zpix,ypix,xpix)
        except ValueError:
            return "There is no data currently loaded on your specified host."

        #Returns a 3-dimensional numpy array to the user
        return volumeOut

