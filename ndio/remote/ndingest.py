from __future__ import absolute_import
import json
import os
import requests
from jsonspec.validators import load
import re
import shutil
from .neurodata import neurodata as nd
import ndio.convert.tiff as ndtiff
import ndio.convert.png as ndpng

VERIFY_BY_FOLDER = 'Folder'
VERIFY_BY_SLICE = 'Slice'


class NDIngest:
    """
    A remote to automate the ingest of large volumetric data into ndstore.
    """

    def __init__(self, site_host=None):
        """
        Arguments:
            site_host(str): The site host to post the data to, by default
                http://openconnectome.me.

        Returns:
            None
        """
        self.channels = {}
        self.dataset = []
        self.project = []
        self.metadata = ''
        if site_host is not None:
            self.oo = nd(site_host)
        else:
            self.oo = nd()

        rd = requests.get(
            'https://raw.githubusercontent.com/\
neurodata/ndstore/ae-doc-edits/docs/sphinx/dataset_schema.json')
        if (rd.status_code < 300):
            self.DATASET_SCHEMA = load(eval(str(rd.text)))
        else:
            raise OSError("Dataset schema not available")

        rc = requests.get(
            'https://raw.githubusercontent.com/\
neurodata/ndstore/ae-doc-edits/docs/sphinx/channel_schema.json')
        if (rc.status_code < 300):
            self.CHANNEL_SCHEMA = load(eval(str(rc.text)))
        else:
            raise OSError("Channel schema not available")

        rp = requests.get(
            'https://raw.githubusercontent.com\
/neurodata/ndstore/ae-doc-edits/docs/sphinx/project_schema.json')
        if (rp.status_code < 300):
            self.PROJECT_SCHEMA = load(eval(str(rp.text)))
        else:
            raise OSError("Project schema not available")

    def add_channel(
        self, channel_name, datatype, channel_type, data_url, file_format,
            file_type, exceptions=None, resolution=None,
            windowrange=None, readonly=None):
        """
        Arguments:
            channel_name (str): Channel Name is the specific name of a
                specific series of data. Standard naming convention is to do
                ImageTypeIterationNumber or NameSubProjectName.
            datatype (str): The data type is the storage method of data in
                the channel. It can be uint8, uint16, uint32, uint64, or
                float32.
            channel_type (str): The channel type is the kind of data being
                stored in the channel. It can be image, annotation, or
                timeseries.
            data_url (str): This url points to the root directory of the
                files. Dropbox (or any data requiring authentication to
                download such as private s3) is not an acceptable HTTP
                Server. See additional instructions in documentation online
                to format s3 properly so it is http accessible.
            file_format (str): File format refers to the overarching kind
                of data, as in slices (normal image data) or catmaid
                (tile-based).
            file_type (str): File type refers to the specific type of file
                that the data is stored in, as in, tiff, png, or tif.
            exceptions (int): Exceptions is an option to enable the
                possibility for annotations to contradict each other (assign
                different values to the same point). 1 corresponds to True,
                0 corresponds to False.
            resolution (int): Resolution is the starting resolution of the
                data being uploaded to the channel.
            windowrange (int, int): Window range is the maximum and minimum
                pixel values for a particular image. This is used so that the
                image can be displayed in a readable way for viewing through
                RESTful calls
            readonly (int): This option allows the user to control if,
                after the initial data commit, the channel is read-only.
                Generally this is suggested with data that will be publicly
                viewable.

        Returns:
            None
        """
        self.channels[channel_name] = [
            channel_name.strip().replace(" ", ""), datatype,
            channel_type.lower(), data_url,
            file_format, file_type, exceptions, resolution,
            windowrange, readonly
        ]

    def add_project(self, project_name, token_name=None, public=None):
        """
        Arguments:
            project_name (str): Project name is the specific project within
                a dataset's name. If there is only one project associated
                with a dataset then standard convention is to name the
                project the same as its associated dataset.
            token_name (str): The token name is the default token. If you
                do not wish to specify one, a default one will be created for
                you with the same name as the project name. However, if the
                project is private you must specify a token.
            public (int): This option allows users to specify if they want
                the project/channels to be publicly viewable/search-able.
                (1, 0) = (TRUE, FALSE)

        Returns:
            None
        """
        self.project = (project_name.strip().replace(" ", ""),
                        token_name.strip().replace(" ", ""), public)

    def add_dataset(self, dataset_name, imagesize, voxelres, offset=None,
                    timerange=None, scalinglevels=None, scaling=None):
        """
        Add a new dataset to the ingest.

        Arguments:
            dataset_name (str): Dataset Name is the overarching name of the
                research effort. Standard naming convention is to do
                LabNamePublicationYear or LeadResearcherCurrentYear.
            imagesize (int, int, int): Image size is the pixel count
                dimensions of the data. For example is the data is stored
                as a series of 100 slices each 2100x2000 pixel TIFF images,
                the X,Y,Z dimensions are (2100, 2000, 100).
            voxelres (float, float, float): Voxel Resolution is the number
                of voxels per unit pixel. We store X,Y,Z voxel resolution
                separately.
            offset (int, int, int): If your data is not well aligned and
                there is "excess" image data you do not wish to examine, but
                are present in your images, offset is how you specify where
                your actual image starts. Offset is provided a pixel
                coordinate offset from origin which specifies the "actual"
                origin of the image. The offset is for X,Y,Z dimensions.
            timerange (int, int): Time Range is a parameter to support
                storage of Time Series data, so the value of the tuple is a
                0 to X range of how many images over time were taken. It
                takes 2 inputs timeStepStart and timeStepStop.
            scalinglevels (int): Scaling levels is the number of levels the
                data is scalable to (how many zoom levels are present in the
                data). The highest resolution of the data is at scaling level
                0, and for each level up the data is down sampled by 2x2
                (per slice). To learn more about the sampling service used,
                visit the the propagation service page.
            scaling (int): Scaling is the orientation of the data being
                stored, 0 corresponds to a Z-slice orientation (as in a
                collection of tiff images in which each tiff is a slice on
                the z plane) and 1 corresponds to an isotropic orientation
                (in which each tiff is a slice on the y plane).

        Returns:
            None
        """
        self.dataset = (dataset_name.strip().replace(" ", ""), imagesize,
                        voxelres, offset, timerange, scalinglevels, scaling)

    def add_metadata(self, metadata=""):
        """
        Arguments:
            metadata(str): Any metadata as appropriate from the LIMS schema

        Returns:
            None
        """
        self.metadata = metadata

    def nd_json(self, dataset, project, channel_list, metadata):
        """
        Genarate ND json object.
        """
        nd_dict = {}
        nd_dict['dataset'] = self.dataset_dict(*dataset)
        nd_dict['project'] = self.project_dict(*project)
        nd_dict['metadata'] = metadata
        nd_dict['channels'] = {}
        for channel_name, value in channel_list.items():
            nd_dict['channels'][channel_name] = self.channel_dict(*value)

        return json.dumps(nd_dict, sort_keys=True, indent=4)

    def nd_json_list(self, dataset, project, channel_list, metadata):
        """
        Genarate ND json object.
        """
        nd_dict = {}
        nd_dict['dataset'] = self.dataset_dict(*dataset)
        nd_dict['project'] = self.project_dict(*project)
        nd_dict['metadata'] = metadata
        nd_dict['channels'] = {}
        for channel_name, value in channel_list.items():
            nd_dict['channels'].append(self.channel_dict(*value))

        return json.dumps(nd_dict, sort_keys=True, indent=4)

    def dataset_dict(
        self, dataset_name, imagesize, voxelres,
            offset, timerange, scalinglevels, scaling):
        """Generate the dataset dictionary"""
        dataset_dict = {}
        dataset_dict['dataset_name'] = dataset_name
        dataset_dict['imagesize'] = imagesize
        dataset_dict['voxelres'] = voxelres
        if offset is not None:
            dataset_dict['offset'] = offset
        if timerange is not None:
            dataset_dict['timerange'] = timerange
        if scalinglevels is not None:
            dataset_dict['scalinglevels'] = scalinglevels
        if scaling is not None:
            dataset_dict['scaling'] = scaling
        return dataset_dict

    def channel_dict(self, channel_name, datatype, channel_type, data_url,
                     file_format, file_type, exceptions, resolution,
                     windowrange, readonly):
        """
        Generate the project dictionary.
        """
        channel_dict = {}
        channel_dict['channel_name'] = channel_name
        channel_dict['datatype'] = datatype
        channel_dict['channel_type'] = channel_type
        if exceptions is not None:
            channel_dict['exceptions'] = exceptions
        if resolution is not None:
            channel_dict['resolution'] = resolution
        if windowrange is not None:
            channel_dict['windowrange'] = windowrange
        if readonly is not None:
            channel_dict['readonly'] = readonly
        channel_dict['data_url'] = data_url
        channel_dict['file_format'] = file_format
        channel_dict['file_type'] = file_type
        return channel_dict

    def project_dict(self, project_name, token_name, public):
        """
        Genarate the project dictionary.
        """
        project_dict = {}
        project_dict['project_name'] = project_name
        if token_name is not None:
            if token_name == '':
                project_dict['token_name'] = project_name
            else:
                project_dict['token_name'] = token_name
        else:
            project_dict['token_name'] = project_name

        if public is not None:
            project_dict['public'] = public
        return project_dict

    def identify_imagesize(self, image_type, image_path='/tmp/img.'):
        """
        Identify the image size using the data location and other parameters
        """
        dims = ()
        try:
            if (image_type.lower() == 'png'):
                dims = ndpng.import_png('{}{}'.format(image_path, image_type))
            elif (image_type.lower() == 'tif' or image_type.lower() == 'tiff'):
                dims = ndtiff.import_tiff('{}{}'.format(
                    image_path, image_type
                ))
            else:
                raise ValueError("Unsupported image type.")
        except:
            raise OSError('The file was not accessible at {}{}'.format(
                image_path,
                image_type
            ))
        return dims

    def verify_path(self, data, verifytype):
        """
        Verify the path supplied.
        """
        # Insert try and catch blocks
        try:
            token_name = data["project"]["token_name"]
        except:
            token_name = data["project"]["project_name"]
        # Check if token exists
        URLPath = self.oo.url("{}/info/".format(token_name))

        # UA TODO determine if the return will be in json for token DNE
        try:
            response = requests.get(URLPath)
        except:
            raise OSError("Error code contacting {} with code {}".format(
                URLPath, response.status_code
            ))

        if (str(response.content.decode("utf-8")) !=
                "Token {} does not exist".format(token_name)):
            online_data = response.content
            try:
                assert(online_data['dataset']['name'] ==
                       data['dataset']['dataset_name'])
                assert(online_data['dataset']['imagesize'] ==
                       data['dataset']['imagesize'])
                assert(online_data['dataset']['offset'] ==
                       data['dataset']['offset'])
                assert(online_data['project']['name'] ==
                       data['project']['project_name'])
            except:
                raise ValueError("Project and Dataset information Inconistent")

        channel_names = list(data["channels"].copy().keys())
        imgsz = data['dataset']['imagesize']

        for i in range(0, len(channel_names)):
            channel_type = data["channels"][
                channel_names[i]]["channel_type"]
            path = data["channels"][channel_names[i]]["data_url"]
            aws_pattern = re.compile("^(http:\/\/)(.+)(\.s3\.amazonaws\.com)")
            file_type = data["channels"][channel_names[i]]["file_type"]
            if "scaling" in data["dataset"]:
                if (data["dataset"]["scaling"]) == 0:
                    if "offset" in data["dataset"]:
                        offset = data["dataset"]["offset"][0]
                    else:
                        offset = 0
                else:
                    if "offset" in data["dataset"]:
                        offset = data["dataset"]["offset"][2]
                    else:
                        offset = 0
            else:
                if "offset" in data["dataset"]:
                    offset = data["dataset"]["offset"][0]
                else:
                    offset = 0

            if (aws_pattern.match(path)):
                verifytype = VERIFY_BY_SLICE

            if (channel_type == "timeseries"):
                timerange = data["dataset"]["timerange"]
                for j in xrange(timerange[0], timerange[1] + 1):
                    # Test for tifs or such? Currently test for just not
                    # empty
                    if (verifytype == VERIFY_BY_FOLDER):
                        work_path = "{}/{}/{}/time{}/".format(
                            path, token_name, channel_names[i], j)
                    elif (verifytype == VERIFY_BY_SLICE):
                        work_path = "{}/{}/{}/time{}/{}.{}".format(
                            path, token_name, channel_names[i], j,
                            ("%04d" % offset), file_type)
                    else:
                        raise TypeError('Incorrect verify method')
                    # Check for accessibility
                    try:
                        if (verifytype == VERIFY_BY_FOLDER):
                            resp = requests.head(work_path)
                            assert(resp.status_code == 200)
                        elif (verifytype == VERIFY_BY_SLICE):
                            resp = requests.get(work_path, stream=True)
                            with open('/tmp/img.{}'.format(file_type),
                                      'wb') as out_file:
                                shutil.copyfileobj(resp.raw, out_file)
                            out_file.close()
                            assert(resp.status_code == 200)
                            resp.close()
                    except AssertionError:
                        raise OSError('Files are not http accessible: \
                            Error: {}'.format(resp.status_code))
                    # Attempt to Verify imagesize here

                    try:
                        if (verifytype == VERIFY_BY_SLICE):
                            assert(list(self.identify_imagesize(file_type)) ==
                                   imgsz)
                    except:
                        raise ValueError('File image size does not match\
provided image size.')

            else:
                # Test for tifs or such? Currently test for just not empty
                if (verifytype == VERIFY_BY_FOLDER):
                    work_path = "{}/{}/{}/".format(
                        path, token_name, channel_names[i])
                elif (verifytype == VERIFY_BY_SLICE):
                    work_path = "{}/{}/{}/{}.{}".format(
                        path, token_name, channel_names[i],
                        ("%04d" % offset), file_type)
                else:
                    raise TypeError('Incorrect verify method')
                # Check for accessibility
                if (verifytype == VERIFY_BY_FOLDER):
                    resp = requests.head(work_path)
                elif (verifytype == VERIFY_BY_SLICE):
                    resp = requests.get(work_path, stream=True)
                    with open('/tmp/img.{}'.format(file_type),
                              'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                    out_file.close()
                    resp.close()
                if (resp.status_code >= 300):
                    raise OSError('Files are not http accessible: \
URL: {}'.format(work_path))
                # Attempt to Verify imagesize here

                try:
                    if (verifytype == VERIFY_BY_SLICE):
                        assert(list(self.identify_imagesize(file_type)) ==
                               imgsz)
                except:
                    raise ValueError('File image size does not match\
provided image size.')

            # By Here the path should have been verified

    def verify_json(self, data):
        """
        Verify the JSON against the spec.
        """
        names = []
        # Channels
        channel_names = list(data["channels"].copy().keys())
        for i in range(0, len(channel_names)):
            channel_object = data["channels"][channel_names[i]]
            try:
                self.CHANNEL_SCHEMA.validate(channel_object)
            except:
                raise ValueError("channel " + channel_object["channel_name"])
            names.append(channel_object["channel_name"])
        # Dataset"
        dataset_object = data["dataset"]
        try:
            self.DATASET_SCHEMA.validate(dataset_object)
        except:
            raise ValueError("Error in dataset parameters")
        names.append(dataset_object["dataset_name"])

        # Project
        project_object = data["project"]
        try:
            self.PROJECT_SCHEMA.validate(project_object)
        except:
            raise ValueError("Error in project parameters")
        names.append(project_object["project_name"])

        # Check if names contain bad chars. Underscore is allowed
        spec_chars = re.compile(".*[$&+,:;=?@#|'<>.^*()%!-].*")

        for i in names:
            if(spec_chars.match(i)):
                raise ValueError("Error. No special characters allowed \
including: $&+,:;=?@#|'<>.^*()%!-].* in dataset, project, channel or token \
names")

    def put_data(self, data):
        """
        Try to post data to the server.
        """
        URLPath = self.oo.url("autoIngest")
        try:
            response = requests.post(URLPath, data=json.dumps(data))
            assert(response.status_code == 200)
            print("From ndio: {}".format(response.content))
        except:
            raise OSError("Error in posting JSON file {}\
".format(reponse.status_code))

    def post_data(self,
                  file_name=None, legacy=False,
                  verifytype=VERIFY_BY_SLICE):
        """
        Arguments:
            file_name (str): The file name of the json file to post (optional).
                If this is left unspecified it is assumed the data is in the
                AutoIngest object.
            dev (bool): If pushing to a microns dev branch server set this
                to True, if not leave False.
            verifytype (enum): Set http verification type, by checking the
                first slice is accessible or by checking channel folder.
                NOTE: If verification occurs by folder there is NO image size
                or type verification. Enum: [Folder, Slice]

        Returns:
            None
        """
        if (file_name is None):
            complete_example = (
                self.dataset, self.project, self.channels, self.metadata)
            data = json.loads(self.nd_json(*complete_example))

        else:
            try:
                with open(file_name) as data_file:
                    data = json.load(data_file)
            except:
                raise OSError("Error opening file")

        self.verify_path(data, verifytype)
        self.verify_json(data)
        self.put_data(data)

    def output_json(self, file_name='/tmp/ND.json'):
        """
        Arguments:
            file_name(str : '/tmp/ND.json'): The file name to store the json to

        Returns:
            None
        """
        complete_example = (
            self.dataset, self.project, self.channels, self.metadata)
        data = json.loads(self.nd_json(*complete_example))

        self.verify_json(data)
        self.verify_path(data, VERIFY_BY_SLICE)

        f = open(file_name, 'w')
        f.write(str(data))
        f.close()
