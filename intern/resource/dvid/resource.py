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
from subprocess import call
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
    def StartLocalDvid(self, repoName, portName, port, imagePath):
        """
            Method to spin up a local version of Dvid

            Args:
                repoName (str) : name of the repository docker container
                portName (str) : name of the port where dvid will be Running
                port (str) : Port where dvid will be Running
                imagePath(str) : name of the path where data is located

            Returns:
                Str : all outputs from the command prompt
        """
        call(["docker", "pull", "flyem/dvid"])
        call(["docker", "run", "-v", imagePath + ":/dataLoad/", "--name", repoName, "-d", "flyem/dvid"])
        print("Running your container...")
        call(["docker", "run", "--volumes-from", repoName, "-p", port + ":" + port, "--name", portName, "-t", "flyem/dvid"])

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
    def get_channel(self, UUID_coll_exp):
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

        return UUID_coll_exp

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
        octet_stream = r.content
        print("Grabbing your cutout...")

         #Converts obtained octet-stream into a numpy array of specified type uint8
        block = np.fromstring(octet_stream, dtype = np.uint8)
        try:
            #Specifies the 3 dimensional shape of the numpy array of the size given by the user
            volumeOut =  block.reshape(zpix,ypix,xpix)
        except ValueError:
            print("There is no data currently loaded on your specified host.")
        #Returns a 3-dimensional numpy array to the user
        return volumeOut

    @classmethod
    def create_project(self, api, coll, des):

        """
            Creates a repository for the data to be placed in.
            Returns randomly generated 32 character long UUID
        """

        r = requests.post(api + "/api/repos",
            data = json.dumps({"Alias" : coll,
                "Description" : des}
                )
        )
        r = str(r.content)
        r = r.split("'")
        r = r[1]
        cont = ast.literal_eval(r)
        UUID = cont["root"]
        return UUID

    @classmethod
    def create_cutout(self, chan, portName, xrang, yrang, zrang, volume):
        """
            Method to upload a cutout of data

            Args:
                chan (str) : Project string which carries UUID, and channel name information
                portName (str) : Name of the docker port from which the local dvid instance is running
                xrang (str) : Start x value within the 3D space
                yrang (str) : Start y value within the 3D space
                zrang (str) : Start z value witinn the 3D space
                volume (str) : Path to the data within the mounted docker file

            Retruns:
                message (str) : Uploading Data... message

        """
        chan = chan.split("/")
        UUID = str(chan[0])
        print("Your data is uploading onto the UUID, please ignore the next timeout message!")
        instanceName = str(chan[1])
        xrang = str(xrang)
        yrang = str(yrang)
        zrang = str(zrang)
        call(["docker", "exec", portName, "dvid", "node", UUID, instanceName, "load", xrang + "," + yrang + "," + zrang, "/dataLoad/" + volume])
        return "Your data is uploading..."

    @classmethod
    def ChannelResource(self, api, UUID, exp, datatype):
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

        dat1 = requests.post(api + "/api/repo/" + UUID + "/instance" ,
            data=json.dumps({"typename" : datatype,
                "dataname" : exp,
                "versioned" : "0"
            }))
        chan = str(UUID) + "/" + str(exp)
        return chan
