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
import numpy as np
import h5py


class LocalResource(Resource):

    """Base class for LocalFile resources.

    Attributes:
        name (string): Name of resource.  Used as identifier when talking to
        the LocalFile database.
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
    def create_LocalFile(self,filePath,fileName):

        """
            Method to create a local HDF5 datastore. This method is not necessary as the remote
            initiation immidiately created a local stroe with a given name if it does not exist,
            however this may be used if that presents problems.

            Args:
                filePath (string) : directory path to where the datastore is made
                filename (string) : name of the new local datastore
        """

        form = ".hdf5"
        dirP = str(filePath) + str(fileName) + str(form)
        f = h5py.File(dirP, 'w')
        return f

    @classmethod
    def create_collection(self,datastore, groupName):

        """
			Method to create a group space within local HDF5 datastore

			Args:
				groupName (string) : Desired name of the group which will be categorized 'collection'

			Raises:
				(KeyError): if given invalid version.
        """

        grp = datastore.create_group(groupName)
        return (grp)

    @classmethod
    def create_channel(self, groupName, subGroup):

        """
			Method to create a sub-group space within local HDF5 datastore

			Args:
				groupName (string) : name of the group (collection) this sub-group (channel) will be created in
				subGroup (string) : Desired name of the sub-group which will be categorized as the channel

			Raises:
				(KeyError): if given invalid version.
        """

        subgrp = groupName.create_group(subGroup)
        return (subgrp)

    @classmethod
    def create_cutout(self, subgrp, ArrayName, dataArray):

        """
			Method to create a dataset within local HDF5 datastore

			Args:
				subGroup (string) : name of the channel (sub-group) in which the data will be saved
				arrayName (string) : name of the data
				dataArray (array) : N-Dimensional array which is to be saved

			Raises:
				(KeyError): if given invalid version.
        """
        dset = subgrp.create_dataset(ArrayName, data = dataArray, compression = 'gzip')
        return(dset)

    @classmethod
    def create_project(self, datastore ,chan_setup):
        """
            Creates the space in which data will be stored

            Args:
                chan_setup (string) : desired path to new or existing dataset

            Returns:
                subGrp (HDF5) : group to which the new dataset will be added

            Raises:
                The program tries to create the groups, if they already exist then
                it simply opens them.
        """
        chan_setup = chan_setup.split('/')
        chan,col = chan_setup[0],chan_setup[1]
        try:
            grp = datastore.create_group(chan)
        except:
            grp = datastore[chan]
        try:
            subGrp = grp.create_group(col)
        except:
            subGrp = grp[col]
        return subGrp

    @classmethod
    def get_channel(self,channel,collection,experiment=''):

        """
			Method to reques specific collection/channel/experiment where the data is located

			Args:
				collection (string) : name of collection
				channel (string) : name of channel
				experiment (string) : name of experiement (actual dataset)

			Returns:
				channelSource (string) : amalgamation of all three parameters into a single path string

			Raises:
				(KeyError): if given invalid version
        """

        channelSource = str(channel + '/' + collection + '/' + experiment)
        return channelSource

    @classmethod
    def get_cutout(self, datastore, channelRes, res, xspan, yspan, zspan):

        """
			Method to request a volume of data from local server

			Args:
				channelRes (string) : hiererchal path of where the data is located
				res (int) : data resolution
				xspan (int) : range of pixels in x axis ([1000:1500])
				yspan (int) : range of pixels in y axis ([1000:1500])
				zspan (int) : range of pixels in z axis ([1000:1010])

			Returns:
				array: numpy array representation of the requested volume

			Raises:
				(KeyError): if given invalid version.
        """

        #Defining used variables
        xpix = xspan[1]-xspan[0]
        xo = xspan[0]

        ypix = yspan[1]-yspan[0]
        yo = yspan[0]

        zpix = zspan[1]-zspan[0]
        zo = zspan[0]

        dataLoc = datastore[channelRes]
        vol = dataLoc[zo:zpix,yo:ypix,xo:xpix]
        return vol

    @classmethod
    def retrieve(self, datastore, path):

        """
			Method to retrieve a specific file. Aimed at developer for quick file access

			Args:
				path (string): desired path to the HDF5 group created

			Raises:
				(KeyError): if given invalid version.
        """

        retrF = datastore[path]
        return retrF

    @classmethod
    def list(self, userFind):

        """
			Method to retrieve a tree of hirerchy within datastore.

			Returns:
				printname (string) : list of all possible collections, channels and experiments
									 created in the current datastore

			Raises:
				(KeyError): if given invalid version.
        """

        def printname(name):
            print name
        return userFind.visit(printname)
