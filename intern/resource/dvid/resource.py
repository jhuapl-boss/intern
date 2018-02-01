# Copyright 2017 The Johns Hopkins University Applied Physics Laboratory
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

from intern.resource import Resource
from io import BytesIO
import numpy as np
import requests
import json
import ast


class DvidResource(Resource):

    """Base class for Dvid resources.

    Attributes:
        name (string): Name of resource.  Used as identifier when talking to
        the Dvid API.
        description (string): Text description of resource.
        creator (string): Resource creator.
        raw (dictionary): Holds JSON data returned by DVID on a POST (create) or GET operation.
    """

    def __init__(self):
        """
            Initializes intern.Resource parent class
        """
        Resource.__init__(self)

    @classmethod
    def get_UUID(self, ID, repos):

        """
            obtains ID and repos and converts the input into a touple
        """
        if ID is '':
            raise ValueError('The UUID was not specified')
        elif repos is '':
            raise ValueError('The repository name was not specified')
        else:
            IDrepos = (ID, repos)
            return IDrepos

    @classmethod
    def get_channel(self, UUID, coll, exp):
        """
            Method to input all channel hierarchy requirememnts, works as a dummy
            for BossRemote Parallelism.

            Args:
                UUID (str) : Root UUID of the repository
                col (str) : Name of collection
                exp (str) : Name of experiment

            Returns:
                chan (str) : String of UUID/col/exp
        """

        chan = UUID + "/" + coll + "/" + exp
        return chan

    @classmethod
    def get_cutout(self, api, chan, res, xspan, yspan, zspan):

        """
            ID MUST BE STRING ""
            xpix = "x" how many pixels traveled in x
            ypix = "y" how many pixels traveled in y
            zpix = "z" how many pixels traveled in z
            xo, yo, zo (x,y,z offsets)
            type = "raw"
            scale = "grayscale"
        """
        #Defining used variables
        chan = chan.split("/")
        UUID = chan[0]
        exp = chan[1]

        xpix = xspan[1]-xspan[0]
        xo = xspan[0]
        ypix = yspan[1]-yspan[0]
        yo = yspan[0]
        zpix = zspan[1]-zspan[0]
        zo = zspan[0]

        size = str(xpix) + "_" + str(ypix) + "_" + str(zpix)
        offset = str(xo) + "_" + str(yo) + "_" + str(zo)

        #User entered IP address with added octet-stream line to obtain data from api in octet-stream form
        #0_1_2 specifies a 3 dimensional octet-stream "xy" "xz" "yz"
        address = api + "/api/node/" + UUID + "/" + exp + "/raw/0_1_2/" + size + "/" + offset + "/octet-stream"
        r = requests.get(address)
        octet_stream = str(r.content)

         #Converts obtained octet-stream into a numpy array of specified type uint8
        block = np.fromstring(octet_stream, dtype = np.uint8)

        #Specifies the 3 dimensional shape of the numpy array of the size given by the user
        volumeOut =  block.reshape(zpix,ypix,xpix)

        #Returns a 3-dimensional numpy array to the user
        return volumeOut

    @classmethod
    def get_cutoutI(self, api, chan, res, xspan, yspan, zspan):

        """
            ID MUST BE STRING ""
            xpix = "x" how many pixels traveled in x
            ypix = "y" how many pixels traveled in y
            zpix = "z" how many pixels traveled in z
            xo, yo, zo (x,y,z offsets)
            type = "raw"
            scale = "grayscale"
        """
        #Defining used variables
        chan = chan.split("/")
        UUID = chan[0]
        exp = chan[2]

        xpix = xspan[1]-xspan[0]
        xo = xspan[0]
        ypix = yspan[1]-yspan[0]
        yo = yspan[0]
        zpix = zspan[1]-zspan[0]
        zo = zspan[0]

        size = str(xpix) + "_" + str(ypix) + "_" + str(xpix)
        offset = str(xo) + "_" + str(yo) + "_" + str(zo)

        #User entered IP address with added octet-stream line to obtain data from api in octet-stream form
        #0_1_2 specifies a 3 dimensional octet-stream "xy" "xz" "yz"
        address = api + "/api/node/" + UUID + "/" + exp + "/raw/0_1_2/256_256_256/" + offset + "/octet-stream"
        r = requests.get(address)
        octet_stream = str(r.content)
        dat = octet_stream.split("///////////////")
        dat = dat[0]
        print len(dat)
        block = np.fromstring(dat, dtype = np.uint8)
        volumeOut =  block.reshape(xpix,ypix,zpix)

        #Returns a 3-dimensional numpy array to the user
        return volumeOut

    @classmethod
    def create_project(self, api, chan):

        """
            Creates a repository for the data to be placed in.
            Returns randomly generated 32 character long UUID
        """

        print "Your Channel/Collection/Experiment space has been created: " + str(chan)
        return chan

    @classmethod
    def create_cutout(self, api, chan, xrang, yrang, zrang, volume):

        """
            Creates an instance which works as a sub-folder where the data is stored
            Must specify:
            dataname(required) = "example1"
            version(required) = "1"
            The size of the space reserved must be a cube with sides of multiples of 32
        """
        x = xrang[1] - xrang[0]
        y = yrang[1] - yrang[0]
        z = zrang[1] - zrang[0]

        chan = chan.split("/")
        UUID_exp = chan[0] + "/" + chan[1]
        chan = chan[2]

        volume = volume.tobytes()
        dif = (x * y * x) - len(volume)
        dataBytes = volume + str("".join((["/"] * dif)))

        res = requests.post(
            api + "/api/node/" + UUID_exp + "/raw/0_1_2/{}_{}_{}/{}_{}_{}".format(
            x,y,x,xrang[0],yrang[0],zrang[1]
            ),
            data = dataBytes
        )
        print "Your data has been uploaded."

    @classmethod
    def ChannelResource(self, api, coll, exp, chan, des, datatype):
        """
		Method to create a channel within specified collection, experiment and of a known datatype

		Args:
			Coll (str) : Alias of the UUID
			exp (str) : Name of the instance of data that will be created
			des (str) : Description of what is saved under the given UUID
			datatype (str) : Type of data that will be uploaded. Deafaults to uint8blk

		Returns:
			chan (str) : composed of UUID, exp and chan for use in create_cutout function
        """

        a = requests.post(api + "/api/repos",
            data = json.dumps({"Alias" : coll,
                "Description" : des}
                )
        )
        cont = ast.literal_eval(a.content)
        UUID = cont["root"]

        dat1 = requests.post(api + "/api/repo/" + UUID + "/instance" ,
            data=json.dumps({"typename" : datatype,
                "dataname" : exp,
                "versioned" : "0"
            }))
        chan = str(UUID) + "/" + str(exp) + "/" + str(chan)
        return chan

    @classmethod
    def delete_project(self, api, UUID):
        """
        Method to delete a project

        Args:
            UUID (str) : hexadecimal character long string characterizing the project

        Returns:
            (str) : Confirmation message
        """

        requests.delete(api + "/api/repo/" + UUID + "?imsure=true")
        return "Your instance has been deleted"
