from enums import *
from exceptions import *

class RAMONBase(object):
    """
    RAMONBase Object for storing neuroscience data
    """
    def __init__(self,  id = DEFAULT_ID,
                        confidence = DEFAULT_CONFIDENCE,
                        dynamic_metadata = DEFAULT_DYNAMIC_METADATA,
                        status = DEFAULT_STATUS,
                        author = DEFAULT_AUTHOR):
        """
        Initialize a new RAMONBase object with default attributes.

        Arguments:
            :id:                `int` Unique 32bit ID value assigned by OCP database
            :confidence:        `float` Value 0-1 indicating confidence in annotation
            :dynamic_metadata:  `dict` A flexible, unspecified collection key-value pairs
            :status:            `string` Status of annotation in database
            :author:            `string` Username of the person who created the annotation
        """
        self._id = id
        self.confidence = confidence
        self.dynamic_metadata = dynamic_metadata
        self._status = status
        self.author = author


    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value):
        if type(value) is not int or value <= 0:
            raise InvalidIDException("Invalid ID {0}".format(value))
        self._id = value
        return value


    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        try:
            r = eRAMONAnnoStatus.reverse_mapping[value]
        except:
            raise InvalidEnumerationException()
            return False
        self._status = value
